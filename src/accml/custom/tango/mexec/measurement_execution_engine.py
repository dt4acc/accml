from __future__ import annotations

import asyncio
import os
from dataclasses import asdict
from typing import Dict, List, Sequence, Any

from ophyd_async.core import Device, Signal

from accml.core.bl.liasion_translator_setup import load_managers
from accml.core.interfaces.measurement_execution_engine import MeasurementExecutionEngine
from accml.core.model.command import Command
# Your existing types
from ..mexec.master_clock import MasterClock
from ..mexec.multiplexer_for_settable_devices import MultiplexerProxy
from ..mexec.power_converter import PowerConverter
from ..mexec.tunes import Tunes


class AsyncMeasurementExecutionEngine(MeasurementExecutionEngine):
    """
    Bluesky-free async engine.

    Key behavior:
      - Executes commands sequentially (no sleeps between commands).
      - Supports 'delta_' properties client-side by doing read-modify-write
        against the device setpoint (e.g., 'delta_set_current').
      - Prints results; returns a list of dicts (index, command, error/reading).
    """

    def __init__(self, run_engine=None) -> None:
        # kept arg for compatibility with your caller; not used
        self.run_engine = run_engine

    # ---- helpers ---------------------------------------------------------

    @staticmethod
    async def _get_value(sig_or_dev: Any) -> Any:
        """
        Try to fetch a scalar value from an ophyd-async Signal-like.
        Works for Signals with get_value() or .read() returning {'value': ...}.
        """
        # direct signal
        if hasattr(sig_or_dev, "get_value") and callable(sig_or_dev.get_value):
            return await sig_or_dev.get_value()

        if hasattr(sig_or_dev, "read") and callable(sig_or_dev.read):
            r = await sig_or_dev.read()
            # common pattern: {'value': <x>, 'timestamp': <t>, ...}
            if isinstance(r, dict) and "value" in r:
                return r["value"]
            return r  # fallback: unknown structure
        return sig_or_dev  # already a scalar

    @staticmethod
    async def _set_value(sig: Signal, value: Any) -> None:
        """
        Set value on an ophyd-async Signal-like (await the status if returned).
        """
        if hasattr(sig, "set") and callable(sig.set):
            st = sig.set(value)
            # st could be an awaitable or a status-like with .wait()
            if asyncio.iscoroutine(st):
                await st
            elif hasattr(st, "wait") and callable(st.wait):
                await asyncio.get_event_loop().run_in_executor(None, st.wait)
            return
        # last resort: raise, as we expected a settable Signal
        raise RuntimeError("Signal is not settable")

    async def _apply_delta(self, pc: PowerConverter, delta_value: float) -> float:
        """
        Implement client-side delta: new_setpoint = current_setpoint + delta.
        Writes to pc.setpoint and returns the new_setpoint.
        """
        # prefer readback if available/stable; else current setpoint
        base = None
        if hasattr(pc, "readback"):
            try:
                base = await self._get_value(pc.readback)
            except Exception:
                base = None

        if base is None and hasattr(pc, "setpoint"):
            base = await self._get_value(pc.setpoint)

        if base is None:
            raise RuntimeError("Cannot read current value for delta operation")

        new_sp = float(base) + float(delta_value)
        if not hasattr(pc, "setpoint"):
            raise RuntimeError("Power converter has no 'setpoint' Signal")
        await self._set_value(pc.setpoint, new_sp)
        return new_sp

    async def _set_property(self, dev: Device, prop: str, value: Any) -> Any:
        """
        Generic property setter:
          - If prop starts with 'delta_', perform client-side read-modify-write
            against <prop name without 'delta_'>, mapping common names.
          - Else, try to find attribute on the device and set it directly.
        """
        # handle common aliasing for power converters
        #   'delta_set_current' -> operate on 'setpoint' Signal
        #   'delta_<anything>'  -> try to map to attribute without 'delta_'
        if prop.startswith("delta_"):
            # Known PC alias used in your scripts
            if prop == "delta_set_current":
                if not hasattr(dev, "setpoint"):
                    raise RuntimeError("Device has no 'setpoint' for delta_set_current")
                if not isinstance(dev, PowerConverter):
                    # allow generic device with 'setpoint' too
                    return await self._apply_delta(dev, float(value))
                return await self._apply_delta(dev, float(value))
            else:
                # best-effort generic delta_<x>: try device.<x>
                base_name = prop[len("delta_"):]
                if not hasattr(dev, base_name):
                    raise RuntimeError(f"Device has no attribute '{base_name}' for {prop}")
                sig = getattr(dev, base_name)
                # read, add, write
                base = await self._get_value(sig)
                new_val = float(base) + float(value)
                await self._set_value(sig, new_val)
                return new_val

        # non-delta: set directly on the named attribute
        if not hasattr(dev, prop):
            raise RuntimeError(f"Device has no attribute '{prop}'")
        sig = getattr(dev, prop)
        # if it looks like a Signal, set it
        if isinstance(sig, Signal) or hasattr(sig, "set"):
            await self._set_value(sig, value)
            return await self._get_value(sig)
        # else, if simple attribute, just assign (rare)
        try:
            setattr(dev, prop, value)
            return getattr(dev, prop)
        except Exception as ex:
            raise RuntimeError(f"Cannot set property '{prop}': {ex}") from ex

    async def _read_detectors(self, detectors: Sequence[Device]) -> Dict[str, Any]:
        """
        Read a small summary from detectors (e.g. Tunes).
        For Tunes, tries .x and .y. For others, calls .read() if available.
        """
        out: Dict[str, Any] = {}
        for d in detectors:
            name = getattr(d, "name", d.__class__.__name__)
            # Tunes friendly read
            if hasattr(d, "x") and hasattr(d, "y"):
                try:
                    x = await self._get_value(d.x)
                    y = await self._get_value(d.y)
                    out[name] = {"x": x, "y": y}
                    continue
                except Exception:
                    pass
            # Generic read
            if hasattr(d, "read") and callable(d.read):
                try:
                    out[name] = await d.read()
                except Exception as ex:
                    out[name] = {"error": f"read failed: {ex}"}
            else:
                out[name] = {"info": "not readable"}
        return out

    # ---- public API ------------------------------------------------------

    async def execute(
            self,
            commands_collection: Sequence[Sequence[Command]],
            detectors: Sequence[Device],
            actuators: Dict[str, Device],
            info_signals: Dict[str, Signal],
            md: Dict[str, object],
    ) -> List[Dict[str, Any]]:
        """
        Execute all commands sequentially, print progress, and return results.

        Returns:
            List of dicts:
              { "index": int, "command": {cmd-as-dict}, "result" | "error": ... }
        """
        # flatten commands (your caller seems to pass a flat list already)
        commands: List[Command] = []
        for seq in commands_collection:
            if isinstance(seq, Command):
                commands.append(seq)
            else:
                commands.extend(list(seq))

        print(f"[AsyncEngine] Executing {len(commands)} commands...\n")
        results: List[Dict[str, Any]] = []

        for i, cmd in enumerate(commands, start=1):
            print(f"[{i}/{len(commands)}] → Executing {cmd!r}")
            rec = {"index": i, "command": asdict(cmd)}
            try:
                dev = actuators[cmd.id]  # PowerConverter (via MultiplexerProxy)
                # set selection info (print-only for now)
                if info_signals:
                    try:
                        dn = info_signals.get("device_name")
                        cn = info_signals.get("channel_name")
                        cv = info_signals.get("channel_value")
                        if dn is not None:
                            await self._set_value(dn, str(cmd.id))
                        if cn is not None:
                            await self._set_value(cn, str(cmd.property))
                        if cv is not None:
                            await self._set_value(cv, cmd.value)
                    except Exception:
                        # info signals are best-effort for now
                        pass

                # Apply property (supports delta_* client-side)
                new_val = await self._set_property(dev, cmd.property, cmd.value)

                # Immediately read detectors (no sleep)
                det_readings = await self._read_detectors(detectors)

                rec["result"] = {
                    "applied_value": new_val,
                    "detectors": det_readings,
                }
                print("✓ Done")
            except Exception as ex:
                rec["error"] = str(ex)
                print(f"✗ Error during command {i}: {ex}")

            results.append(rec)
            # move immediately to next command

        print(f"\n[AsyncEngine] Finished {len(commands)} commands.")
        return results

    def setup(self, *args) -> dict:
        """

        Todo:
            Setup should be done outside the engine, but provided here for convenience in this draft version

        :param args:
        :return:
        """
        yp, _, __ = load_managers()

        # Tango config from ENV
        pc_prefix = os.environ.get("TANGO_PC_PREFIX", "SimpleTangoServer/test/power_converter_")
        pc_attr_set = os.environ.get("TANGO_PC_ATTR_SET", "current_setpoint")
        pc_attr_rdbk = os.environ.get("TANGO_PC_ATTR_RDBK", "current_readback")

        tunes_device = os.environ.get("TANGO_TUNES_DEVICE", "SimpleTangoServer/test/tune_device")
        tunes_attr_x = os.environ.get("TANGO_TUNES_ATTR_X", "TUNECC/x")
        tunes_attr_y = os.environ.get("TANGO_TUNES_ATTR_Y", "TUNECC/y")

        mc_device = os.environ.get("TANGO_MC_DEVICE", "SimpleTangoServer/test/master_clock_device")
        mc_attr_set = os.environ.get("TANGO_MC_ATTR_SET", "frequency_setpoint")
        mc_attr_rdbk = os.environ.get("TANGO_MC_ATTR_RDBK", "frequency_readback")

        # Quadrupoles
        quad_pcs = {
            name: PowerConverter(
                f"{pc_prefix}{name}",
                name=name,
                setpoint_suffix=pc_attr_set,
                readback_suffix=pc_attr_rdbk,
            )
            for name in yp.get("quadrupole_pcs")
        }
        quadrupoles = MultiplexerProxy(
            name="quad_col", settable_devices=quad_pcs, default_name=list(quad_pcs)[0]
        )

        master_clock = MasterClock(
            mc_device,
            name="mc",
            set_attr=mc_attr_set,
            rdbk_attr=mc_attr_rdbk,
        )

        tunes = Tunes(
            tunes_device,
            name="tune_device",
            attr_x=tunes_attr_x,
            attr_y=tunes_attr_y,
        )

        return dict(master_clock=master_clock, quadrupole_pcs=quadrupoles, tunes=tunes)
