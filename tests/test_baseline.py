# -*- coding: utf-8 -*-
import pytest
from pytest import Pytester


@pytest.mark.parametrize("help_msg", [
    "baseline-plugin:",
    "*--env=ENV*Environment name to pass to tests"
])
def test_help_message(testdir: Pytester, help_msg: str):
    """Ensure all configured help options are displayed"""
    result = testdir.runpytest(
        '--help',
    )
    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines([help_msg])


def test_env_fixture_not_passed(testdir: Pytester):
    """Ensure --env option is being set to the default correctly for the `env`
    fixture
     """

    # create a temporary pytest test module
    testdir.makepyfile("""
        def test_env(env):
            assert env == "DEFAULT"
    """)

    # run pytest with the following cmd args
    result = testdir.runpytest("-v")

    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines([
        '*::test_env PASSED*',
    ])

    # make sure that that we get a '0' exit code for the testsuite
    assert result.ret == 0


def test_env_fixture_passed(testdir: Pytester):
    """Ensure --env option is being passed correctly to the `env` fixture"""

    # create a temporary pytest test module
    testdir.makepyfile("""
        def test_env(env):
            assert env == "dev"
    """)

    # run pytest with the following cmd args
    result = testdir.runpytest("-v", "--env=dev")

    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines([
        '*::test_env PASSED*',
    ])

    # make sure that that we get a '0' exit code for the testsuite
    assert result.ret == 0


def test_pytest_baseline_parametrized_module_variable_info(testdir: Pytester):

    testdir.makeconftest(
        """
        def pytest_baseline_parametrized_module_variable_info(
            module_variable_info
        ):
            module_variable_info.append(("paramed_var", []))
        """
    )
    # create a temporary pytest test module
    testdir.makepyfile("""

        paramed_var_data = ["hello", "world"]

        def test_paramed_var(paramed_var_value):
            assert paramed_var_value in paramed_var_data
    """)

    # run pytest with the following cmd args
    result = testdir.runpytest("-v")

    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines([
        '*::test_paramed_var*hello*PASSED*',
        '*::test_paramed_var*world*PASSED*',
    ])

    # make sure that that we get a '0' exit code for the testsuite
    assert result.ret == 0


def test_pytest_baseline_parametrized_module_variable_info_string(
    testdir: Pytester
):

    testdir.makeconftest(
        """
        def pytest_baseline_parametrized_module_variable_info(
            module_variable_info
        ):
            module_variable_info.append(("paramed_var", []))
        """
    )
    # create a temporary pytest test module
    testdir.makepyfile("""

        paramed_var_data = "hello world"

        def test_paramed_var(paramed_var_value):
            assert paramed_var_value in paramed_var_data
    """)

    # run pytest with the following cmd args
    result = testdir.runpytest("-v")

    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines([
        '*::test_paramed_var*hello world*PASSED*',
    ])

    # make sure that that we get a '0' exit code for the testsuite
    assert result.ret == 0


def test_pytest_baseline_parametrized_module_variable_info_skipped(
    testdir: Pytester
):

    testdir.makeconftest(
        """
        def pytest_baseline_parametrized_module_variable_info(
            module_variable_info
        ):
            module_variable_info.append(("paramed_var", []))
        """
    )
    # create a temporary pytest test module
    testdir.makepyfile("""
        def test_paramed_var(paramed_var_value):
            assert paramed_var_value in paramed_var_data
    """)

    # run pytest with the following cmd args
    result = testdir.runpytest("-v")

    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines([
        "*::test_paramed_var*Not Configured*SKIPPED*"
    ])

    # make sure that that we get a '0' exit code for the testsuite
    assert result.ret == 0


def test_pytest_baseline_parametrized_module_variable_info_id_func(
    testdir: Pytester
):

    testdir.makeconftest(
        """
        def pytest_baseline_parametrized_module_variable_info(
            module_variable_info
        ):
            module_variable_info.append(
                ("paramed_var", [], lambda x: x.upper())
            )
        """
    )
    # create a temporary pytest test module
    testdir.makepyfile("""

        paramed_var_data = ["hello", "world"]

        def test_paramed_var(paramed_var_value):
            assert paramed_var_value in paramed_var_data
    """)

    # run pytest with the following cmd args
    result = testdir.runpytest("-v")

    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines([
        '*::test_paramed_var*HELLO*PASSED*',
        '*::test_paramed_var*WORLD*PASSED*',
    ])

    # make sure that that we get a '0' exit code for the testsuite
    assert result.ret == 0


def test_skipping_tests(testdir: Pytester):

    # create a temporary pytest test module
    testdir.makepyfile("""

        def test_marker():
            assert True

        skip_tests = ["test_marker"]
    """)

    # run pytest with the following cmd args
    result = testdir.runpytest("-v")

    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines([
        "*collected 1 item*",
        '*::test_marker SKIPPED (Marked in Module)*',
        '*= 1 skipped in*',
    ])

    # make sure that that we get a '0' exit code for the testsuite
    assert result.ret == 0


