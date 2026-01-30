from collections import defaultdict

from accml.app.tune.model import MeasuredTuneResponse, MeasuredTuneResponseItem, MeasuredTuneResponsePerPowerConverter
from accml_lib.core.model.output.result import Result


def data_to_model(data: Result) -> MeasuredTuneResponse:
    tmp = defaultdict(list)

    for epoch in data.data:
        # Todo: improve me
        #       currently only taking the last data value
        single =  epoch.data[-1]
        tune = single.get("tune-transversal").payload
        # currently only prepared that a single command i.e. state change was applied
        cmd, = epoch.cmds
        dev_name = cmd.id
        tmp[str(dev_name)].append(
            MeasuredTuneResponseItem(setpoint=float(cmd.value), x=float(tune["x"]), y=float(tune["y"]))
        )

    r = MeasuredTuneResponse(
        col=[
            MeasuredTuneResponsePerPowerConverter(pc_name=dev_name, col=items)
            for dev_name, items in tmp.items()
        ]
    )
    return r
