from datetime import datetime
from random import randint

import pytest

from pytest_baseline.helpers.printing import (block_center_str,
                                              center_dict_str,
                                              date_time_sentence_str,
                                              date_time_sentence_utc_str,
                                              date_time_str, date_time_utc_str,
                                              dir_str_of_object,
                                              ellipsis_print, generate_table,
                                              generate_table_iter, secs_to_str,
                                              today_stamp_utc,
                                              yesterday_datetime,
                                              yesterday_stamp_utc)
from types import GeneratorType

class ObjWithBadStrMagicMethod:
    def __str__(self):
        return None


class DirStrObj:
    class_attribute = "this is my class attribute"
    class_dict = {"this": "is", "a": "dict"}
    _private_attribute = "this is my private attribute"

    def __init__(self, add_bad_str=False):
        self.multi_line_attribute = (
            "This\nattribute\ncontains\nnewline\ncharacters"
        )
        if add_bad_str:
            self.bad_str = ObjWithBadStrMagicMethod()

    def _private_method(self):
        pass

    def public_method(self):
        pass

    @staticmethod
    def static_method():
        pass

    @classmethod
    def class_method():
        pass


def test_dir_str_of_object_default():
    """Ensure the default use of the function, private attributes and methods
    are return but magic methods are not, the keys and values are spaced to
    line up, fill_char is `.`, correct type is used for header
    """
    dir_str = dir_str_of_object(DirStrObj())
    print(dir_str)
    assert all([".__" not in x for x in dir_str.split("\n")])
    assert "._private_attribute" in dir_str
    assert dir_str.startswith("\n<class 'test_printing.DirStrObj'>:")
    centered_colon = [
        len(x.split(":")[0]) for x in dir_str.split("\n") if " : " in x
    ]
    assert len(set(centered_colon)) == 1


def test_dir_str_of_object_print_dbl_underscore():
    """Ensure `filter__` parameter is honored"""
    dir_str = dir_str_of_object(DirStrObj(), filter__=False)
    print(dir_str)
    assert ".__class__" in dir_str


def test_dir_str_of_object_print_dbl_underscore_no_single():
    """Ensure both `filter__` and `filter_` parameters are honored together
    correctly
    """
    dir_str = dir_str_of_object(DirStrObj(), filter_=True, filter__=False)
    print(dir_str)
    assert ".__class__" in dir_str
    assert "._private_attribute" not in dir_str


def test_dir_str_of_object_no_init():
    """Just a slight difference for the basic usage for an object that has not
    been initialized
    """
    dir_str = dir_str_of_object(DirStrObj)
    print(dir_str)
    assert ".multi_line_attribute :" not in dir_str
    assert dir_str.startswith("\n<class 'type'>:")


def test_dir_str_of_object_max_len():
    """Ensure that the max_len parameter is honored"""
    dir_str = dir_str_of_object(DirStrObj(), max_len=4)
    print(dir_str)
    trim_len = [
        len(x.split(" : ")[1]) for x in dir_str.split("\n") if " : " in x
    ]
    assert len(set(trim_len)) == 1
    assert trim_len[0] == 4


def test_dir_str_of_object_filter_keys():
    """Ensure that any keys passed in filter_keys do not appear in return"""
    dir_str = dir_str_of_object(DirStrObj(), filter_keys=["_private_method"])
    print(dir_str)
    assert "_private_method" not in dir_str


def test_dir_str_of_object_fill_char():
    """Ensures the fill_char parameter is used properly"""
    dir_str = dir_str_of_object(DirStrObj, fill_char="#")
    print(dir_str)
    assert all([x.startswith("#") for x in dir_str.split("\n") if " : " in x])


def test_dir_str_of_object_new_line():
    """Ensures that a new line in an attribute value is indented correctly"""
    dir_str = dir_str_of_object(DirStrObj())
    print(dir_str)
    assert ".multi_line_attribute : This" in dir_str.split("\n")
    assert "                        attribute" in dir_str.split("\n")


def test_dir_str_of_object_bad_str_magic_method():
    """Ensures that an object whose __str__ magic method doesn't return a
    string doesn't cause the function to fail
    """
    dir_str = dir_str_of_object(DirStrObj(add_bad_str=True))
    print(dir_str)
    assert (
        "..............bad_str : TypeError: None <class "
        "'test_printing.ObjWithBadStrMagicMethod'>" in dir_str
    )


