# -*- coding: utf-8 -*

from typing import Any, Callable, Optional

import pytest
from _pytest.config import Config, PytestPluginManager
from _pytest.config.argparsing import Parser
from _pytest.fixtures import FixtureRequest

from .BaselineTestManager import BaselineTestManager, FixtureExtraList
from .helpers.framework import get_module_defined_configuration
from .helpers.timer_laps import LapWatch


@pytest.fixture(name="timer")
def fixture_timer(request: FixtureRequest) -> LapWatch:
    """Returns a Lapwatch that can be used to record 'laps' to time certian
    parts of the test execution
    """
    module_name = request.module.__name__
    func_name = request.function.__name__
    if request.cls is None:
        test_name = f"{module_name}::{func_name}"
    else:
        test_name = f"{module_name}::{request.cls.__name__}.{func_name}"
    return LapWatch(test_name)


@pytest.fixture(name="env", scope="session")
def fixture_env(request: FixtureRequest) -> str:
    """Returns the passed --env command line argument"""
    return request.config.option.ENV


@pytest.fixture(name="module_variable", scope="module")
def fixture_module_variable(
    request: FixtureRequest
) -> Callable[[str, Optional[Any], Optional[bool]], Any]:
    """Helper fixture to obtain module variables for common tests.  Function
    wrapper removes the need to request """

    def func(
        name: str,
        default: Any = None,
        skip_if_not_defined: bool = False
    ):
        return get_module_defined_configuration(
            request,
            name,
            default,
            skip_if_not_defined
        )
    return func


###############################################################################
# Plugin to pytest hooks
###############################################################################
def pytest_addhooks(pluginmanager: PytestPluginManager) -> None:
    """Called at plugin registration time to allow adding new hooks via a
    call to ``pluginmanager.add_hookspecs(module_or_class, prefix)``.

    :param pytest.PytestPluginManager pluginmanager: The pytest plugin manager.

    .. note::
        This hook is incompatible with ``hookwrapper=True``.
    """
    from . import baseline_hooks

    pluginmanager.add_hookspecs(baseline_hooks)


def pytest_configure(config: Config) -> None:
    """Allow plugins and conftest files to perform initial configuration.

    This hook is called for every plugin and initial conftest file
    after command line options have been parsed.

    After that, the hook is called for other conftest files as they are
    imported.

    .. note::
        This hook is incompatible with ``hookwrapper=True``.

    :param pytest.Config config: The pytest config object.
    """
    config._baseline = BaselineTestManager(config)
    config.pluginmanager.register(config._baseline)


def pytest_unconfigure(config: Config) -> None:
    """Called before test process is exited.

    :param pytest.Config config: The pytest config object.
    """
    baseline_plugin = getattr(config, "_baseline", None)
    if baseline_plugin:
        del config._baseline
        config.pluginmanager.unregister(baseline_plugin)


def pytest_addoption(
    parser: Parser,
    pluginmanager: PytestPluginManager
) -> None:
    """Register argparse-style options and ini-style config values,
    called once at the beginning of a test run.

    .. note::

        This function should be implemented only in plugins or
        ``conftest.py`` files situated at the tests root directory due to
        how pytest :ref:`discovers plugins during startup <pluginorder>`.

    :param pytest.Parser parser:
        To add command line options, call
        :py:func:`parser.addoption(...) <pytest.Parser.addoption>`.
        To add ini-file values call :py:func:`parser.addini(...)
        <pytest.Parser.addini>`.

    :param pytest.PytestPluginManager pluginmanager:
        The pytest plugin manager, which can be used to install
        :py:func:`hookspec`'s or :py:func:`hookimpl`'s and allow one plugin
        to call another plugin's hooks to change how command line options
        are added.

    Options can later be accessed through the
    :py:class:`config <pytest.Config>` object, respectively:

    - :py:func:`config.getoption(name) <pytest.Config.getoption>` to
    retrieve the value of a command line option.

    - :py:func:`config.getini(name) <pytest.Config.getini>` to retrieve
    a value read from an ini-style file.

    The config object is passed around on many internal objects via the
    ``.config`` attribute or can be retrieved as the ``pytestconfig``
    fixture.

    .. note::
        This hook is incompatible with ``hookwrapper=True``.
    """
    group = parser.getgroup('baseline-plugin')
    group.addoption(
        "--env",
        dest="ENV",
        action="store",
        default="DEFAULT",
        help="Environment name to pass to tests"
    )
###############################################################################


def pytest_baseline_fixtures_add_to_report(
    fixtures_extra_config: FixtureExtraList
) -> None:
    """Add to List for fixtures to include on HTML Report"""
    fixtures_extra_config.add_fixture_extra_config(LapWatch)
