import functools
from inspect import isgeneratorfunction
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import pytest
from _pytest.fixtures import FixtureRequest
from _pytest.nodes import Item
from _pytest.python import Metafunc, Module
from _pytest.runner import CallInfo
from pytest_html import extras

from ..annotations import (FixtureExtraFilterFunc, FixtureExtraPrintFunc,
                           HtmlExtraType)

NL = "\n"


def fixture_print_wrapper(
    char: str = "-",
    length: int = 100
) -> Callable[[Callable[..., Any]], Any]:
    def fixture_print_wrapper(func: Callable[..., Any]) -> Callable[..., Any]:
        """Wraps a fixture to print out the start and end of a fixture
        executing to help in log traces, decorator must be placed after
        `@pytest.fixture` decorator.  This decorator will work for both yield
        and regular return fixtures
        """
        @functools.wraps(func)
        def yield_wrapper(*args, **kwargs):
            f_name = f"{func.__module__}.{func.__name__}"
            print(
                f"{f'[ START Yield {f_name} ]':{char}^{length}}"
            )
            val = yield from func(*args, **kwargs)
            print(
                f"{f'[ END Yield {f_name} ]':{char}^{length}}"
            )
            return val

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            print(f"{f'[ START {func.__module__}.{func.__name__} ]':{char}^{length}}")
            val = func(*args, **kwargs)
            print(f"{f'[ END {func.__module__}.{func.__name__} ]':{char}^{length}}")
            return val

        if isgeneratorfunction(func):
            return yield_wrapper
        else:
            return wrapper
    return fixture_print_wrapper


def check_duplicate_keys_list_of_dict(
    list_to_check: List[Dict[str, Any]],
    key_to_check: str
) -> Union[None, AssertionError]:
    """Checks that all `key_to_check` values in all the Dictionaries in a list
    are unique, raises AssertionError
    """
    names = [x[key_to_check] for x in list_to_check]
    assert len(set(names)) == len(names), (
        f"There are duplicate values for '{key_to_check}' Key"
    )


def get_module_defined_configuration(
    request_obj: Union[FixtureRequest, Metafunc, Item],
    config_name: str,
    default: Optional[Any] = None,
    skip_if_not_defined: Optional[bool] = False,
    override_module: Optional[Module] = None
) -> Any:
    """Returns the value stored in the module for the specific variable name
    or the default.  Will return the environment dependent version if it
    exists.  To mark a variable as environment specific append `_[ENV]` to the
    end of the variable,
    example: cloud_secrets_config_qal or cloud_secrets_config_Qal
    """
    if override_module is None:
        module = request_obj.module
    else:
        module = override_module

    # get configured test environment
    env = (
        request_obj.config.getoption("--env", "").upper()
        if request_obj.config.getoption("--env", "") is not None
        else ""
    )
    check_names = [
        f"{config_name}_{env}",
        f"{config_name}_{env.lower()}",
        config_name
    ]
    for var_name in check_names:
        if hasattr(module, var_name):
            return getattr(module, var_name)
    if skip_if_not_defined:
        pytest.skip(
            f"`{config_name}` not defined for `{module.__name__}`"
        )
    return default


def is_iterable(obj: Any) -> bool:
    """Returns whether an object is iterable or not"""
    try:
        _ = iter(obj)
    except TypeError:
        return False
    else:
        return True


def construct_parametrized_args_from_module_variable(
    metafunc: Metafunc,
    root_name: str,
    skip_value: Any,
    id_func: Optional[Callable] = None,
    is_indirect: bool = False
) -> Dict[str, Union[str, List[Any], Callable]]:
    """Constructs the arguments to be passed to parametrized marker for a
    fixture based on module variable. The module variable must be named
    `{root_name}_data` the requesting fixture must be named `{root_name}_value`
    """

    # Obtain module variables
    configured_values = get_module_defined_configuration(
        metafunc, f"{root_name}_data", skip_value
    )

    # if configured values are present parametrize otherwise skip test
    if configured_values == skip_value:
        ids = ["Not Configured"]
        params = [
            pytest.param(
                [],
                marks=pytest.mark.skip(
                    f"No Configured `{root_name}_data` values"
                ),
            )
        ]
    else:
        ids = id_func
        if (
            isinstance(configured_values, str)
            or not is_iterable(configured_values)
        ):
            configured_values = [configured_values]
        params = configured_values

    return {
        "argnames": f"{root_name}_value",
        "argvalues": params,
        "indirect": is_indirect,
        "ids": ids
    }


