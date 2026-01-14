from collections import defaultdict
from itertools import zip_longest
from typing import Sequence, Dict

from bact_math_utils.misc import CountSame

from accml.app.tune.model import (
    MeasuredTuneResponsePerPowerConverter,
    MeasuredTuneResponseItem,
    MeasuredTuneResponse,
)


def data_to_model(data: Dict[str, Sequence[float]]) -> MeasuredTuneResponse:
    """For data as stored by bluesky / databroker"""
    # combine data per magnet
    tmp = defaultdict(list)

    cs = CountSame()
    for dev_name, val, tune, rep in zip_longest(
        data["device_name"],
        data["channel_value"],
        data["tunes"],
        cs(zip(data["device_name"], data["channel_value"])),
    ):
        tmp[str(dev_name)].append(
            MeasuredTuneResponseItem(
                setpoint=float(val), x=float(tune.x), y=float(tune.y), repetition=rep[0]
            )
        )

    # Now put it in a model
    r = MeasuredTuneResponse(
        col=[
            MeasuredTuneResponsePerPowerConverter(pc_name=dev_name, col=items)
            for dev_name, items in tmp.items()
        ]
    )
    return r


def select_repetitions_for_power_converter(
    data: MeasuredTuneResponsePerPowerConverter, acceptable_repetition: Sequence[int]
) -> MeasuredTuneResponsePerPowerConverter:
    """Filter out the acceptable data using repetition

    For BESSY II e.g. the Tune measurement is free running, thus the first
    value taken can be correct, but not necessarily. So the race condition is avoided taken
    only acceptable repetitions
    """
    return MeasuredTuneResponsePerPowerConverter(
        pc_name=data.pc_name,
        col=[item for item in data.col if item.repetition in acceptable_repetition],
    )


def select_repetitions(
    data: MeasuredTuneResponse, acceptable_repetition: Sequence[int]
) -> MeasuredTuneResponse:
    return MeasuredTuneResponse(
        col=[
            select_repetitions_for_power_converter(
                data=t_col, acceptable_repetition=acceptable_repetition
            )
            for t_col in data.col
        ]
    )
