import time
import warnings
from pathlib import Path
from typing import List, Union

import pytest
from _pytest.config import Config
from _pytest.main import Session
from _pytest.nodes import Item
from _pytest.python import Metafunc
from _pytest.runner import CallInfo
from pytest_metadata.plugin import metadata_key

from .helpers.framework import (
    FixtureExtraList, construct_parametrized_args_from_module_variable,
    get_fixtures_of_type, get_items_to_mark)

NL = "\n"


class BaselineTestManager:
    def __init__(self, config: Config) -> None:
        self._config = config
        self._has_html = None
        self.env = self._config.getoption("ENV", "")
        self.add_description_html = True

        # Get and Set Logo
        logo = self._config.hook.pytest_baseline_client_logo()
        if not isinstance(logo, str):
            if isinstance(logo, list):
                logo = "\n".join([str(x) for x in logo])
            else:
                logo = str(logo)
        self.logo = logo

        # Obtain Parametrized Module Variable Fixture info
        self.parametrized_module_variable_info = []
        self._config.hook.pytest_baseline_parametrized_module_variable_info(
            module_variable_info=self.parametrized_module_variable_info
        )

        self.fixtures_extra_config = FixtureExtraList()
        self._config.hook.pytest_baseline_fixtures_add_to_report(
            fixtures_extra_config=self.fixtures_extra_config
        )

    @property
    def has_html(self) -> bool:
        if self._has_html is None:
            if getattr(self._config.option, "htmlpath") is None:
                self._has_html = False
            else:
                self._has_html = True
        return self._has_html

    def pytest_report_header(
        self,
        config: Config,
        start_path: Path
    ) -> Union[str, List[str]]:
        """Return a string or list of strings to be displayed as header info
        for terminal reporting.

        :param config: The pytest config object.
        :param start_path: The starting dir.
        :type start_path: pathlib.Path
        :param startdir: The starting dir (deprecated).

        .. note::

            Lines returned by a plugin are displayed before those of plugins
            which ran before it.
            If you want to have your line(s) displayed first, use
            :ref:`trylast=True <plugin-hookorder>`.

        .. versionchanged:: 7.0.0
            The ``start_path`` parameter was added as a :class:`pathlib.Path`
            equivalent of the ``startdir`` parameter. The ``startdir``
            parameter has been deprecated.

        Use in conftest plugins
        =======================

        This hook is only called for :ref:`initial conftests <pluginorder>`.
        """
        # Obtain for format logo
        hdr_lines = []
        if self.logo != "":
            hdr_lines.append(self.logo)
            hdr_lines.append("")
        return hdr_lines

    def pytest_configure(self, config: Config) -> None:
        """Allow plugins and conftest files to perform initial configuration.

        This hook is called for every plugin and initial conftest file
        after command line options have been parsed.

        After that, the hook is called for other conftest files as they are
        imported.

        .. note::
            This hook is incompatible with ``hookwrapper=True``.

        :param pytest.Config config: The pytest config object.
        """
        config.stash[metadata_key]["Environment"] = self.env
        config.stash[metadata_key]["Invoking Command"] = (
            f"pytest {' '.join(config.invocation_params.args)}"[:250]
        )
        config.stash[metadata_key]["Start Time"] = time.strftime(
            "%Y-%m-%dT%H:%M:%S"
        )

        if (
            hasattr(config.option, 'htmlpath')
            and config.option.htmlpath is not None
        ):
            print("i'm here", self.env, config.option.htmlpath)
            config.option.htmlpath = config.option.htmlpath.format(
                date=time.strftime("%Y-%m-%dT%H-%M"),
                env=self.env
            )
            print("i'm here", self.env, config.option.htmlpath)

        config.addinivalue_line(
            "markers", "env(name): mark test to run only on named environment"
        )

    def pytest_html_results_table_header(self, cells):
        """Adding columns to HTML Report, Description"""
        if self.add_description_html and self.has_html:
            cells.insert(2, "<th>Desciption</th>")
            cells.insert(1, '<th class="sortable">Parametrization ID</th>')

    def pytest_html_results_table_row(self, report, cells):
        """Adding values to columns of HTML Report, Description"""
        if self.add_description_html and self.has_html:
            if hasattr(report, "description"):
                cells.insert(2, f"<td>{report.description}</td>")
            else:
                cells.insert(2, "<td>None</td>")

            # Add parametrization
            test_name = report.head_line
            if "[" in test_name:
                param = test_name.split("[")[1][:-1]
            else:
                param = "not a parametrized test"
            cells.insert(1, f'<td>{param}</td>')

    def pytest_generate_tests(self, metafunc: Metafunc):
        """Generate (multiple) parametrized calls to a test function."""

        for info in self.parametrized_module_variable_info:
            if f"{info[0]}_value" in metafunc.fixturenames:
                params = construct_parametrized_args_from_module_variable(
                    metafunc, *info)
                metafunc.parametrize(**params)

    @pytest.hookimpl(tryfirst=True)
    def pytest_collection_modifyitems(
        self,
        session: Session,
        config: Config,
        items: List[Item]
    ):
        """Called after collection has been performed. May filter or re-order
        the items in-place.

        :param pytest.Session session: The pytest session object.
        :param _pytest.config.Config config: The pytest config object.
        :param List[pytest.Item] items: List of item objects.
        """
        # Get items by module to reduce execution time
        items_by_module = {}
        for item in items:
            this_module = item.module.__name__
            if this_module not in items_by_module.keys():
                items_by_module[this_module] = []
            items_by_module[this_module].append(item)

        # Get all the custom markers plus `skip` and `xfail`
        builtin_markers = set([
            "filterwarnings",
            "skipif",
            "parametrize",
            "usefixtures",
            "tryfirst",
            "trylast"
        ])
        available_markers_names = set([
            x.split('(')[0].split(':')[0]
            for x in config.getini('markers')
        ]) - builtin_markers
        configured_markers = {x: set() for x in available_markers_names}
        marked_markers = {x: set() for x in available_markers_names}

        # Loop through each module's items to mark appropriately
        for module_name, items in items_by_module.items():

            for marker, configured in configured_markers.items():
                items_to_mark = get_items_to_mark(items[0], f"{marker}_tests")
                configured.update(
                    [f"{module_name}.{x}" for x in items_to_mark]
                )
                for item in items:

                    # Determine item name
                    if item.cls is not None:
                        item_name = f"{item.cls.__name__}.{item.name}"
                    else:
                        item_name = item.name
                    if item_name in items_to_mark.keys():

                        # Special Case for Skip
                        if marker == "skip":
                            item.add_marker(
                                pytest.mark.skip(
                                    reason=items_to_mark[item_name][0]
                                )
                            )

                        # Special Case for xfail
                        elif marker == "xfail":
                            raises_exception = (
                                items_to_mark[item_name][1]
                                if len(items_to_mark[item_name]) > 1
                                else AssertionError
                            )
                            item.add_marker(pytest.mark.xfail(
                                reason=items_to_mark[item_name][0],
                                strict=True,
                                raises=raises_exception
                            ))
                        else:
                            item.add_marker(marker)

                        marked_markers[marker].add(
                            f"{module_name}.{item_name}"
                        )
        for name in available_markers_names:
            if marked_markers[name] != configured_markers[name]:
                diff_set = configured_markers[name] - marked_markers[name]
                msg = (
                    f"Configured to be marked with '{name}' does not match "
                    "the tests actually marked, check that test names and "
                    f"classes are spelled correctly: {NL}{', '.join(diff_set)}"
                )
                warnings.warn(UserWarning(msg))

    def pytest_runtest_setup(self, item: Item) -> None:
        """Called to perform the setup phase for a test item.

        The default implementation runs ``setup()`` on ``item`` and all of its
        parents (which haven't been setup yet). This includes obtaining the
        values of fixtures required by the item (which haven't been obtained
        yet).
        """
        env_names = [
            y for mark in item.iter_markers(name="env") for y in mark.args
        ]
        if env_names:
            if self.env not in env_names:
                pytest.skip("test requires env in {!r}".format(env_names))

    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_makereport(self, item: Item, call: CallInfo):
        """Called to create a :py:class:`_pytest.reports.TestReport` for each
        of the setup, call and teardown runtest phases of a test item.

        See :func:`pytest_runtest_protocol` for a description of the runtest
        protocol.

        :param CallInfo[None] call: The ``CallInfo`` for the phase.

        Stops at first non-None result, see :ref:`firstresult`.
        """
        outcome = yield
        report = outcome.get_result()

        # Make sure there is even a report to generate stuff for
        if self.has_html:

            # Obtain Doc Str, set it in report
            doc_str = (
                str(item.function.__doc__)
                if item.function.__doc__ else "No Description"
            )
            report.description = doc_str

            # Right before Tests is called is best time to get what resources
            # are available to the test and the state they are in
            if report.when == "call":

                # Get existing extras, or start new array
                extra = getattr(report, "extra", [])

                # Loop through all configured fixtures to print
                for fixture_to_print in self.fixtures_extra_config:

                    # Get all fixtures that match type requested to print
                    fixtures = get_fixtures_of_type(
                        funcargs=item.funcargs,
                        fixture_type=fixture_to_print.type,
                        check_dict_values=fixture_to_print.search_dict
                    )

                    # Generate Printouts
                    for fix_name, scope, full_name, fix_value in fixtures:

                        # Second configured Check
                        if fixture_to_print.filter_check(
                            fixture_name=fix_name,
                            fixture_value=fix_value,
                            scope=scope,
                            full_name=full_name,
                        ):
                            extra.append(fixture_to_print.generate_printout(
                                fixture_value=fix_value,
                                fixture_name=fix_name,
                                scope=scope,
                                full_name=full_name,
                                test_item=item,
                                test_call=call
                            ))

                # Make sure to add back the extras, incase not defined
                # originally
                report.extra = extra


def pytest_html_results_table_header(cells):
    """Adding columns to HTML Report, Description"""
    cells.insert(1, '<th class="sortable">Parametrization ID</th>')


def pytest_html_results_table_row(report, cells):
    """Adding values to columns of HTML Report, Description"""
    test_name = report.head_line
    if "[" in test_name:
        param = test_name.split("[")[1][:-1]
    else:
        param = "not a parametrized test"
    cells.insert(1, f'<td>{param}</td>')
