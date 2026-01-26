


async def measure_chromaticity(
    *,
    detectors: Sequence[ReadCommand],
    measurement_values: Sequence[float],
    mexec: MeasurementExecutionEngine = None,
    **kwargs
    ):

    md = {}

    uid = await mexec.execute(
        detectors=detectors,
        commands_collection=cmds_on_machine.commands,  # need to add bpms
        **kwargs,
        # detectors=[tunes],
        # actuators=actuators,
        # info_signals=info_signals,
        md=md,
    )
    print(f"Chromaticity run created {uid=}")
    return uid
