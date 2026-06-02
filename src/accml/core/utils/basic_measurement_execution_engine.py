import asyncio
import datetime
import itertools
from typing import Any, Mapping, Sequence

# from accml_lib.core.interfaces.backend.backend import BackendRW
# from accml_lib.core.interfaces.utils.command_rewritter import CommandRewriterBase
from accml_lib.core.interfaces.utils.measurement_execution_engine import MeasurementExecutionEngine
from accml_lib.core.interfaces.utils.storage import StorageInterface
# from accml_lib.core.model.utils.command import TransactionCommand, ReadCommand, Command
# from accml_lib.core.model.output.result import SingleReading, SingleFloat, ReadTogether, Result, ResultOfExecutionStep

import tqdm

from dt4acc_lib.interfaces.backend.backend import BackendRW
from dt4acc_lib.interfaces.utils.command_rewritter import CommandRewriterBase
from dt4acc_lib.model.utils.command import TransactionCommand, ReadCommand, Command
from dt4acc_lib.model.output.result import ReadTogether, ResultOfExecutionStep, SingleReading, SingleFloat, Result


class BasicMeasurementExecutionEngine(MeasurementExecutionEngine):
    """Common functionality of the measurement execution engine"""

    def __init__(
        self,
        *,
        backend: BackendRW,
        cmd_rewriter: CommandRewriterBase,
        storage: StorageInterface,
        expected_view_for_output: str,
        num_readings: int
    ):
        assert num_readings >= 1, f"{num_readings=} must be at least one!"
        self.backend = backend
        self.cmd_rewriter = cmd_rewriter
        self.storage = storage
        self.expected_view_for_output = expected_view_for_output
        self.num_readings = num_readings

    def get_data(self, uuid):
        return self.storage.get(uuid)

    def get_expected_view_for_output(self) -> str:
        return self.expected_view_for_output

    async def execute(
        self,
        commands_collection: Sequence[TransactionCommand],
        detectors: Sequence[ReadCommand],
        *,
        md,
        **kwargs,
    ) -> str:
        """

        The commands collections is missing Context i.e. in which view it is
        operating.


        Todo:
            evaluate if a set / read method should be provided as separate
            methods
        """

        if commands_collection is None:
            cmd_backend_ctxt = None
        else:
            cmd_backend_ctxt = [
                TransactionCommand(
                    transaction=convert_set_commands(
                        cmd_rewriter=self.cmd_rewriter,
                        commands=transaction.transaction,
                        commands_view=self.get_expected_view_for_output(),
                        target_view=self.backend.get_natural_view_name(),
                    )
                )
                for transaction in commands_collection
            ]

        # Todo: rewrite detectors!
        data = await execute(self.backend, detectors, cmd_backend_ctxt, num_readings=self.num_readings)

        # Todo: consider using ConvertedReadTogether based on ConvertedSingleReading
        #       these could contain the original and the converted data
        def _conv(data: ReadTogether):
            return ReadTogether(
                start=data.start,
                end=data.end,
                data=convert_data_seq(
                    cmd_rewriter=self.cmd_rewriter,
                    detectors=detectors,
                    data=data.data,
                    data_view=self.get_expected_view_for_output(),
                    target_view= self.backend.get_natural_view_name(),
                ),
            )
        converted_data = [[_conv(d) for d in epoch] for epoch in data]
        #: Todo ... how to properly enrich the data ... analysis needs to know which
        #           device and which value
        def extract_single(t_cmd: TransactionCommand) -> SingleReading:
            # Only work is only one was set
            (cmd,) = t_cmd.transaction
            return SingleReading(
                name="setpoint",
                payload=SingleFloat(value=cmd.value),
                cmd=ReadCommand(id=cmd.id, property=cmd.property),
            )

        measured_enriched = [
            ResultOfExecutionStep(data=epoch, cmds=tc.transaction)
            for epoch, tc in itertools.zip_longest(
                data, cmd_backend_ctxt
            )
        ]
        enriched = [
            ResultOfExecutionStep(data=epoch, cmds=tc.transaction)
            for epoch, tc in itertools.zip_longest(
                converted_data, commands_collection
            )
        ]
        converted = Result(
            data=enriched,
            orig_data=measured_enriched,
            # md=dict(commands=cmd_design_ctxt)
        )
        del data
        uuid = self.storage.add(converted)
        return uuid

    async def trigger_read(self, rcmds: Sequence[ReadCommand]) -> ReadTogether:
        """
        Todo:
            review handling context or view:
                * design / device

            Can commands be only converted once?

            command rewriter: separate function for
            read commands? i.e. a delegation to
            liaison manager
        """
        rcmds = convert_read_commands(
            cmd_rewriter=self.cmd_rewriter,
            commands=rcmds,
            output_view=self.get_expected_view_for_output(),
            backend_view=self.backend.get_natural_view_name(),
        )
        start = datetime.datetime.now()
        data = await read_and_encapsulate(self.backend, rcmds)
        end = datetime.datetime.now()
        # Todo: how to convert data back ... I think
        #       that gets difficult as soon as there is no 1-to-1 mapping any more
        #       how to handle delta_ ... I need to be able to access reference storage
        converted_data = convert_data_seq(
            cmd_rewriter=self.cmd_rewriter,
            detectors=rcmds,
            data=data.data,
            data_view=self.backend.get_natural_view_name(),
            target_view=self.get_expected_view_for_output(),
        )
        return ReadTogether(data=converted_data, start=start, end=end)

    async def set(self, cmds: Sequence[Command]):
        return await set_(
            self.backend,
            convert_set_commands(
                cmd_rewriter=self.cmd_rewriter,
                commands=cmds,
                commands_view=self.get_expected_view_for_output(),
                target_view=self.backend.get_natural_view_name(),
            ),
        )