def test_skipping_tests_custom_reason(testdir: Pytester):

    # create a temporary pytest test module
    testdir.makepyfile("""

        def test_marker():
            assert True

        skip_tests = [("test_marker", "Because")]
    """)

    # run pytest with the following cmd args
    result = testdir.runpytest("-v")

    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines([
        "*collected 1 item*",
        '*::test_marker SKIPPED (Because)*',
        '*= 1 skipped in*',
    ])

    # make sure that that we get a '0' exit code for the testsuite
    assert result.ret == 0


def test_xfailing_tests(testdir: Pytester):

    # create a temporary pytest test module
    testdir.makepyfile("""

        def test_marker():
            assert False

        xfail_tests = ["test_marker"]
    """)

    # run pytest with the following cmd args
    result = testdir.runpytest("-v")

    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines([
        "*collected 1 item*",
        '*::test_marker XFAIL (Marked in Module)*',
        '*= 1 xfailed in*',
    ])

    # make sure that that we get a '0' exit code for the testsuite
    assert result.ret == 0


def test_xfailing_tests_custom_reason(testdir: Pytester):

    # create a temporary pytest test module
    testdir.makepyfile("""

        def test_marker():
            assert False

        xfail_tests = [("test_marker", "Because")]
    """)

    # run pytest with the following cmd args
    result = testdir.runpytest("-v")

    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines([
        "*collected 1 item*",
        '*::test_marker XFAIL (Because)*',
        '*= 1 xfailed in*',
    ])

    # make sure that that we get a '0' exit code for the testsuite
    assert result.ret == 0


def test_xfailing_tests_custom_exception(testdir: Pytester):

    # create a temporary pytest test module
    testdir.makepyfile("""

        def test_marker():
            1/0

        xfail_tests = [("test_marker", "Because", ZeroDivisionError)]
    """)

    # run pytest with the following cmd args
    result = testdir.runpytest("-v")

    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines([
        "*collected 1 item*",
        '*::test_marker XFAIL (Because)*',
        '*= 1 xfailed in*',
    ])

    # make sure that that we get a '0' exit code for the testsuite
    assert result.ret == 0


def test_xfailing_tests_custom_exception_xpass(testdir: Pytester):

    # create a temporary pytest test module
    testdir.makepyfile("""

        def test_marker():
            assert False

        xfail_tests = [("test_marker", "Because", ZeroDivisionError)]
    """)

    # run pytest with the following cmd args
    result = testdir.runpytest("-v")

    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines([
        "*collected 1 item*",
        '*::test_marker FAILED*',
        "*: AssertionError*",
        '*= 1 failed in*',
    ])

    # make sure that that we get a '1' exit code for the testsuite, because
    # it should fail
    assert result.ret == 1


def test_marking_with_custom_marker(testdir: Pytester):

    # Define a custom marker
    testdir.makeconftest(
        """
        def pytest_configure(config):
            config.addinivalue_line(
                "markers", "tt2: mark tests to run for only Tiger Team 2 Views"
            )
        """
    )

    # create a temporary pytest test module
    testdir.makepyfile("""

        def test_marker(request):
            assert "tt2" in request.keywords

        tt2_tests = ["test_marker"]
    """)

    # run pytest with the following cmd args
    result = testdir.runpytest("-v")

    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines([
        "*collected 1 item*",
        '*::test_marker PASSED*',
        '*= 1 passed in*',
    ])

    # make sure that that we get a '0' exit code for the testsuite
    assert result.ret == 0


def test_incorrect_marking_raises_warning(testdir: Pytester):

    # Define a custom marker
    testdir.makeconftest(
        """
        def pytest_configure(config):
            config.addinivalue_line(
                "markers", "tt2: mark tests to run for only Tiger Team 2 Views"
            )
        """
    )

    # create a temporary pytest test module
    testdir.makepyfile("""

        def test_marker_warning(request):
            assert "tt2" not in request.keywords

        tt2_tests = ["test_marker"]
        xfail_tests = ["test_marker"]
        skip_tests = ["test_marker"]
    """)

    # run pytest with the following cmd args
    result = testdir.runpytest("-v")

    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines_random([
        "*collected 1 item*",
        '*::test_marker_warning PASSED*',
        '*= 1 passed, 3 warnings in*',
        "*UserWarning: Configured to be marked with 'skip'*",
        "*UserWarning: Configured to be marked with 'tt2'*",
        "*UserWarning: Configured to be marked with 'xfail'*"
    ])

    # make sure that that we get a '0' exit code for the testsuite
    assert result.ret == 0


