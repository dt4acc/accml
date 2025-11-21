import asyncio
import pprint
from typing import Annotated as A

from ophyd_async.tango.core import TangoReadable, TangoPolling
from ophyd_async.core import (
    SignalR,
    SignalRW,
    StandardReadableFormat as Format,
)


class PowerConverter(TangoReadable):
    """

    Try current without TangoPolling
    Does the device support automatic update?

    """
    # fmt: off
    current: A[SignalRW[float], Format.HINTED_UNCACHED_SIGNAL, TangoPolling(0.2, 1e-3, 1e-4)]
    # fmt: on


async def main():
    pc = PowerConverter(name="pc", trl="ring/pcs/t_very_pc")
    pprint.pprint(await pc.describe())
    await pc.connect(timeout=3.0)
    # should be instantanious
    pprint.pprint(await pc.current.read())
    pprint.pprint(await pc.read())
    # Is that in range
    current = 0.0
    r  = await pc.current.set(current)

    r  = await pc.current(current)

    print(r)



if __name__ == "__main__":
    asyncio.run(main())