async def execute(
    backend: BackendRW,
    detectors: Sequence[ReadCommand],
    commands: Sequence[TransactionCommand],
    num_readings: int
    ) -> Sequence[ReadTogether]:
    data_docs = []
    for cmd in tqdm.tqdm(commands, total=len(commands)):
        r = await execute_step(backend, detectors, cmd.transaction, num_readings=num_readings)
        data_docs.append(r)
    return data_docs


async def execute_step(
    backend: BackendRW,
    detectors: Sequence[ReadCommand],
    transaction_commands: Sequence[Command],
    num_readings: int
) -> Sequence[ReadTogether]:
    """Handle transactional commands"""
    assert num_readings >= 1
    # for simulator this is not necessary but just in case
    # set all in parallel: e.g. if used with ophyd_async backend
    await set_(backend=backend, transaction_commands=transaction_commands)
    await trigger(backend=backend, detectors=detectors)

    data_epoch = [await read_and_encapsulate(backend=backend, detectors=detectors) for cnt in range(num_readings)]
    return data_epoch

async def set_(backend: BackendRW, transaction_commands: Sequence[Command]) -> None:
    await asyncio.gather(
        *[
            backend.set(dev_id=cmd.id, prop_id=cmd.property, value=cmd.value)
            for cmd in transaction_commands
        ]
    )


async def trigger(backend: BackendRW, detectors: Sequence[ReadCommand]) -> None:
    # read in parallel
    await asyncio.gather(
        *[backend.trigger(dev_id=dev.id, prop_id=dev.property) for dev in detectors]
    )

async def read_and_encapsulate(backend: BackendRW, detectors: Sequence[ReadCommand]) -> ReadTogether:
    """put data into a ReadToGether envelope"""
    start = datetime.datetime.now()
    data = await read(backend, detectors)
    end = datetime.datetime.now()
    reading = [
        SingleReading(
            name=f"{cmd.id}-{cmd.property}", payload=datum, cmd=cmd,
        )
        for datum, cmd in zip(data, detectors)
    ]
    return ReadTogether(data=reading, start=start, end=end)

async def read(backend: BackendRW, detectors: Sequence[ReadCommand]) -> Sequence[Any]:
    # read in parallel
    data = await asyncio.gather(
        *[backend.read(dev_id=dev.id, prop_id=dev.property) for dev in detectors]
    )
    return data


