from typing import Tuple

from _pytest.pytester import RunResult
from pytest import Pytester


def run(
    testdir: Pytester,
    path: str = "report.html",
    *args
) -> Tuple[RunResult, str]:
    path = testdir.tmpdir.join(path)
    result = testdir.runpytest("--html", path, *args)
    new_path = get_new_report_path(result, testdir)
    try:
        read_file(new_path)
    except Exception:
        import os
        print(", ".join([x for x in os.listdir(testdir) if os.path.isfile(os.path.join(testdir, x))]))
        print("PROBLEM", result.stdout)

    return result, read_file(new_path)


def get_new_report_path(result, testdir):
    new_path = testdir.tmpdir.join(
        str(result.stdout).split(str(testdir.tmpdir))[-1].split(" ")[0]
    )
    return new_path


def read_file(path: str) -> str:
    with open(str(path)) as f:
        return f.read()


def test_html_report_created(testdir: Pytester):
    """Ensure that a HTML report is generated"""
    result, report = run(testdir, "report.html", "--fixtures", "-v")
    result.stdout.fnmatch_lines(["*Generated html report: file:*report.html*"])
    assert report is not None


def test_html_report_doc_string_column(testdir: Pytester):
    """Ensure that doc string for test is added to HTML Report"""
    doc_str_sep = '"""'
    doc_str = "This is my doc string for test_something function"
    testdir.makepyfile(
        f"""
        def test_something(request):
            {doc_str_sep}{doc_str}{doc_str_sep}
            assert True
        """
    )
    result, report = run(testdir, "report.html", "-v")
    assert f"{doc_str}" in report
    assert result.ret == 0


def test_html_report_extra_link_basic(testdir: Pytester):
    """Ensure that `pytest_baseline_fixtures_add_to_report` hook basic
    functionality works
    """

    # Write Conftest with `api_config` Fixture and
    # `pytest_baseline_fixtures_add_to_report` hook defined
    testdir.makeconftest(
        """
        import pytest

        @pytest.fixture(name="api_config", scope="session")
        def fixture_api_config():
            return {
                "base_url": "https://jsonplaceholder.typicode.com"
            }

        def pytest_baseline_fixtures_add_to_report(fixtures_extra_config):
            fixtures_extra_config.add_fixture_extra_config(dict)
        """
    )

    # Simple test that
    testdir.makepyfile(
        """
        def test_something(api_config):
            assert True
        """
    )

    # Run test, retrieve report and result
    result, report = run(testdir, "report.html", "-v")

    # Expected file path addition for created extra
    file_path = (
        "assets/test_html_report_extra_link_basic.py__test_something_0_0.txt"
    )

    # Ensure Report includes reference to created extra
    assert (
        fr'href=\&#34;{file_path}' in report
    )
    assert "&#34;&gt;api_config&" in report

    # Read Extra Created and verify correct contents
    extra_str = read_file(testdir.tmpdir.join(file_path))
    assert extra_str == "{'base_url': 'https://jsonplaceholder.typicode.com'}"

    # Make sure test didn't fail
    assert result.ret == 0


