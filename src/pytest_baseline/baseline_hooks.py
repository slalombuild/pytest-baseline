from .annotations import FixtureInfoType
from .BaselineTestManager import FixtureExtraList


def pytest_baseline_client_logo() -> str:
    """Called during pytest_report_header to obtain a logo to print at start of
    terminal output
    """
    return ""


def pytest_baseline_parametrized_module_variable_info(
    module_variable_info: FixtureInfoType
) -> None:
    """Called during pytest_generate_tests to obtain parametrized fixture info,
    Append to fixture_info tuples that pass info to
    `construct_parametrized_args_from_module_variable` where first item is the
    NAME following "NAME[_data/_value]" format, second is the skip value, or
    value of configuration to skip the test, third is an optional id function
    (callable) for building the display id for the console, defaults to pytest
    parametrized unique id function.
    """


def pytest_baseline_fixtures_add_to_report(
    fixtures_extra_config: FixtureExtraList
) -> None:
    """Add to List for fixtures to include on HTML Report"""
