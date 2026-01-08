import asyncio
import datetime
import itertools
from itertools import zip_longest
from typing import Sequence, Mapping, Any
from uuid import uuid4

from accml.core.interfaces.backend.backend import BackendRW
from accml.core.interfaces.command_rewritter import CommandRewriterBase
from accml.core.interfaces.measurement_execution_engine import (
    MeasurementExecutionEngine,
)
from accml.core.model.command import Command, ReadCommand, TransactionCommand, BehaviourOnError
from accml.core.model.result import SingleReading, Result, ReadTogether, SingleFloat


class SimpleDataStorage:
    def __init__(self):
        self.data = dict()

    def add(self, data) -> str:
        uuid = uuid4()
        self.data[uuid] = data
        return uuid

    def clear(self):
        self.data.clear()

    def keys(self):
        return self.data.keys()

    def get(self, uuid: str):
        return self.data.get(uuid)


class SimulatorExecutionEngine(MeasurementExecutionEngine):

    def __init__(
        self,
        *,
        backend: BackendRW,
        cmd_rewritter: CommandRewriterBase,
        storage: SimpleDataStorage,
    ):
        self.backend = backend
        self.cmd_rewritter = cmd_rewritter
        self.storage = storage

    def get_data(self, uuid):
        return self.storage.get(uuid)

    def execute(
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

        def convert(transaction: Sequence[Command]) -> Sequence[Command]:
            tmp = [self.cmd_rewritter.inverse(cmd) for cmd in transaction]
            r = list(itertools.chain(*tmp))
            return r

        if commands_collection is None:
            cmd_design_ctxt = None
        else:
            cmd_design_ctxt = [
            TransactionCommand(transaction=convert(transaction.transaction))
            for transaction in commands_collection
        ]

        loop = asyncio.get_event_loop()
        data = loop.run_until_complete(execute(self.backend, detectors, cmd_design_ctxt))

        converted_data = convert_data(self.cmd_rewritter, detectors, data["data"])
        #: Todo ... how to properly enrich the data ... analysis needs to know which
        #           device and which value
        def extract_single(t_cmd: TransactionCommand) -> SingleReading:
            # Only work is only one was set
            cmd, = t_cmd.transaction
            return SingleReading(name="setpoint", payload=SingleFloat(value=cmd.value), cmd=ReadCommand(id=cmd.id, property=cmd.property))

        enriched = [
            ReadTogether(data=single.data + [extract_single(transaction)])
            for single, transaction in zip_longest(converted_data, commands_collection)
        ]
        converted = Result(
            start=data["start"],
            end=data["end"],
            data=enriched,
            orig_data=[
                ReadTogether(data=[
                    SingleReading(name=tmp[0], cmd=rcmd, payload=tmp[1])
                    for tmp, rcmd in zip(single.items(), detectors)
                ])
                for single in data["data"]
            ],
            # md=dict(commands=cmd_design_ctxt)
        )
        del data
        uuid = self.storage.add(converted)
        return uuid

    async def trigger(self, cmds: Sequence[ReadCommand]):
        return await trigger(self.backend, cmds)

    async def read(self, cmds: Sequence[ReadCommand]) -> ReadTogether:
        """
        Todo:
            review handling context or view:
                * design / device

            Can commands be only converted once?

            command rewritter: separate function for
            read commands? i.e. a delegation to
            liasion manager
        """
        tmp =  [self.cmd_rewritter.inverse_read_command(r) for r in cmds]
        rcmds_design_ctxt = list(itertools.chain(*tmp))
        data = await read(self.backend, rcmds_design_ctxt)
        # Todo: how to convert data back ... I think
        #       that gets difficult as soon as there is no 1-to-1 mapping any more
        #       how to handle delta_ ... I need to be able to access reference storage
        converted_data = convert_data_seq(self.cmd_rewritter, rcmds_design_ctxt, data)
        return converted_data

    async def set(self, cmds: Sequence[Command]):
        tmp = [self.cmd_rewritter.inverse(cmd) for cmd in cmds]
        cmds_design_ctxt = itertools.chain(*tmp)
        return await set_(self.backend, cmds_design_ctxt)


async def execute(
    backend: BackendRW,
    detectors: Sequence[ReadCommand],
    commands: Sequence[TransactionCommand],
):
    start = datetime.datetime.now()
    d = dict(
        start=start,
        commands=commands,
        # execute one step after the other
        data=[
            await execute_step(backend, detectors, cmd.transaction) for cmd in commands
        ],
    )
    d["end"] = datetime.datetime.now()
    return d


async def execute_step(
    backend: BackendRW,
    detectors: Sequence[ReadCommand],
    transaction_commands: Sequence[Command],
):
    """Handle transactional commands"""
    # for simulator this is not necessary but just in case
    # set all in parallel
    await set_(backend=backend, transaction_commands=transaction_commands)
    await trigger(backend=backend, detectors=detectors)
    data = await read(backend=backend, detectors=detectors)
    return {f"{dev.id}-{dev.property}": datum for dev, datum in zip(detectors, data)}


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


async def read(backend: BackendRW, detectors: Sequence[ReadCommand]) -> Sequence[Any]:
    # read in parallel
    data = await asyncio.gather(
        *[backend.read(dev_id=dev.id, prop_id=dev.property) for dev in detectors]
    )
    return data


def convert_data_seq(cmd_rewritter: CommandRewriterBase, detectors: Sequence[ReadCommand], data: Sequence[object]) -> ReadTogether:
    """
    Todo:
        merge with convert_data

    """

    def convert_single(rcmd: ReadCommand, datum):
        if rcmd is None:
            pass
        cmd = Command(id=rcmd.id, property=rcmd.property, value=datum, behaviour_on_error=None)
        ncmd = cmd_rewritter.forward(cmd)
        return ncmd.value

    detectors
    # Todo: use key for checking ...
    r = ReadTogether(
        data=[SingleReading(name=f"{cmd.id}-{cmd.property}", cmd=cmd, payload=convert_single(cmd, datum))
                for cmd, datum in zip_longest(detectors, data)]
        )
    return r


def convert_data(cmd_rewritter: CommandRewriterBase, detectors: Sequence[ReadCommand], data: Sequence[Mapping[str, object]]) -> Sequence[ReadTogether]:
    """

    Here only command rewritter is used. As always the same command is used
    one could just look up the translation object once and then do batch
    processing.

    Early optimisation ...
    """

    def convert_single(cmd, datum):
        ncmd = cmd_rewritter.forward(Command(id=cmd.id, property=cmd.property, value=datum, behaviour_on_error=None))
        return ncmd.value

    cmds = [
        ReadCommand(id=rcmd.id, property=rcmd.property)
        for rcmd in detectors
    ]
    # Todo: use key for checking ...
    return [
        ReadTogether(
            data=[
                SingleReading(name=datum[0], cmd=ReadCommand(id=cmd.id, property=cmd.property), payload=convert_single(cmd, datum[1]))
                for cmd, datum in zip_longest(cmds, epoch.items())]
        )
        for epoch in data
    ]