def test_html_report_extra_link_sub_dict(testdir: Pytester):
    """Ensure that `pytest_baseline_fixtures_add_to_report` hook
    functionality works with the sub dictionary feature enabled
    """

    # Write Conftest with `pytest_baseline_fixtures_add_to_report` hook
    # defined
    testdir.makeconftest(
        """
        def custom_filter(fixture_value, *args, **kwargs):
            return "DoNotIncudeKey" not in fixture_value.keys()

        def custom_print(fixture_value, *args, **kwargs):
            return ", ".join(
                [m.upper() for m in fixture_value.keys()]
            )

        def pytest_baseline_fixtures_add_to_report(fixtures_extra_config):
            fixtures_extra_config.add_fixture_extra_config(
                dict,
                True,
                custom_filter,
                custom_print
            )
        """
    )

    # fixture that returns a type that is a sub directory for the reporter
    testdir.makepyfile(
        """
        import pytest

        @pytest.fixture
        def fixture_extra():
            return {
                "DictKey1": {
                    "SubDictKey1.1": "SubDictValue1.1",
                    "SubDictKey1.2": "SubDictValue1.2"
                },
                "DictKey2": {
                    "SubDictKey2.1": "this shouldn't be there",
                    "DoNotIncudeKey": "this shouldn't be there"
                },
                "DictKey3": {
                    "SubDictKey3.1": "SubDictValue3.1",
                    "SubDictKey3.2": "SubDictValue3.2"
                }

            }

        def test_something(fixture_extra):
            pass
        """
    )

    # Run test, retrieve report and result
    result, report = run(testdir, "report.html", "-v")

    # Expected file path addition for created extra
    file_path = (
        "assets/"
        "test_html_report_extra_link_sub_dict.py__test_something_{}_0.txt"
    )
    file_path_1 = file_path.format("0")
    file_path_2 = file_path.format("1")
    file_path_3 = file_path.format("2")

    # Ensure Report includes reference to created extra
    assert (
        f'<td class="col-links"><a class="text" href="{file_path_1}"'
    )
    assert "&#34;&gt;fixture_extra&" in report
    assert (
        f'<td class="col-links"><a class="text" href="{file_path_2}"'
    )
    assert "&#34;&gt;DictKey1(fixture_extra)&" in report
    assert (
        f'<td class="col-links"><a class="text" href="{file_path_3}"'
    )
    assert "&#34;&gt;DictKey3(fixture_extra)&" in report
    assert "DictKey2(fixture_extra)" not in report

    # Read Extra Created and verify correct contents
    extra_str = read_file(testdir.tmpdir.join(file_path_1))
    assert extra_str == "DICTKEY1, DICTKEY2, DICTKEY3"
    extra_str = read_file(testdir.tmpdir.join(file_path_2))
    assert extra_str == "SUBDICTKEY1.1, SUBDICTKEY1.2"
    extra_str = read_file(testdir.tmpdir.join(file_path_3))
    assert extra_str == "SUBDICTKEY3.1, SUBDICTKEY3.2"

    # Make sure test didn't fail
    assert result.ret == 0


def test_html_report_extra_link_multiple(testdir: Pytester):
    """Ensure that `pytest_baseline_fixtures_add_to_report` hook
    functionality works with multiple different fixtures are used
    """

    # Write Conftest with `pytest_baseline_fixtures_add_to_report` hook
    # defined
    testdir.makeconftest(
        """
        import pytest

        @pytest.fixture(name="api_config", scope="session")
        def fixture_api_config():
            return {
                "base_url": "https://jsonplaceholder.typicode.com"
            }

        def custom_filter(fixture_value, *args, **kwargs):
            print(kwargs['fixture_name'])
            print(fixture_value.keys())
            return "DoNotIncudeKey" not in fixture_value.keys()

        def custom_print(fixture_value, *args, **kwargs):
            return ", ".join(
                [m.upper() for m in fixture_value.keys()]
            )

        def pytest_baseline_fixtures_add_to_report(fixtures_extra_config):
            fixtures_extra_config.add_fixture_extra_config(
                dict,
                True,
                custom_filter,
                custom_print
            )
        """
    )

    # fixture that returns a type that is a sub directory for the reporter
    testdir.makepyfile(
        """
        import pytest

        @pytest.fixture
        def fixture_extra():
            return {
                "DictKey1": {
                    "SubDictKey1.1": "SubDictValue1.1",
                    "SubDictKey1.2": "SubDictValue1.2"
                },
                "DictKey2": {
                    "SubDictKey2.1": "this shouldn't be there",
                    "DoNotIncudeKey": "this shouldn't be there"
                },
                "DictKey3": {
                    "SubDictKey3.1": "SubDictValue3.1",
                    "SubDictKey3.2": "SubDictValue3.2"
                }

            }

        def test_something(fixture_extra, api_config):
            pass
        """
    )

    # Run test, retrieve report and result
    result, report = run(testdir, "report.html", "-v")

    # Expected file path addition for created extra
    file_path = (
        "assets/"
        "test_html_report_extra_link_multiple.py__test_something_{}_0.txt"
    )
    file_path_1 = file_path.format("0")
    file_path_2 = file_path.format("1")
    file_path_3 = file_path.format("2")
    file_path_4 = file_path.format("3")

    # Ensure Report includes reference to created extra
    assert (
        f'<td class="col-links"><a class="text" href="{file_path_1}"'
    )
    assert "&#34;&gt;api_config&" in report
    assert (
        f'<td class="col-links"><a class="text" href="{file_path_2}"'
    )
    assert "&#34;&gt;fixture_extra&" in report
    assert "DictKey2(fixture_extra)" not in report

    assert (
        f'<td class="col-links"><a class="text" href="{file_path_3}"'
    )
    assert "&#34;&gt;DictKey1(fixture_extra)&" in report
    assert (
        f'<td class="col-links"><a class="text" href="{file_path_4}"'
    )
    assert "&#34;&gt;DictKey3(fixture_extra)&" in report
    assert "DictKey2(fixture_extra)" not in report

    # Read Extra Created and verify correct contents
    extra_str = read_file(testdir.tmpdir.join(file_path_1))
    assert extra_str == "BASE_URL"
    extra_str = read_file(testdir.tmpdir.join(file_path_2))
    assert extra_str == "DICTKEY1, DICTKEY2, DICTKEY3"
    extra_str = read_file(testdir.tmpdir.join(file_path_3))
    assert extra_str == "SUBDICTKEY1.1, SUBDICTKEY1.2"
    extra_str = read_file(testdir.tmpdir.join(file_path_4))
    assert extra_str == "SUBDICTKEY3.1, SUBDICTKEY3.2"

    # Make sure test didn't fail
    assert result.ret == 0