@pytest.mark.parametrize(
    "input_str, input_len",
    [
        ("X" * 10, 6),
        ("X" * 10, 7),
        ("X" * 10, 8),
        ("X" * 10, 9)
    ]
)
def test_ellipsis_print_ellipsised(input_str, input_len):
    """Ensure a string is ellipsised correctly"""
    output = ellipsis_print(input_str, input_len)
    print(output)
    assert output[-3:] == "..."
    assert len(output) == input_len


@pytest.mark.parametrize(
    "input_str, input_len",
    [
        (None, 10),
        (DirStrObj(), 10),
        (None, None),
        ("X" * 10, None),
        ("X" * 10, 11),
        ("X" * 10, 10),
        ("X" * 10, 0)
    ]
)
def test_ellipsis_print_not_ellipsised(input_str, input_len):
    """Ensure that an ellipsis is not added when length is longer than the
    string, length is not an integer > 0, string is not a string
    """
    output = ellipsis_print(input_str, input_len)
    print(output)
    assert input_str == output
    if isinstance(output, str):
        assert output[-3:] != "..."


def test_center_dict_str_default():
    """Ensure Default behavior works, centered on delimiter and is string"""
    input = {
        "English": "Goodmorning",
        "Deutsch": ["Gutenmorgen", "Gutentag"],
        "Italiano": "Boungiorno"
    }
    output = center_dict_str(input)
    print(output)
    assert isinstance(output, str)
    centered_colon = [
        len(x.split(":")[0]) for x in output.split("\n") if " : " in x
    ]
    assert len(set(centered_colon)) == 1


def test_center_dict_str_non_printable():
    """Ensure a non printable value in the dict works correctly"""
    input = {
        "English": "Goodmorning",
        "Deutsch": ["Gutenmorgen", "Gutentag"],
        "Italiano": "Boungiorno",
        "Dutch": ObjWithBadStrMagicMethod()
    }
    output = center_dict_str(input)
    print(output)
    assert isinstance(output, str)
    centered_colon = [
        len(x.split(":")[0]) for x in output.split("\n") if " : " in x
    ]
    assert len(set(centered_colon)) == 1
    assert (
        "   Dutch : TypeError: "
        "None <class 'test_printing.ObjWithBadStrMagicMethod'>" in output
    )


def test_center_dict_str_leave_line():
    """Ensure that a line with a key that starts with `LEAVE_LINE_AS_IS` is
    left alone and printed as is
    """
    rand_str = "".join([str(randint(0,9)) for _ in range(randint(10, 100))])
    input = {
        "English": "Goodmorning",
        "LEAVE_LINE_AS_IS_A": rand_str,
        "Deutsch": ["Gutenmorgen", "Gutentag"],
        "Italiano": "Boungiorno",
        "LEAVE_LINE_AS_IS_B": rand_str,
    }
    output = center_dict_str(input)
    print(output)
    assert isinstance(output, str)
    assert rand_str in output.split("\n")


def test_center_dict_str_new_lines():
    """Ensure that values with a new line are indented correctly"""
    input = {
        "English": "Goodmorning",
        "Deutsch": "\n".join(["Gutenmorgen", "Gutentag", "Morgen"]),
        "Italiano": "Boungiorno",
    }
    output = center_dict_str(input)
    print(output)
    assert isinstance(output, str)
    assert "           Gutentag" in output


@pytest.mark.parametrize("delimiter", [":", " <-> "])
def test_center_dict_str_parameters_delimiter(delimiter):
    """Ensure that the delimiter can be changed and can be one or multiple
    characters
    """
    input = {
        "English": "Goodmorning",
        "Deutsch": "\n".join(["Gutenmorgen", "Gutentag", "Morgen"]),
        "Italiano": "Boungiorno",
    }
    output = center_dict_str(input, delimiter)
    print(output)
    assert isinstance(output, str)
    assert delimiter in output
    centered_colon = [
        len(x.split(delimiter)[0])
        for x in output.split("\n") if delimiter in x
    ]
    assert len(set(centered_colon)) == 1


def test_center_dict_str_parameters_fill():
    """Ensure that the fill parameter works correctly"""
    fill = "_"
    input = {
        "English": "Goodmorning",
        "Deutsch": "\n".join(["Gutenmorgen", "Gutentag", "Morgen"]),
        "Italiano": "Boungiorno",
        "Portuguese": "bom Dia"
    }
    output = center_dict_str(input, fill=fill)
    print(output)
    assert isinstance(output, str)
    assert "___Deutsch :" in output


