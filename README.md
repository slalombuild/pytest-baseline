[![Pytest_logo](https://github.com/user-attachments/assets/a7102128-2300-4b4f-a829-62efe3d28668) + ![Pytest_logo](https://github.com/user-attachments/assets/a7102128-2300-4b4f-a829-62efe3d28668)]
# pytest-baseline


Pytest Plugin to help develop and manage highly repeatable tests by leveraging common test classes and functions.

## Feature Overview
--------

* Configuration driven common tests for highly repeatable tests.
* Expansions on the pytest-html pytest plugin
* Helpful printing methods for generating table outputs, comparisons and other formatted output

## Installation
------------

* In the future this package will be available on pypi, however this repo must be publically available first.
* How to copy and install local
    - Clone This Repo to your local machine
    - In your project's virtual environment run:
    ````
    pip install {PATH_TO_CLONED REPO}
    ````


## Basic Usage
-----
Below is an example of the core feature of `pytest-baseline`.  The writing of highly repeatable tests often contains lots of challenges for test writers.  This example demostrates a simple database table validation test suite.  Running the same set of tests over several different tables with many different possible configurations.

### Assumptions:

* The tests being written are for higher level than unit tests, example API, Integration, Data Transformation.  And that these tests are being run against some type of deployed environment.

* The SQL Query, `SELECT * FROM DEV.BASIC_INFO` produces the following pandas dataframe:

    | ID | First  |   Last   | Age |    City     |   State    | Favorite_Color |
    |----|--------|----------|-----|-------------|------------|----------------|
    | 1  |  John  |   Doe    | 27  |  New York   |  New York  |      Red       |
    | 2  |  Jane  |   Doe    | 28  | Jersey City | New Jersey |     Purple     |
    | 3  | Nikola |  Tesla   | 86  |  Belgrade   |   Serbia   | Electric Blue  |
    | 4  |  Ada   | Lovelace | 36  |   London    |  England   |     Yellow     |
    | 5  | Keith  |  Knapp   | 39  |   Denver    |  Colorado  |      Blue      |

* There a 10s to 100s of tables that are under test, with varying acceptance criteria for each.

* Performing a query against the database could be slow and resource intensive.

* Tests are being written against a product that is actively being developed and is subject to change.

* That a fixture exists, `sql_con`, to query a database.


### Consider the following tests to be performed against the above dataframe:

1. Verify that the dataframe has a row count of 5
1. Verify that ID is unique
1. Verify that the dataframe has columns: ID, First, Last, Age, City, State, Favorite_Color
1. Verify that values in the Age column are an integer > 0

### Conventional Example of tests without `pytest-baseline`:

```python
# contents of test_basic_info.py
import pytest
import postgress_connection
import pandas as pd

# @pytest.fixture(scope="session")
# def sql_con():
#     return postress_connection.connect(
#         database="phillips_local",
#         user="admin",
#         password="password"
#     )

@pytest.fixture(scope="module")
def df(sql_con):
    sql = "SELECT * FROM DEV.BASIC_INFO"
    # return sql_con.execute(sql)
    return pd.read_sql_query(sql=sql, con=sql_con)

def test_row_count(df):
    assert len(df.index) == 5

def test_id_is_unique(df):
    assert df["ID"].is_unique

@pytest.mark.parametrize(
    "column_name",
    ["ID", "First", "Last", "Age", "City", "State", "Favorite_Color"]
)
def test_column_exists(df, column_name):
    assert column_name in df.columns

def test_column_value_greater_than_zero(df):
    assert (df["Age"] > 0).all()
```

#### Running the above gives you:

```bash
$ pytest test_basic_info.py -v
=========================================== test session starts ============================================
platform darwin -- Python 3.x.y, pytest-7.x.y, py-1.x.y, pluggy-1.x.y
cachedir: .pytest_cache
rootdir: $REGENDOC_TMPDIR
collected 10 items

test_basic_info.py::test_row_count PASSED                                                            [ 10%]
test_basic_info.py::test_id_is_unique PASSED                                                         [ 20%]
test_basic_info.py::test_column_exists[ID] PASSED                                                    [ 30%]
test_basic_info.py::test_column_exists[First] PASSED                                                 [ 40%]
test_basic_info.py::test_column_exists[Last] PASSED                                                  [ 50%]
test_basic_info.py::test_column_exists[Age] PASSED                                                   [ 60%]
test_basic_info.py::test_column_exists[City] PASSED                                                  [ 70%]
test_basic_info.py::test_column_exists[State] PASSED                                                 [ 80%]
test_basic_info.py::test_column_exists[Favorite_Color] PASSED                                        [ 90%]
test_basic_info.py::test_column_value_greater_than_zero PASSED                                       [100%]

============================================ 10 passed in 0.34s ============================================
```

#### Problems with above approach:
1. To add another table to test the above would need to be copied and the values modified appropriately.  Adding one more table wouldn't me an issue but 50 more would be.
1. If an additional test needed to be added it would need to be added to every file to test.  Likewise with a modification to an existing test.
1. If there is different acceptance criteria for different environments then multiple test files may need to be created and skipped or not included in the test run or another mechanism would need to be implemented.
1. If more than a few tests would be needed for each table it becomes challenging to maintain.
1. Copy and Paste of code can be messy and dangerous practice.

This plugin attempts to solve all of the above concerns.

### Example with `pytest-baseline` (NOTE: There are several files):

```python
# contents of common_table_tests.py
class TestCommonTable:
    def test_row_count(_, df, module_variable):
        assert len(df.index) == module_variable("expected_row_count")

    def test_id_is_unique(_, df, unique_columns_value):
        assert df[unique_columns_value].is_unique

    def test_column_exists(_, df, columns_must_exist_value):
        assert columns_must_exist_value in df.columns

    def test_age_greater_than_zero(
        _,
        df,
        column_value_greater_than_zero_value
    ):
        assert (
            df[column_value_greater_than_zero_value] > 0
        ).all()
```
Moving tests into a common test class allows any test file to import them, reducing code copying.  This will also allow the tests to be more robust and informative since there is only one place that the tests are defined.  Another advantage is that if a test needs to be added it will be added to all test files that import the class without any additional modification (unless configuration is required for the test).  This does however require that the context of the test file that is importing the class needs to be available, note the `module_variable`, `unique_columns_value`, `columns_must_exist_value`, and `column_value_greater_than_zero_value` fixtures.  These fixtures will be discussed below.

```python
# contents of conftest.py
import pytest
import pandas as pd
import postgress_connection

@pytest.fixture(scope="session")
def sql_con():
    return postress_connection.connect(
        database="phillips_local",
        user="admin",
        password="password"
    )

@pytest.fixture(scope="module")
def df(sql_con, module_variable):
    db_name = module_variable("database_name", "DEV")
    tbl_name = module_variable("table_name")
    sql = f"SELECT * FROM {db_name}.{tbl_name}"
    # return sql_con.execute(sql)
    return pd.read_sql_query(sql=sql, con=sql_con)

def pytest_baseline_parametrized_module_variable_info(module_variable_info):
    module_variable_info.append(("columns_must_exist", []))
    module_variable_info.append(("unique_columns", []))
    module_variable_info.append(("column_value_greater_than_zero", []))
```
Moving the `df` fixture up to the conftest will allow it to be accessed by all tests below it, again note the `module_variable` fixture.  Next notice the `pytest_baseline_parametrized_module_variable_info` hook that is defined.  This is a hook that is provided by `pytest-baseline` and will be discussed further below, however take note of the names in each line `columns_must_exist`, `unique_columns`, and `column_value_greater_than_zero`.

```python
# contents of test_basic_info_plugin.py
# Import the Common Test Class, this imports all the
# tests contained in the class
from .common_table_tests import TestCommonTable

# Define information needed to obtain dataframe
database_name_stage = "STG"
table_name = "BASIC_INFO"

# Define test acceptance criteria
expected_row_count = 5
expected_row_count_stage = 4
columns_must_exist_data = [
    "ID",
    "First",
    "Last",
    "Age",
    "City",
    "State",
    "Favorite_Color"
]
unique_columns_data = ["ID"]
column_value_greater_than_zero_data = ["Age"]
```
The test file shows the configuration for the common tests, note that there is `database_name_stage` and no `database_name`, and `expected_row_count` and `expected_row_count_stage`.  These are for environment dependent configuration which can be passed with `--env` command line argument that is registered by `pytest-baseline`, this will be addressed more in detail below.

#### Running the above gives you:

```bash
% pytest test_basic_info_plugin.py -v
=========================================== test session starts ============================================
platform darwin -- Python 3.x.y, pytest-7.x.y, py-1.x.y, pluggy-1.x.y
cachedir: .pytest_cache
metadata: {'Python': '3.x.y', 'Packages': {'pytest': '7.x.y', 'py': '1.x.y', 'pluggy': '1.x.y'}, 'Plugins': {'html': '3.x.y', 'metadata': '2.x.y', 'baseline': '0.1.0'}, 'Environment': 'DEFAULT', 'Invoking Command': 'pytest test_basic_info_plugin.py -v', 'Start Time': '2023-01-05T18:07:39'}
rootdir: $REGENDOC_TMPDIR
plugins: html-3.2.0, metadata-2.0.2, baseline-0.1.0
collected 10 items

test_basic_info_plugin.py::TestCommonTable::test_row_count PASSED                                    [ 10%]
test_basic_info_plugin.py::TestCommonTable::test_id_is_unique[ID] PASSED                             [ 20%]
test_basic_info_plugin.py::TestCommonTable::test_column_exists[ID] PASSED                            [ 30%]
test_basic_info_plugin.py::TestCommonTable::test_column_exists[First] PASSED                         [ 40%]
test_basic_info_plugin.py::TestCommonTable::test_column_exists[Last] PASSED                          [ 50%]
test_basic_info_plugin.py::TestCommonTable::test_column_exists[Age] PASSED                           [ 60%]
test_basic_info_plugin.py::TestCommonTable::test_column_exists[City] PASSED                          [ 70%]
test_basic_info_plugin.py::TestCommonTable::test_column_exists[State] PASSED                         [ 80%]
test_basic_info_plugin.py::TestCommonTable::test_column_exists[Favorite_Color] PASSED                [ 90%]
test_basic_info_plugin.py::TestCommonTable::test_column_value_greater_than_zero[Age] PASSED          [100%]

============================================ 10 passed in 0.76s ============================================
```
#### The same number of tests were collected and executed even though the output is slightly different:
* There is more output at the beginning of the test run
* `test_id_is_unique` and `test_column_value_greater_than_zero` are now parametrized.
* The test names now contain `TestCommonTable`.

#### As promised let's discuss some of what is happening:

* The `module_variable` fixture:
    This is a fixture that is provided by `pytest-baseline` and is a function that contains the context of the module.  This function is used to obtain the value of module variables.  A default can be supplied so that the module variable does not always need to be defined. The function is also aware of the value passed by the `--env` command line argument.  Notice how the `df` fixture calls the function twice once for the `database_name` (with a default of "DEV") and a second time for the `table_name`.  It then uses these to construct the query for the database.  Also the test `TestCommonTable.test_row_count` uses it to get the expected count which has both a "default" (no `_{DEV_NAME}`) and "_stage" values defined separately.  So if `--env=stage` is passed the `expected_row_count_stage` value would be returned.  More about what this fixture can do can be found HERE.
* The `pytest_baseline_parametrized_module_variable_info` hook:
    This is a hook that is registered by `pytest-baseline` and is called when the tests are collected. By defining the hook and appending tuples to the list that is passed to the hook enables tests to be parametrized based on the names added.  To avoid confusion with module variables that are intended for the `module_variable` fixture a naming convention is implemented.  The first item in the tuple appended in the hook is the `BASE_VARIABLE_NAME`, the plugin then looks for tests that request a fixture named `{BASE_VARIABLE_NAME}_value` and parametrized the fixture with the module variable named `{BASE_VARIABLE_NAME}_data`.  The second argument in the tuple appended in the hook is the default value incase it is not defined in the module, if the module variable is not defined or is an empty iterable then the test will be skipped since there would be no information to provide to the test.  This is why `test_id_is_unique` and `test_column_value_greater_than_zero` are now parametrized.  This would allow multiple columns to be tested for uniquness or values greater than zero.  While this example did not leverage this, the module variables are also environment dependent (`unique_columns_data_stage` for example). More about what this hook can do can be found HERE.

#### What problems have been fixed:
1. The amount of code for each table that would need to be tested is drastically reduced to only the configuration that is needed, adding additional tables to test would be quick and very easy.
1. If a test needs to be updated there is a single place to do this, no more find and replace or copy pasta.  Putting the tests into classes means that a test can be added to all files that import that class without the need to update each test file (unless of course additional configuration is required for the test)
1. Test configuration can now be more environment aware, removing the needed for duplicate tests or some other solution to be provided.
1. Now that the tests live outside the test files and are only in one location they can be more robust and exhaustive with better messaging and commenting to describe the behavior
1. As noted several times, copying and pasting of code is greatly reduced.

#### There are of course some potential concerns with this approach:
1. With test code being imported instead of in the test file troubleshooting can become more of a challenge.  Always executing the tests with the `-v` flag can help to resolve this as it prints out the entire file path, test class, and test name for each test instead of just a `.`/`F`/`S`.
1. Since each test is expected to work with each test file configuration it is imported into there can be tests or test classes that are very similar due to slight differences in functionality.  However since the code only needs to be written once it can be more complex to handle these scenarios.
1. Sometimes a test needs to be skipped or xfailed or marked in some way, with the tests living outside the test file this would not normally be possible for pytest alone however `pytest-baseline` does provide a mechanism for this and is described HERE
1. The learning curve to understand the tests can be steep.  This is true, fully understanding this plugin and what it can do does require a very strong understanding of pytest and how it works.  However good naming conventions and helpful comment along with this documentation should help to alivate a lot of that burden.

**PLEASE NOTE:** While the above example is a demostration of the core feature of `pytest-baseline` there is still a lot of functionality that is provided, see below for full details.


## Advanced Features
-----
### Displaying a Client LOGO at start of output:

A logo can be added to the initial pytest printout by defining the `pytest_baseline_client_logo` hook and returning a string or an object that will return a string when `str()` is called on it.

```python
def pytest_baseline_client_logo():
    return """
        This is a placeholder for the LOGO
    """
```

### Registering Fixtures to be attached to pytest-html Report:

A fixture can be registered to be attached to the HTML report, when `--html={PATH}` is passed when invoking pytest.  This feature is intended to help simplify test writting by automatically including the "output" value of a fixture.  Take for example a fixture that returns a random number:

```python
@pytest.fixture
def random_number():
    return rand_int(0, 1000000)
```

Registering the fixture to be attached is done by the type of the object that is returned by the fixture.  In this case `int` therefor registering is as simple as:

```python
# Conents of conftest.py
def pytest_baseline_fixtures_add_to_report(fixtures_extra_config):
    fixtures_extra_config.add_fixture_extra_config(type=int)
```

This will produce an HTML report that includes an extra that has a string value that is the value of the random number.

The above object returns `int` which return something meaningful when `str()` is called on it. However not every object does that, for more complex objects for example a JSON (specific dict structure) would print all on one line and would be difficult to read and understand.  For this a print_function can be defined:

```python
# Conents of conftest.py
from json import dumps

# by wrapping json.dumps allows indent to be set
def json_dumps_wrapper():
    def wrapped(fixture_value, *args, **kwargs):
        return json.dumps(fixture_value, indent=4)
    return wrapped

def pytest_baseline_fixtures_add_to_report(fixtures_extra_config):
    fixtures_extra_config.add_fixture_extra_config(
        type=dict,
        print_func=json_dumps_wrapper()
    )
```

The above would generate a pretty print version of a json like dictionary, however if the dict cannot be Decoded correctly, ie throws a `json.JSONDecodeError`, then it will cause the test suite to fail.  This is where the `filter_func` parameter could be useful.

```python
# Conents of conftest.py
from json import dumps, JSONDecodeError

# by wrapping json.dumps allows indent to be set
def json_dumps_wrapper():
    def wrapped(fixture_value, *args, **kwargs):
        return json.dumps(fixture_value, indent=4)
    return wrapped

def check_valid_json(fixture_value, *args, **kwargs):
    try:
        json.dumps(fixture_value)
        return True
    except JSONDecodeError:
        return False

def pytest_baseline_fixtures_add_to_report(fixtures_extra_config):
    fixtures_extra_config.add_fixture_extra_config(
        type=dict,
        print_func=json_dumps_wrapper(),
        filter_func=check_valid_json
    )
```

Other configurations for this feature:

* `search_dict`: Check the values of a fixture that returns a dict.
* `html_extra_type`: pytest-html extra type to include on report, defaults to `extras.text` other possible types are: extra, html, image, jpg, json, mp4, png, svg, text, url, video

### Talk about assert rewrite for common test files

`pytest.register_assert_rewrite("plugin_tests.common_table_tests")`

### Built-in Available Fixtures:

#### `timer`

The time fixtures returns a function scoped `LapWatch` object.  The `LapWatch` object is like a stopwatch where "laps" can be recorded to help with determining what parts of tests are taking the most time, example:

```python
def test_multi_step_thing(timer):
    timer.start()
    timer.lap("start test")
    # Do something that takes some time
    timer.lap("step 1")
    # Do something else that takes some time
    timer.lap("step 2")
    # Do one more thing and assert stuff
    timer.lap("end test")
```

There is no need to print the value of the laps if a HTML report is being generated as this fixture type is already reqistered to be included in the report.

#### `env`

Returns the value of the command line option `--env`, default is `DEFAULT`

#### `module_variable`

Discussed above in [Basic Usage](#Basic-Usage), return `request` scoped function with following parameters:
* name: str - Name of Variable to search for, will return environment specific if available
* default: Any[None] - Default value if Variable is not found.
* skip_if_not_defined: bool[False] - Boolean to skip the requested test if the variable is not defined


## Contributing
------------
Contributions are very welcome. Tests can be run with `tox`, please ensure
the coverage at least stays the same before you submit a pull request.

## License
-------

Distributed under the terms of the _MIT_ license, "pytest-baseline" is free and open source software


## Issues
------

If you encounter any problems, please _file an issue_ along with a detailed description.

## Slalom Build
------

This plugin was developed in house at Slalom Build.

Interested in joining the team checkout our Careers [page](https://www.slalombuild.com/en-gb/careers)

Check us out on Social Media

* [LinkedIn](https://www.linkedin.com/company/slalom-build)
* [Instagram](https://www.instagram.com/slalombuild/)
* [Threads](https://www.threads.net/@slalombuild)
* [X](https://twitter.com/slalombuild)

## Tools
------

This repo was built with the help of the following tools:

- `Cookiecutter`: https://github.com/audreyr/cookiecutter
- `@hackebrot`: https://github.com/hackebrot
- `MIT`: http://opensource.org/licenses/MIT
- `BSD-3`: http://opensource.org/licenses/BSD-3-Clause
- `GNU GPL v3.0`: http://www.gnu.org/licenses/gpl-3.0.txt
- `Apache Software License 2.0`: http://www.apache.org/licenses/LICENSE-2.0
- `cookiecutter-pytest-plugin`: https://github.com/pytest-dev/cookiecutter-pytest-plugin
- `file an issue`: https://github.com/knappkeith/pytest-baseline/issues
- `pytest`: https://github.com/pytest-dev/pytest
- `tox`: https://tox.readthedocs.io/en/latest/
- `pip`: https://pypi.org/project/pip/
- `PyPI`: https://pypi.org/project
