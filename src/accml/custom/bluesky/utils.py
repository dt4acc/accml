import asyncio
import itertools
from typing import Sequence

from accml_lib.core.model.utils.command import TransactionCommand


def extract_device_identifiers(commands_collection: Sequence[TransactionCommand]) -> Sequence[str]:
    return list(itertools.chain(*[[cmd.id for cmd in tc.transaction] for tc in commands_collection]))


async def connect_to_devices(devices, timeout=5.0):
    """
    """
    for dev in devices:
        assert dev is not None, "Sanity check, all devices must not be None"

    return await asyncio.gather(
        *[dev.connect(timeout=timeout) for dev in devices]
    )