def get_fixtures_of_type(
    funcargs: Dict[str, Any],
    fixture_type: Union[Any, Tuple[Any, ...]],
    check_dict_values: Optional[bool] = True,
) -> List[Tuple[str, str, str, Any]]:
    """Returns a list of tuples of overall fixture name, overall fixture scope,
    item name, item value pairs of the type or types requested.
    check_dict_values option will check if the values
    of a dictionary are of the type requested
    """
    fixtures_to_rtn = []
    request_fix = funcargs.get("request", None)
    for name, fixture in funcargs.items():
        if request_fix is not None:
            fixture_def = request_fix._fixture_defs.get(name)
            fixture_scope = getattr(fixture_def, "scope", "unknown")
        else:
            fixture_scope = "unknown"
        fixture_dict = {
            name: fixture
        }
        if isinstance(fixture, dict) and check_dict_values:
            fixture_dict.update(
                {f"{k}({name})": v for k, v in fixture.items()}
            )

        # Add all fixtures if they are of the correct type
        fixtures_to_rtn.extend(
            [
                (
                    name,
                    fixture_scope,
                    f_name,
                    f_value
                )
                for f_name, f_value in fixture_dict.items()
                if isinstance(f_value, fixture_type)
            ]
        )
    return fixtures_to_rtn


def get_items_to_mark(
    request_obj,
    var_name: str,
    default_reason: str = "Marked in Module"
) -> List[Tuple[str, ...]]:
    """Obtains module variable for marker"""
    raw_skip_array = get_module_defined_configuration(
        request_obj,
        var_name,
        []
    )
    items_to_skip = {}
    for raw_item in raw_skip_array:
        if not isinstance(raw_item, tuple):
            raw_item = (raw_item, default_reason)
        items_to_skip[raw_item[0]] = raw_item[1:]
    return items_to_skip


class FixtureExtra:
    def __init__(
        self,
        type: Any,
        search_dict: Optional[bool] = False,
        filter_func: FixtureExtraFilterFunc = None,
        print_func: FixtureExtraPrintFunc = None,
        html_extra_type: HtmlExtraType = extras.text
    ):
        self.type = type
        self.search_dict = search_dict
        self.filter_func = filter_func
        self.print_func = print_func
        self.html_extra_type = html_extra_type

    def filter_check(
        self,
        fixture_value: Any,
        fixture_name: str,
        scope: str,
        full_name: str,
    ) -> bool:
        """Calls the configured filter function if exists otherwise returns
        True
        """
        if self.filter_func is None:
            return True
        return self.filter_func(
            fixture_name=fixture_name,
            scope=scope,
            full_name=full_name,
            fixture_value=fixture_value
        )

    def generate_printout(
        self,
        fixture_value: Any,
        fixture_name: str,
        scope: str,
        full_name: str,
        test_item: Item,
        test_call: CallInfo
    ) -> Dict[str, Any]:
        """Calls the configured print function if exists otherwise returns
        string value of the fixture Value
        """

        # determine if print function is defined
        if self.print_func is None:
            try:
                print_info = str(fixture_value)
            except TypeError:
                print_info = (
                    "Encountered TypeError attempting to generate string "
                    f"representation for {full_name} (type: {self.type}), "
                    "consider using a custom print function in "
                    "`pytest_baseline_fixtures_add_to_report` hook."
                )
        else:
            print_info = self.print_func(
                fixture_value=fixture_value,
                fixture_name=fixture_name,
                scope=scope,
                full_name=full_name,
                test_item=test_item,
                test_call=test_call
            )
        if not isinstance(print_info, tuple):
            print_info = (print_info, full_name)
        return self.html_extra_type(*print_info)


class FixtureExtraList(List[FixtureExtra], list):
    def add_fixture_extra_config(
        self,
        type: Any,
        search_dict: bool = False,
        filter_func: FixtureExtraFilterFunc = None,
        print_func: FixtureExtraPrintFunc = None,
        html_extra_type: HtmlExtraType = extras.text
    ):
        """Appends a FixtureExtra object.
        - type: Required, the type of the object to check for
        - search_dict: Check the values of a fixture that returns a dict.
        - filter_func: Function that return whether to continue with generating
                       output or not if the type already matches
        - print_func: Function that returns string representation of object to
                      include in report.
        - html_extra_type: pytest-html extra type to include on report.
        """
        self.append(FixtureExtra(
            type=type,
            search_dict=search_dict,
            filter_func=filter_func,
            print_func=print_func,
            html_extra_type=html_extra_type
        ))