def test_center_dict_str_parameters_indent():
    """Ensure that the indent length is always honored"""
    indent_len = randint(1, 20)
    input = {
        "English": "Goodmorning",
        "Deutsch": "\n".join(["Gutenmorgen", "Gutentag", "Morgen"]),
        "Italiano": "Boungiorno",
        "LEAVE_LINE_AS_IS_A": "- Other Countries -",
        "Portuguese": "bom Dia"
    }
    output = center_dict_str(input, indent_len=indent_len)
    print(output)
    assert isinstance(output, str)
    centered_colon = [
        len(x.split(":")[0]) for x in output.split("\n") if " : " in x
    ]
    assert len(set(centered_colon)) == 1
    assert all([x.startswith(" " * indent_len) for x in output.split("\n")])


def test_block_center_str_default():
    """Ensure default basic functionality works"""
    block_str = "\n".join([
        " English : Goodmorning",
        " Deutsch : Gutenmorgen",
        "           Gutentag",
        "           Morgen",
        "Italiano : Boungiorno"
    ])
    output = block_center_str(block_str, " : ")
    print(output)
    assert output == block_str


def test_block_center_str_passing_kwargs():
    """Ensure kwargs get passed along"""
    block_str = "\n".join([
        " English : Goodmorning",
        " Deutsch : Gutenmorgen",
        "           Gutentag",
        "           Morgen",
        "Italiano : Boungiorno"
    ])
    output = block_center_str(block_str, " : ", fill=".", indent_len=4)
    print(output)
    assert all([x.startswith("....") for x in output.split("\n")])


def test_block_center_str_recenter():
    """Ensure that the text is recentered correctly"""
    block_str = "\n".join([
        "English > Goodmorning",
        "Deutsch>Gutenmorgen",
        "Italiano> Boungiorno"
    ])
    output = block_center_str(block_str, ">")
    print(output)
    centered_colon = [
        len(x.split(":")[0]) for x in output.split("\n") if " : " in x
    ]
    assert len(set(centered_colon)) == 1
    assert all([" : " in x for x in output.split("\n")])


def test_block_center_str_multi():
    """Ensure if multiple delimiters show up data isn't lost"""
    block_str = "\n".join([
        "English > Goodmorning > helloworld",
        "Deutsch>Gutenmorgen",
        "Italiano> Boungiorno"
    ])
    output = block_center_str(block_str, ">")
    print(output)
    centered_colon = [
        len(x.split(":")[0]) for x in output.split("\n") if " : " in x
    ]
    assert len(set(centered_colon)) == 1
    assert all([" : " in x for x in output.split("\n")])
    assert "Goodmorning > helloworld" in output


@pytest.mark.parametrize("func", [
    date_time_sentence_utc_str,
    date_time_utc_str,
    date_time_sentence_str,
    date_time_str
])
def test_time_str_helper_functions(func):
    """Ensure time helper formatting functions return strings and UTC is
    present in utc functions
    """
    output = func()
    print(output)
    assert isinstance(output, str)
    if "utc" in func.__name__:
        assert "(UTC)" in output


@pytest.mark.parametrize("func", [today_stamp_utc, yesterday_stamp_utc])
@pytest.mark.parametrize("dashes", [True, False])
def test_time_stamp_helper_functions(func, dashes):
    """Ensure timestamp helper functions work as expected"""
    output = func(with_dashes=dashes)
    print(output)
    if dashes:
        assert "-" in output
        assert len(output) == 10
    else:
        assert int(output)
        assert len(output) == 8
    assert isinstance(output, str)


def test_yesterday_datetime():
    """Ensure yesterday datetime is returning a datetime"""
    output = yesterday_datetime()
    assert isinstance(output, datetime)


@pytest.mark.parametrize("input, expected", [
    (1, "1.000s"),
    (0.111, "0.111s"),
    (0.1111, "0.111s"),
    (0.1119, "0.112s"),
    (0.9999, "1.000s"),
    (10.9999, "11.000s"),
    (59.9999, "1m 00.000s"),
    (60, "1m 00.000s"),
    (36000, "10h 00m 00.000s"),
    (3599.9999, "1h 00m 00.000s"),
])
def test_secs_to_str(input, expected):
    """Ensure `secs_to_str` function rounds, parses and outputs correctly"""
    output = secs_to_str(input)
    print(output)
    assert output == expected


