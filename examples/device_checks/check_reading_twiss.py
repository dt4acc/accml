import asyncio
import pprint
from typing import Annotated as A, Sequence, Dict

import numpy as np
import tango
import ophyd_async

from ophyd_async.core import (SignalR, StandardReadable, StandardReadableFormat as Format, Array1D)
from ophyd_async.tango.core import TangoDevice, TangoPolling
from ophyd_async.core import StandardReadable

print(f"{tango.__version__=}")
print(f"{ophyd_async.__version__=}")


class Orbit(StandardReadable, TangoDevice):
    orbit_x : A[ SignalR[ Array1D[np.float64] ] , Format.HINTED_UNCACHED_SIGNAL, TangoPolling(1.0, 0.01, 1e-4) ]
    orbit_y : A[ SignalR[ Array1D[np.float64] ] , Format.HINTED_UNCACHED_SIGNAL, TangoPolling(1.0, 0.01, 1e-4) ]
    pass

class Twiss(StandardReadable, TangoDevice):
    # fmt:off
    alpha_x : A[ SignalR[ Array1D[np.float64] ] , Format.HINTED_UNCACHED_SIGNAL, TangoPolling(1.0, 0.01, 1e-4) ]
    alpha_y : A[ SignalR[ Array1D[np.float64] ] , Format.HINTED_UNCACHED_SIGNAL, TangoPolling(1.0, 0.01, 1e-4) ]
    beta_x : A[ SignalR[ Array1D[np.float64] ] , Format.HINTED_UNCACHED_SIGNAL, TangoPolling(1.0, 0.01, 1e-4) ]
    beta_y : A[ SignalR[ Array1D[np.float64] ] , Format.HINTED_UNCACHED_SIGNAL, TangoPolling(1.0, 0.01, 1e-4) ]
    nu_x   : A[ SignalR[ Array1D[np.float64] ] , Format.HINTED_UNCACHED_SIGNAL, TangoPolling(1.0, 0.01, 1e-4) ]
    nu_y   : A[ SignalR[ Array1D[np.float64] ] , Format.HINTED_UNCACHED_SIGNAL, TangoPolling(1.0, 0.01, 1e-4) ]
    # fmt:off


def extract_tune(data: Dict[str, Dict[str, Sequence[float]]]):
    return data["tunes-nu_x"]["value"][-1], data["tunes-nu_y"]["value"][-1]


async def run_device():
    trl = "PHYSICS/SOLEIL/TWISS_ORBIT"
    twiss = Twiss(name="tunes", trl=trl)

    trl = "PHYSICS/SOLEIL/TWISS_ORBIT"
    orbit = Orbit(name="tunes", trl=trl)
    print("Staging device")
    await orbit.stage()
    await twiss.stage()
    print("Connecting device")
    await orbit.connect()
    await twiss.connect()
    print("Reading")
    orb_r = await orbit.read()
    print(f"tune: {extract_tune(await twiss.read())}")
    print(f"tune: {extract_tune(await twiss.read())}")
    await orbit.unstage()
    await twiss.unstage()



if __name__ == "__main__":
    asyncio.run(run_device())
