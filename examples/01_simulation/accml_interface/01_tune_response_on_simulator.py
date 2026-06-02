import json
from collections import defaultdict
from typing import Union, Sequence

import jsons

from accml.app.tune.tune_measurement import measure_tune_response
from accml.core.utils.basic_measurement_execution_engine import BasicMeasurementExecutionEngine
from accml.core.utils.simple_storage import SimpleDataStorage
from accml_lib.core.model import jsons_support
from accml_lib.custom.als.pyat_simulator_backend import simulator_backend
from accml_lib.core.bl.delta_backend import StateCache
from dt4acc.custom_facility.als.liaison_translator_setup import load_managers
from dt4acc.custom_facility.als.model import MMLStyleDeviceIdentifier
from dt4acc.custom_facility.als.utils import get_power_converters_from_tune_correction_quads
from dt4acc_lib.bl.command_rewritter import CommandRewriter
from dt4acc_lib.model.utils.identifiers import DevicePropertyID, LatticeElementPropertyID
from dt4acc_lib.model.utils.command import ReadCommand, Command
from dt4acc_lib.interfaces.utils.liaison_manager import LiaisonManagerBase


jsons_fork = jsons.fork()
jsons_support.register_serializers(jsons_fork)




async def main():
    # I could use a different cache for command translation and
    # measurement execution. I prefer to use the same one here
    # I need to populate it with necessary reference data
    # Command rewriter will not read data into it
    # I will populate it further down after the measurement engine was
    # instantiated
    reference_state_cache = StateCache(name="ALS_on_PyAT_delta_state_cache")
    backend = simulator_backend(reference_state_cache)

    yp, lm, ts, _ = load_managers()

    ts.register_reference_cache(reference_state_cache)
    # Yellow pages: need to get clearer what it returns
    #   * names as used in the lattice?
    #   * names as expected by users of Matlab middle layer?
    tune_correction_quads = yp.get("tune_correction_quadrupoles")
    # Find out to which power converters these are connected to
    # I was guessing power converter names from the info I had in the ao objects
    pc_set_pvs = get_power_converters_from_tune_correction_quads(lm, tune_correction_quads)
    # Now I add a hack: I only use quadrupoles whoes power converter is unique
    # I should rather work in device space right away
    pc_set_pvs=list(set(pc_set_pvs))

    storage = SimpleDataStorage()
    mexec = BasicMeasurementExecutionEngine(
        backend=backend,
        cmd_rewriter=CommandRewriter(liaison_manager=lm, translation_service=ts),
        storage=storage,
        expected_view_for_output="device",
        num_readings=1,
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

    # ref_vals = await mexec.trigger_read(rcmds_for_ref_values_quad_pcs)
    uuid = await measure_tune_response(
       detectors=[
           ReadCommand("tune", "transversal"),
       ],
       quadrupole_pc_names=pc_set_pvs,
       measurement_values=[0, 1e-1, 0, -1e-1, 0],
       mexec=mexec,
       info_signals=None
    )
    data = storage.get(uuid)
    data = jsons.dump(data, fork_inst=jsons_fork)

    with open("../../06_measurement_simulation_data/tune_response_data_from_simulator.json", "wt") as fp:
        json.dump(data, fp, indent=4)


if __name__  == "__main__":
    import asyncio
    asyncio.run(main())