def test_html_report_extra_link_multiple_not_printed(testdir: Pytester):
    """Ensure that `pytest_baseline_fixtures_add_to_report` hook
    functionality works with simple text (not Dict) with other fixtures of
    different types
    """

    # Write Conftest with `pytest_baseline_fixtures_add_to_report` hook
    # defined
    testdir.makeconftest(
        """
        import pytest

        @pytest.fixture(name="api_config", scope="session")
        def fixture_api_config():
            return {
                "base_url": "https://jsonplaceholder.typicode.com"
            }

        def custom_filter(fixture_value, *args, **kwargs):
            print(kwargs['fixture_name'])
            print(fixture_value.keys())
            return "DoNotIncudeKey" not in fixture_value.keys()

        def custom_print(fixture_value, *args, **kwargs):
            return ", ".join(
                [m.upper() for m in fixture_value.keys()]
            )

        def pytest_baseline_fixtures_add_to_report(fixtures_extra_config):
            fixtures_extra_config.add_fixture_extra_config(str)
        """
    )

    # fixture that returns a type that is a sub directory for the reporter
    testdir.makepyfile(
        """
        import pytest

        @pytest.fixture
        def fixture_extra():
            return {
                "DictKey1": {
                    "SubDictKey1.1": "SubDictValue1.1",
                    "SubDictKey1.2": "SubDictValue1.2"
                },
                "DictKey2": {
                    "SubDictKey2.1": "this shouldn't be there",
                    "DoNotIncudeKey": "this shouldn't be there"
                },
                "DictKey3": {
                    "SubDictKey3.1": "SubDictValue3.1",
                    "SubDictKey3.2": "SubDictValue3.2"
                }

            }

        @pytest.fixture
        def fixture_text_only():
            return "This is my text string"

        def test_something(fixture_extra, api_config, fixture_text_only):
            pass
        """
    )

    # Run test, retrieve report and result
    result, report = run(testdir, "report.html", "-v")

    # Expected file path addition for created extra
    file_path = (
        "assets/"
        "test_html_report_extra_link_multiple_not_printed."
        "py__test_something_{}_0.txt"
    )
    file_path_1 = file_path.format("0")

    # Ensure Report includes reference to created extra
    assert (
        f'<td class="col-links"><a class="text" href="{file_path_1}"'
    )
    assert "&#34;&gt;fixture_text_only&" in report
    assert "&#34;&gt;api_config&" not in report

    # Read Extra Created and verify correct contents
    extra_str = read_file(testdir.tmpdir.join(file_path_1))
    assert extra_str == "This is my text string"

    # Make sure test didn't fail
    assert result.ret == 0


def test_html_report_environment(testdir: Pytester):
    """Ensure that title of HTML Report is modified with date and env, this
    also validates that the file name is modified
    """
    testdir.makepyfile(
        """
        def test_something():
            assert True
        """
    )
    env = "local"
    result, report = run(
        testdir,
        "report-{date}-{env}.html", "-v", f"--env={env}"
    )
    env_table = f"&#34;{env}&#34"
    assert env_table in report
    assert result.ret == 0
