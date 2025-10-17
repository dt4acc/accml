import asyncio
from accml.custom.tango.mexec.power_converter import PowerConverter


async def main():
    pc = PowerConverter(
        "SimpleTangoServer/test/power_converter_Q3P2T6R",
        setpoint_suffix="current_setpoint",
        readback_suffix="current_readback",
        name="Q3P2T6R",
    )
    await pc.connect(timeout=2.0)

    print("rdbk before:", await pc.readback.get_value())
    await pc.setpoint.set(133.9)
    print("rdbk after :", await pc.readback.get_value())


asyncio.run(main())
