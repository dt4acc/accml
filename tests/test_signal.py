import asyncio

from ophyd_async.tango.core import tango_signal_rw, tango_signal_r


async def main():
    # Read/Write setpoint signal
    set_sig = tango_signal_rw(float,
                              "SimpleTangoServer/test/power_converter_Q3P2T6R/current_setpoint",  # read path
                              "SimpleTangoServer/test/power_converter_Q3P2T6R/current_setpoint",  # write path
                              )

    # Read-only readback signal
    rdbk_sig = tango_signal_r(float,
                              "SimpleTangoServer/test/power_converter_Q3P2T6R/current_readback"
                              )

    await set_sig.connect()
    await rdbk_sig.connect()

    before = await rdbk_sig.get_value()
    print(f"Readback before: {before}")

    await set_sig.set(138.53)

    after = await rdbk_sig.get_value()
    print(f"Readback after:  {after}")


asyncio.run(main())
