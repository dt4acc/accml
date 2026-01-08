from collections import defaultdict
from itertools import zip_longest
from typing import Sequence, Dict

from accml.app.tune.model import MeasuredTuneResponsePerPowerConverter, MeasuredTuneResponseItem, MeasuredTuneResponse


def data_to_model(data: Dict[str, Sequence[float]]) -> MeasuredTuneResponse:
    """For data as stored by bluesky / databroker
    """
    # combine data per magnet
    tmp = defaultdict(list)
    for dev_name, val, tune_x, tune_y in zip_longest(
        data["device_name"],
        data["channel_value"],
        data["tune-x-sig"],
        data["tune-y-sig"],
    ):
        tmp[str(dev_name)].append(
            MeasuredTuneResponseItem(setpoint=float(val), x=float(tune_x), y=float(tune_y))
        )

    # Now put it in a model
    r = MeasuredTuneResponse(
        col=[
            MeasuredTuneResponsePerPowerConverter(pc_name=dev_name, col=items)
            for dev_name, items in tmp.items()
        ]
    )
    return r