def convert_read_commands(
    *,
    cmd_rewriter: CommandRewriterBase,
    commands: Sequence[ReadCommand],
    output_view: str,
    backend_view: str,
):
    command = commands
    if output_view == backend_view:
        # no need to convert
        return commands
    elif output_view == "design":
        assert (
            backend_view == "device"
        ), "expected to need to convert from design to device"
        #: Warning: this code path is not yet tested
        # raise AssertionError("This path is not yet tested!")
        tmp = [cmd_rewriter.forward_read_command(r) for r in command]
        return list(itertools.chain(*tmp))
    elif output_view == "device":
        assert (
            backend_view == "design"
        ), "expected to need to convert from device to design"
        tmp = [cmd_rewriter.inverse_read_command(r) for r in command]
        return list(itertools.chain(*tmp))

    raise AssertionError("Did not expect to end up here!")


def convert_set_commands(
    *,
    cmd_rewriter: CommandRewriterBase,
    commands: Sequence[Command],
    commands_view: str,
    target_view: str,
):
    """

    Todo:
        consider to rename input view and target view to context
    """

    if commands_view == target_view:
        # no need to convert
        return commands
    elif commands_view == "design":
        assert (
                target_view == "device"
        ), "expected to need to convert from design to device"
        tmp = [cmd_rewriter.forward(c) for c in commands]
        return list(itertools.chain(*tmp))
    elif commands_view == "device":
        assert (
                target_view == "design"
        ), "expected to need to convert from device to design"
        tmp = [cmd_rewriter.inverse(c) for c in commands]
        return list(itertools.chain(*tmp))
    raise AssertionError("Did not expect to end up here!")


def convert_transaction_commands_device_to_design(
    cmd_rewriter: CommandRewriterBase, transaction: Sequence[Command]
) -> Sequence[Command]:
    tmp = [cmd_rewriter.inverse(cmd) for cmd in transaction]
    r = list(itertools.chain(*tmp))
    return r


def convert_transaction_commands_design_to_device(
    cmd_rewriter: CommandRewriterBase, transaction: Sequence[Command]
) -> Sequence[Command]:
    """
    Warning:
            not tested code

    """
    tmp = [cmd_rewriter.forward(cmd) for cmd in transaction]
    r = list(itertools.chain(*tmp))
    return r


def convert_data_seq(
    *,
    cmd_rewriter: CommandRewriterBase,
    detectors: Sequence[ReadCommand],
    data: Sequence[SingleReading],
    data_view: str,
    target_view: str,
) -> Sequence[SingleReading]:
    """
    Todo:
        merge with convert_data

    """

    def create_command(rcmd: ReadCommand, datum: SingleReading):
        assert rcmd is not None
        return Command(
            id=rcmd.id, property=rcmd.property, value=datum.payload, behaviour_on_error=None
        )

    cmds = convert_set_commands(
        cmd_rewriter=cmd_rewriter,
        commands=[
            create_command(cmd, datum)
            for cmd, datum in itertools.zip_longest(detectors, data)
        ],
        commands_view=data_view,
        target_view=target_view,
    )

    # Todo: use key for checking ...
    r=[
        SingleReading(
            name=f"{cmd.id}-{cmd.property}",
            cmd=ReadCommand(id=cmd.id, property=cmd.property),
            payload=cmd.value
        )
        for cmd in cmds
    ]
    return r


def convert_data(
    cmd_rewriter: CommandRewriterBase,
    detectors: Sequence[ReadCommand],
    data: Sequence[Mapping[str, object]],
) -> Sequence[ReadTogether]:
    """

    Here only command rewritter is used. As always the same command is used
    one could just look up the translation object once and then do batch
    processing.

    Early optimisation ...
    """

    def convert_single(cmd, datum):
        ncmd = cmd_rewriter.forward(
            Command(
                id=cmd.id, property=cmd.property, value=datum, behaviour_on_error=None
            )
        )
        return ncmd.value

    cmds = [ReadCommand(id=rcmd.id, property=rcmd.property) for rcmd in detectors]
    # Todo: use key for checking ...
    return [
        ReadTogether(
            data=[
                SingleReading(
                    name=datum[0],
                    cmd=ReadCommand(id=cmd.id, property=cmd.property),
                    payload=convert_single(cmd, datum[1]),
                )
                for cmd, datum in itertools.zip_longest(cmds, epoch.items())
            ]
        )
        for epoch in data
    ]
