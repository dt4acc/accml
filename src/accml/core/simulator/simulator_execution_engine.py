import asyncio
import datetime
import itertools
from itertools import zip_longest
from typing import Sequence, Mapping
from uuid import uuid4

from accml.core.interfaces.backend.backend import BackendRW
from accml.core.interfaces.command_rewritter import CommandRewriterBase
from accml.core.interfaces.measurement_execution_engine import (
    MeasurementExecutionEngine,
)
from accml.core.model.command import Command, ReadCommand, TransactionCommand, BehaviourOnError
from accml.core.model.result import SingleReading, Result, ReadTogether


async def execute_step(
    backend: BackendRW,
    devices: Sequence[ReadCommand],
    transactional_commands: Sequence[Command],
):
    """Handle transactional commands"""
    # for simulator this is not necessary but just in case
    # set all in parallel
    await asyncio.gather(
        *[
            backend.set(dev_id=cmd.id, prop_id=cmd.property, value=cmd.value)
            for cmd in transactional_commands
        ]
    )
    await asyncio.gather(
        *[backend.trigger(dev_id=dev.id, prop_id=dev.property) for dev in devices]
    )
    # read in parallel
    data = await asyncio.gather(
        *[backend.read(dev_id=dev.id, prop_id=dev.property) for dev in devices]
    )

    return {f"{dev.id}-{dev.property}": datum for dev, datum in zip(devices, data)}


async def execute(
    backend: BackendRW,
    devices: Sequence[ReadCommand],
    commands: Sequence[TransactionCommand],
):
    start = datetime.datetime.now()
    d = dict(
        start=start,
        commands=commands,
        # execute one step after the other
        data=[
            await execute_step(backend, devices, cmd.transaction) for cmd in commands
        ],
    )
    d["end"] = datetime.datetime.now()
    return d


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
        devices: Sequence[ReadCommand],
        *,
        md,
        **kwargs,
    ) -> str:
        """

        The commands collections is missing Context i.e. in which view it is
        operating.
        """

        def convert(transaction: Sequence[Command]) -> Sequence[Command]:
            tmp = [self.cmd_rewritter.inverse(cmd) for cmd in transaction]
            r = list(itertools.chain(*tmp))
            return r

        cmd_design_ctxt = [
            TransactionCommand(transaction=convert(transaction.transaction))
            for transaction in commands_collection
        ]

        loop = asyncio.get_event_loop()
        data = loop.run_until_complete(execute(self.backend, devices, cmd_design_ctxt))
        # Todo: need to convert data to expected

        def convert_data(data: Sequence[Mapping[str, object]]) -> Sequence[ReadTogether]:
            """

            Here only command rewritter is used. As always the same command is used
            one could just look up the translation object once and then do batch
            processing.

            Early optimisation ...
            """

            def convert_single(cmd, datum):
                cmd.value = datum
                ncmd = self.cmd_rewritter.forward(cmd)
                return ncmd.value

            cmds = [
                Command(id=rcmd.id, property=rcmd.property, value=None, behaviour_on_error=BehaviourOnError.ignore)
                for rcmd in devices
            ]
            # Todo: use key for checking ...
            return [
                ReadTogether(
                    data=[SingleReading(name=datum[0], payload=convert_single(cmd, datum[1])) for cmd, datum in zip_longest(cmds, epoch.items())]
                )
                for epoch in data
            ]

        converted = Result(
            start=data["start"],
            end=data["end"],
            data=convert_data(data["data"]),
            orig_data=[
                ReadTogether(data=[SingleReading(name=k, payload=v) for k, v in single.items()])
                for single in data["data"]
            ]
        )
        del data
        uuid = self.storage.add(converted)
        return uuid
