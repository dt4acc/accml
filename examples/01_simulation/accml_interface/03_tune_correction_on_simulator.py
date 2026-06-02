import logging

from accml.app.tune.model import TuneResponseCollection
from accml.core.utils.basic_measurement_execution_engine import BasicMeasurementExecutionEngine
from accml.core.utils.simple_storage import SimpleDataStorage
from accml_lib.core.bl.delta_backend import StateCache
from accml_lib.custom.als.pyat_simulator_backend import simulator_backend
from dt4acc.custom_facility.als.utils import get_power_converters_from_tune_correction_quads
from dt4acc_lib.bl.command_rewritter import CommandRewriter
from dt4acc.custom_facility.als.liaison_translator_setup import load_managers
from dt4acc_lib.model.output.tune import Tune
from dt4acc_lib.model.utils.command import ReadCommand
from dt4acc_lib.model.utils.identifiers import DevicePropertyID

# from accml_lib.core.model.output.tune import  Tune

logging.basicConfig(level=logging.WARNING)

import yaml
import jsons

from accml.app.tune.tune_correction import tune_correction


async def main():
    with open("../../05_reference_data/tune_response_from_simulation.yml") as fp:
        d = yaml.load(fp, yaml.SafeLoader)
    dm = jsons.load(d, TuneResponseCollection)

    reference_state_cache = StateCache(name="ALS_on_PyAT_delta_state_cache")
    backend = simulator_backend(reference_state_cache)

    yp, lm, ts, _ = load_managers()
    ts.register_reference_cache(reference_state_cache)
    pc_set_pvs = get_power_converters_from_tune_correction_quads(lm, yp.get("tune_correction_quadrupoles"))
    # Now I add a hack: I only use quadrupoles whoes power converter is unique
    # I should rather work in device space right away
    pc_set_pvs = list(set(pc_set_pvs))

    mexec = BasicMeasurementExecutionEngine(
        backend=backend,
        cmd_rewriter=CommandRewriter(liaison_manager=lm, translation_service=ts),
        expected_view_for_output="device",
        num_readings=1,
        storage=None
    )

    # I need to populate the reference with appropriate reference values before
    # I can apply the commands
    # Only necessary as the commands are constructed in design view
    rcmds_for_ref_values_quad_pcs  = [
        ReadCommand(pv, "set_current") for pv in pc_set_pvs
    ]

    # Device view: populating directly
    for rcmd in rcmds_for_ref_values_quad_pcs:
        tmp = await mexec.trigger_read([rcmd])
        ref_val, = tmp.data
        reference_state_cache.set(rcmd, ref_val.payload)

    # Design view: peeking into engine
    for rcmd in rcmds_for_ref_values_quad_pcs:
        src, = lm.inverse(DevicePropertyID(rcmd.id, rcmd.property))
        val = await backend.read(src.element_name, src.property)
        design_view_rcmd = ReadCommand(src.element_name, src.property)
        reference_state_cache.set(design_view_rcmd, val)
        pass

    await tune_correction(
        dm,
        tune_target=Tune(x=272, y=380),
        mexec=mexec,
        token_for_tune_data="tune-delta_set_current"
    )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