def test_generate_table():
    """Ensure that `generate_table` function passes everything on to
    `generate_table_iter` function
    """
    input_hdr = ["index", "A", "B"]
    input_data = [
        [0, "a", "b"],
        [1, True, "b"],
        [2, "a", True],
        [1, False, "b"],
        [2, "a", False],
    ]
    output = generate_table(input_hdr, input_data, True, 0, "<", True)
    print(output)
    assert "\n".join([
        "._______________________.",
        "| index |   A   |   B   |",
        "|-------+-------+-------|",
        "| 0     | a     | b     |",
        "| 1     | True  | b     |",
        "| 2     | a     | True  |",
        "| 1     | False | b     |",
        "| 2     | a     | False |",
        "|_______|_______|_______|"
    ]) == output


def test_generate_table_iter():
    input_hdr = ["index", "A", "B"]
    input_data = [
        [0, "a", "b"],
        [1, "y", "b"],
        [2, "a", "Y"],
        [1, "n", "b"],
        [3, "a", "This\nIs\nA\nMulti-line\nCell"],
        "break",
        [2, "a", "N"],
    ]
    output_iter = generate_table_iter(
        input_hdr,
        input_data,
        border=False,
        use_checks=True
    )
    assert isinstance(output_iter, GeneratorType)
    output = "\n".join(list(output_iter))
    print(output)
    assert "\n".join([
        "index | A |     B     ",
        "------+---+-----------",
        "  0   | a |     b     ",
        "  1   | ✓ |     b     ",
        "  2   | a |     ✓     ",
        "  1   | ✗ |     b     ",
        "  3   | a |    This   ",
        "      |   |     Is    ",
        "      |   |     A     ",
        "      |   | Multi-line",
        "      |   |    Cell   ",
        "------+---+-----------",
        "  2   | a |     ✗     "
    ]) == output


def test_generate_table_iter_jusification():
    input_hdr = ["index", "A", "B"]
    input_data = [
        [0, "hello", "b"],
        [1, "y", "b"],
        [2, "a", "Y"],
        [1, "n", "b"],
        [3, "a", "This\nIs\nA\nMulti-line\nCell"],
        "break",
        [2, "a", "N"],
    ]
    output_iter = generate_table_iter(
        input_hdr,
        input_data,
        border=True,
        use_checks=True,
        justification=">"
    )
    assert isinstance(output_iter, GeneratorType)
    output = "\n".join(list(output_iter))
    print(output)
    assert "\n".join([
        ".____________________________.",
        "| index |   A   |     B      |",
        "|-------+-------+------------|",
        "|     0 | hello |          b |",
        "|     1 |     ✓ |          b |",
        "|     2 |     a |          ✓ |",
        "|     1 |     ✗ |          b |",
        "|     3 |     a |       This |",
        "|       |       |         Is |",
        "|       |       |          A |",
        "|       |       | Multi-line |",
        "|       |       |       Cell |",
        "|-------+-------+------------|",
        "|     2 |     a |          ✗ |",
        "|_______|_______|____________|"
    ]) == output


def test_generate_table_iter_jusification_list():
    input_hdr = ["index", "A", "B"]
    input_data = [
        [0, "hello", "b"],
        [1, "y", "b"],
        [2, "a", "Y"],
        [1, "n", "b"],
        [3, "a", "This\nIs\nA\nMulti-line\nCell"],
        "break",
        [2, "a", "N"],
    ]
    output_iter = generate_table_iter(
        input_hdr,
        input_data,
        border=True,
        use_checks=True,
        justification=[">", "^", "<"],
        column_padding=2
    )
    assert isinstance(output_iter, GeneratorType)
    output = "\n".join(list(output_iter))
    print(output)
    assert "\n".join([
        ".__________________________________.",
        "|  index  |    A    |      B       |",
        "|---------+---------+--------------|",
        "|       0 |  hello  | b            |",
        "|       1 |    ✓    | b            |",
        "|       2 |    a    | ✓            |",
        "|       1 |    ✗    | b            |",
        "|       3 |    a    | This         |",
        "|         |         | Is           |",
        "|         |         | A            |",
        "|         |         | Multi-line   |",
        "|         |         | Cell         |",
        "|---------+---------+--------------|",
        "|       2 |    a    | ✗            |",
        "|_________|_________|______________|"
    ]) == output
