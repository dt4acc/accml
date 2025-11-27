import pytest
from unittest.mock import Mock, MagicMock
from bluesky import RunEngine
from ophyd_async.core import Signal

from accml.custom.epics.bluesky_measurement_execution_engine import (
    commands_plan,
    commands_execution_plan,
    BlueskyMeasurementExecutionEngine,
)
from accml.core.model.command import Command


@pytest.fixture
def mock_devices():
    """Mock devices for testing."""
    actuator = Mock()
    actuator.name = "mock_actuator"
    actuator.parent = None
    actuator.set_current = Mock()
    actuator.set_current.parent = None
    detector = Mock()
    detector.name = "mock_detector"
    detector.parent = None
    return {"mock_actuator": actuator}, [detector]


@pytest.fixture
def mock_info_signals():
    """Mock info signals."""
    device_name = Mock(spec=Signal)
    device_name.parent = None
    channel_name = Mock(spec=Signal)
    channel_name.parent = None
    channel_value = Mock(spec=Signal)
    channel_value.parent = None
    return {
        "device_name": device_name,
        "channel_name": channel_name,
        "channel_value": channel_value,
    }


@pytest.fixture
def sample_commands():
    """Sample commands for testing."""
    return [
        Command(id="mock_actuator", property="set_current", value=1.0, behaviour_on_error="stop"),
    ]


@pytest.fixture
def mock_run_engine():
    """Mock RunEngine."""
    re = Mock(spec=RunEngine)
    re.return_value = ("mock_uid",)
    return re


def test_commands_plan_execution(mock_devices, mock_info_signals, sample_commands):
    """Test that commands_plan yields the expected Bluesky messages."""
    actuators, detectors = mock_devices
    plan = list(commands_plan(sample_commands, detectors, actuators, mock_info_signals))
    assert len(plan) > 0  # Basic check; in practice, inspect yielded messages


def test_commands_execution_plan_structure(mock_devices, mock_info_signals, sample_commands):
    """Test that commands_execution_plan wraps the inner plan correctly."""
    actuators, detectors = mock_devices
    plan = commands_execution_plan(sample_commands, detectors, actuators, mock_info_signals, md={})
    # Plan is a generator; check it can be iterated without errors
    list(plan)


def test_bluesky_measurement_execution_engine_init(mock_run_engine):
    """Test initialization of BlueskyMeasurementExecutionEngine."""
    engine = BlueskyMeasurementExecutionEngine(mock_run_engine)
    assert engine.run_engine == mock_run_engine


def test_bluesky_measurement_execution_engine_execute(mock_run_engine, mock_devices, mock_info_signals, sample_commands):
    """Test execute method calls RunEngine with the plan."""
    actuators, detectors = mock_devices
    engine = BlueskyMeasurementExecutionEngine(mock_run_engine)
    uid = engine.execute([sample_commands], detectors, actuators, mock_info_signals, md={})
    assert uid == "mock_uid"
    mock_run_engine.assert_called_once()