def test_skipping_tests_env_dependant(testdir: Pytester):
    """Ensure marked tests with `{MARKER}_tests_{ENV}` module variable are
    marked correctly based on value passed via `--env` option
    """

    # create a temporary pytest test module
    testdir.makepyfile("""

        def test_marker():
            assert True

        skip_tests_someenv = [("test_marker", "Because")]
    """)

    # run pytest with the following cmd args
    result = testdir.runpytest("-v", "--env=someEnv")

    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines([
        "*collected 1 item*",
        '*::test_marker SKIPPED (Because)*',
        '*= 1 skipped in*',
    ])

    # make sure that that we get a '0' exit code for the testsuite
    assert result.ret == 0


def test_skipping_tests_with_env_option(testdir: Pytester):
    """Ensure tests that are marked with `env` marker are properly skipped if
    value passed via `--env` option matches marked value
"""

    # create a temporary pytest test module
    testdir.makepyfile("""
        import pytest
        @pytest.mark.env("dev")
        def test_dev_only(env):
            assert env == "dev"

        @pytest.mark.env("stage")
        def test_stage_only(env):
            assert env == "stage"

        @pytest.mark.env("dev", "stage")
        def test_dev_or_stage(env):
            assert env == "dev" or env == "stage"
    """)

    # run pytest with the following cmd args
    result = testdir.runpytest("-v", "--env=dev", "-ra")

    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines([
        "*collected 3 items*",
        "*::test_dev_only PASSED*",
        "*::test_stage_only SKIPPED (*",
        "*test requires env in*'stage'*",
        "*= 2 passed, 1 skipped in*",
    ])

    # make sure that that we get a '0' exit code for the testsuite
    assert result.ret == 0


def test_pytest_baseline_client_logo(testdir: Pytester):
    """Ensure that the pytest_baseline_client_logo hook will put the logo
    in the header
    """

    # call the custom hook
    testdir.makeconftest(
        """
        def pytest_baseline_client_logo() -> str:
            return "Keith's Totally Awesome Plugin"
        """
    )

    # create a temporary pytest test module
    testdir.makepyfile("""

        def test_marker():
            assert True
    """)

    # run pytest with the following cmd args
    result = testdir.runpytest("-v")

    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines([
        "*Keith's Totally Awesome Plugin*"
    ])

    # make sure that that we get a '0' exit code for the testsuite
    assert result.ret == 0


def test_module_variable_fixture(testdir: Pytester):
    """Ensure that the `module_variable` fixture pulls the module variable
    correctly
    """

    # Create a test class file that has no knowledge of the test file
    testdir.makepyfile(some_class="""

        class TestSomething:
            def test_hello(self, module_variable):
                assert module_variable("some_var") == "hello world"
    """, __init__="")

    # Create test file that imports above created test class
    testdir.makepyfile("""
        from .some_class import TestSomething

        some_var = "hello world"
        some_var_dev = "guten tag"
    """)

    # run pytest with the following cmd args
    result = testdir.runpytest("-v", "-ra")

    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines([
        "*collected 1 item*",
        "*TestSomething::test_hello PASSED*",
        "*= 1 passed in*"
    ])

    # make sure that that we get a '0' exit code for the testsuite
    assert result.ret == 0


def test_module_variable_fixture_skip_if_not_defined(testdir: Pytester):
    """Ensure that the `module_variable` fixture pulls the module variable
    correctly and skips test if not defined.
    """

    # Create a test class file that has no knowledge of the test file
    testdir.makepyfile(some_class="""

        class TestSomething:
            def test_hello(self, module_variable):
                assert module_variable(
                    "some_var",
                    skip_if_not_defined=True
                ) == "hello world"
    """, __init__="")

    # Create test file that imports above created test class
    testdir.makepyfile("""
        from .some_class import TestSomething
    """)

    # run pytest with the following cmd args
    result = testdir.runpytest("-v", "-ra")

    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines([
        "*collected 1 item*",
        "*TestSomething::test_hello SKIPPED*",
        "*some_var*not defined for*test_module_variable_"
        "fixture_skip_if_not_defined*",
        "*= 1 skipped in*"
    ])

    # make sure that that we get a '0' exit code for the testsuite
    assert result.ret == 0


def test_module_variable_fixture_env_dependant(testdir: Pytester):
    """Ensure that the `module_variable` fixture pulls the module variable
    correctly based on the value passed via `--env` option
    """

    # Create a test class file that has no knowledge of the test file
    testdir.makepyfile(some_class="""

        class TestSomething:
            def test_hello(self, module_variable):
                assert module_variable("some_var") == "guten tag"
    """, __init__="")

    # Create test file that imports above created test class
    testdir.makepyfile("""
        from .some_class import TestSomething

        some_var = "hello world"
        some_var_dev = "guten tag"
    """)

    # run pytest with the following cmd args
    result = testdir.runpytest("-v", "-ra", "--env=dev")

    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines([
        "*collected 1 item*",
        "*TestSomething::test_hello PASSED*",
        "*= 1 passed in*"
    ])

    # make sure that that we get a '0' exit code for the testsuite
    assert result.ret == 0
