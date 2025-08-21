from typing import Dict
import jsons

from .model import TuneResponseCollection, TuneResponseForFitItem, TuneResponse


def serialise_tune_response_collection(inst: TuneResponseCollection, **kwargs) -> Dict:
    assert isinstance(inst, TuneResponseCollection)
    r = dict(col=jsons.dump(inst.col, **kwargs))
    return r


def serialise_tune_response_for_fit_item(
    inst: TuneResponseForFitItem, **kwargs
) -> Dict:
    """
    required as polarity is defined as a Literal

    Todo:
        shall it be a cls method of TuneResponseForFitItem?
    """
    assert isinstance(inst, TuneResponseForFitItem)
    return dict(
        response=jsons.dump(inst.response, **kwargs), polarity=int(inst.polarity)
    )


def deserialise_tune_response_for_fit_item(
    inp: Dict, *args, **kwargs
) -> TuneResponseForFitItem:
    """
    required as polarity is defined as a Literal

    Todo:
        shall it be a cls method of TuneResponseForFitItem?
    """
    polarity = int(inp["polarity"])
    assert polarity in [-1, 1], f'polarity should be -1 or 1 but got "{polarity}"'
    return TuneResponseForFitItem(
        polarity=polarity,
        response=jsons.load(inp["response"], TuneResponse),
    )


def install_jsons_io():
    # todo: shall these serializers only be installed on user request ?
    #       is it straight forward to uninstall them if needed
    jsons.set_serializer(serialise_tune_response_for_fit_item, TuneResponseForFitItem)
    jsons.set_deserializer(
        deserialise_tune_response_for_fit_item, TuneResponseForFitItem
    )
    jsons.set_serializer(serialise_tune_response_collection, TuneResponseCollection)
