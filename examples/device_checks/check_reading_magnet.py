import asyncio
import time

from accml.custom.tango.devices.magnet import Magnet


def compute_delay(n_sample: int = 10, delay: float= 0.5):
    start = time.time()
    for i in range(n_sample):
        ref = i * delay
        now = time.time() - start
        diff = ref - now
        # print(f"{i=:2d} {ref=:.3f} {now=:.3f} {diff=:.3f}")
        yield diff


async def run_device():
    trl = "AN01-AR/EM/CQLN.03"
    pc = Magnet(
        name="mag",
        trl=trl,
        # setpoint_name="current_setpoint",
        # readback_name="current_readback",
    )
    await pc.connect()
    await pc.stage()
    d = await pc.describe()
    r = await pc.read()

    start = time.time()
    for delay in compute_delay():
        if delay > 0.0:
            print(f"sleeping for {delay:.3f}")
            await asyncio.sleep(delay)
        r = await pc.read()
        now = time.time()
        dt = now - start
        stamp = r["mag-magnetic_strength"]["timestamp"]
        print(
            f'dt {stamp-start:.2f} '
            f' strength={r["mag-magnetic_strength"]["value"]:.3f}'
            f' current={r["mag-current"]["value"]:.3f}'
        )
    await pc.unstage()


if __name__ == "__main__":
    asyncio.run(run_device())