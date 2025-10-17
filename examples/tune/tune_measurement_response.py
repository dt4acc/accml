import asyncio

from ophyd import Signal

from accml.app.tune.tune_measurement import tune
from accml.core.bl.liasion_translator_setup import load_managers
from accml.core.model.identifiers import LatticeElementPropertyID
from accml.custom.tango.mexec.measurement_execution_engine import AsyncMeasurementExecutionEngine


async def main():
    # Setup informational signals (mock metadata)
    info_sigs = {name: Signal(name=name) for name in ["device_name", "channel_name", "channel_value"]}

    yp, lm, _ = load_managers()

    tune_correction_quads = [name for name in yp.tune_correction_quadrupole_names() if name[1] in ["3", "4"]]

    pc_names = {
        lm.forward(LatticeElementPropertyID(name, "main_strength")).device_name:
            name for name in tune_correction_quads
    }
    pc_names = list(set(pc_names))

    results = await tune(
        quadrupole_pc_names=pc_names,
        measurement_values=[0, 1e0, 0, -1e0, 0],
        mexec=AsyncMeasurementExecutionEngine(),
        info_signals=info_sigs
    )

    print("\nMeasurement Results:")
    for r in results:
        print(r)


if __name__ == "__main__":
    asyncio.run(main())
