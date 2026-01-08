from collections import defaultdict

from accml.app.tune.model import MeasuredTuneResponse, MeasuredTuneResponseItem, MeasuredTuneResponsePerPowerConverter
from accml.core.model.result import Result


def data_to_model(data: Result) -> MeasuredTuneResponse:
    tmp = defaultdict(list)

    for single in data.data:
        tune = single.get("tune-transversal").payload
        dev_name = "unknown"
        setpoint = single.get("setpoint")
        dev_name = setpoint.cmd["id"]
        tmp[str(dev_name)].append(
            MeasuredTuneResponseItem(setpoint=float(setpoint.payload["value"]), x=float(tune["x"]), y=float(tune["y"]))
        )

    r = MeasuredTuneResponse(
        col=[
            MeasuredTuneResponsePerPowerConverter(pc_name=dev_name, col=items)
            for dev_name, items in tmp.items()
        ]
    )
    return r
