
import datetime
import time
from inspect import cleandoc
from textwrap import indent
from typing import Any, Dict, List, Optional, Union


NL = "\n"


def dir_str_of_object(
    obj: Any,
    filter_: bool = False,
    filter__: bool = True,
    max_len: Optional[int] = 500,
    filter_keys: Optional[List[str]] = None,
    fill_char: str = "."
) -> str:
    """Returns a sting with joined properties of the passed object for printing
    Intended to be used to help see what is available in object, This should
    only be used as a tool to assist in troubleshooting
    """
    if filter_keys is None:
        filter_keys = []

    obj_dir = list(dir(obj))

    # Filter private methods, attributes that start with "_"
    if filter_:
        obj_dir = [
            x for x in obj_dir
            if not x.startswith("_") or x.startswith("__")]

    # Filter magic methods, attributes that start with "__"
    if filter__:
        obj_dir = [x for x in obj_dir if not x.startswith("__")]

    obj_dir = [x for x in obj_dir if x not in filter_keys]

    # Get label width
    hdr_w = max([len(x) for x in obj_dir]) + 1

    obj_dir = sorted(obj_dir)

    def new_lines(item: Any, ind_len: int) -> str:
        temp_rtn = str(item)
        if f"{NL}" in temp_rtn:
            return indent(temp_rtn, " " * ind_len)[ind_len:]
        return temp_rtn

    def get_str_attribute(obj, attr):
        attr_value = getattr(obj, attr)
        try:
            return str(attr_value)
        except TypeError:
            return f"TypeError: None {type(attr_value)}"

    # format and return string
    val_ind = hdr_w + 3
    attr_str = NL.join(
        [
            f"{x:{fill_char}>{hdr_w}} : "
            f"{new_lines(get_str_attribute(obj, x), val_ind)[0:max_len]}"
            for x in obj_dir if hasattr(obj, x)
        ]
    )
    return f"{NL}{type(obj)}:{NL}{attr_str}{NL}"


def center_dict_str(
    data: Dict[str, Any],
    delimiter: str = " : ",
    fill: str = " ",
    indent_len: int = 0,
    key_justification: str = ">"
) -> str:
    """Generates the string for a Dictionary centering on the delimiter between
    the Key and Value, Values whose __str__ method returns a string with `\n`
    will be indented to fit in Value column
    """
    def new_lines(item: Any, ind_len: int) -> str:
        temp_rtn = str(item)
        if f"{NL}" in temp_rtn:
            temp_rtn = cleandoc(temp_rtn)
            return indent(temp_rtn, " " * ind_len)[ind_len:]
        return temp_rtn

    def get_str_value(obj, key):
        key_value = obj.get(key)
        try:
            return str(key_value)
        except TypeError:
            return f"TypeError: None {type(key_value)}"

    if len(data.keys()) == 0:
        return ""

    hdr_w = max(
        [
            len(str(k)) for k in data.keys()
            if not k.startswith("LEAVE_LINE_AS_IS")
        ]
    )
    val_ind = hdr_w + len(delimiter) + indent_len
    ind_str = f"{'':{fill}^{indent_len}}"
    return NL.join(
        [
            f"{ind_str}{str(k):{fill}{key_justification}{hdr_w}}{delimiter}"
            f"{new_lines(get_str_value(data, k), val_ind)}"
            if not k.startswith("LEAVE_LINE_AS_IS")
            else f"{ind_str}{get_str_value(data, k)}"
            for k, v in data.items()
        ]
    )


def block_center_str(data: str, split_delimiter: str = ":", **kwargs):
    """Wrapper around `center_dict_str` to parse block text (separated by \\n)
    centers on `split_delimiter`.  `**kwargs` are passed to `center_dict_str`.
    If `split_delimiter` present more than once in a line only the first and
    second will be used if `split_delimiter` does not exist the line will be
    returned as is.
    """
    if split_delimiter is None or split_delimiter == "":
        raise RuntimeError(
            "`split_delimiter` must be a non empty string, passed: "
            f"`{split_delimiter}`"
        )
    data_dict = {}
    leave_cnt = 0
    for line in cleandoc(data).split("\n"):
        split_line = line.split(split_delimiter)
        if len(split_line) == 1:
            key = f"LEAVE_LINE_AS_IS_{leave_cnt}"
            value = split_line[0]
            leave_cnt += 1
        elif len(split_line) > 1:
            key = split_line[0]
            value = split_delimiter.join(split_line[1:])
        data_dict[key] = value
    return center_dict_str(data_dict, **kwargs)


def date_time_sentence_utc_str() -> str:
    """Returns current UTC date time stamp in the format:
        `on %d-%h-%Y at %H:%M:%S (UTC)`
    """
    return f"on {time.strftime('%d-%h-%Y at %H:%M:%S', time.gmtime())} (UTC)"


def date_time_utc_str() -> str:
    """Returns current UTC date time stamp in the format:
        `%d-%h-%Y %H:%M:%S (UTC)`
    """
    return f"{time.strftime('%d-%h-%Y %H:%M:%S', time.gmtime())} (UTC)"


def date_time_sentence_str() -> str:
    """Returns current date time stamp in the format:
        `on %d-%h-%Y at %H:%M:%S`
    """
    return f"on {time.strftime('%d-%h-%Y at %H:%M:%S')}"


def date_time_str() -> str:
    """Returns current date time stamp in the format: `%d-%h-%Y %H:%M:%S`
    """
    return f"{time.strftime('%d-%h-%Y %H:%M:%S')}"


def today_stamp_utc(with_dashes: bool = False) -> str:
    """Returns current UTC date stamp in the format:
        `%Y%m%d`
    """
    fmt = "%Y-%m-%d" if with_dashes else "%Y%m%d"
    return time.strftime(fmt, time.gmtime())


def yesterday_datetime():
    """Returns DateTime object for yesterday"""
    return datetime.datetime.utcnow() - datetime.timedelta(days=1)


def yesterday_stamp_utc(with_dashes: bool = False) -> str:
    """Returns yesterday's UTC date stamp in the format:
        `%Y%m%d`
    """
    fmt = "%Y-%m-%d" if with_dashes else "%Y%m%d"
    return (yesterday_datetime()).strftime(fmt)


def ellipsis_print(string: str, length: int) -> str:
    """Returns a trimmed string for printing that has ... (ellipsis) appended
    after length is reached
    """
    if not isinstance(length, int) or length < 1:
        return string
    if isinstance(string, str) and len(string) > length:
        return "{}...".format(string[0:length - 3])
    return string


def generate_table(
        headers: List[str],
        content: List[List[str]],
        border: bool = True,
        column_padding: int = 0,
        justification: Union[str, List[str]] = "^",
        use_checks: bool = False):
    return "\n".join(
        list(generate_table_iter(
            headers,
            content,
            border,
            column_padding,
            justification,
            use_checks
        ))
    )


def generate_table_iter(
        headers: List[str],
        content: List[List[str]],
        border: bool = True,
        column_padding: int = 0,
        justification: Union[str, List[str]] = "^",
        use_checks: bool = False):
    """Returns a printable Table line that has the formatting and spacing"""

    # Check for correct Types
    if not isinstance(headers, list):
        raise TypeError(f"Headers must be of type 'list': {type(content)}")
    if not isinstance(content, list):
        raise TypeError(f"Content must be of type 'list': {type(content)}")

    # Set Checks and Crosses if Desired
    if use_checks:
        check = "\u2713"
        check_replace = ["y", "Y"]
        cross = "\u2717"
        cross_replace = ["n", "N"]
        for l_index, line in enumerate(content):
            if line != "break":
                for i_index, item in enumerate(line):
                    if item in check_replace:
                        content[l_index][i_index] = check
                    elif item in cross_replace:
                        content[l_index][i_index] = cross

    # Determine max Width of column
    widths = [len(str(x)) for x in headers]
    for line in content:
        if not isinstance(line, (list, tuple)):
            if line != "break":
                raise TypeError("Content line item must be of type 'list'")
        elif len(line) != len(headers):
            raise TypeError(
                "Content line item must be same length as 'headers'"
            )
        else:
            # max_nl = max([len(str(x).split("\n")) for x in line])
            for item_index, line_item in enumerate(line):
                split_nl = str(line_item).split("\n")
                max_width = max(
                    [len(x) for x in split_nl]
                )
                if (max_width > widths[item_index]):
                    widths[item_index] = max_width

    # Handle New Lines in cell
    new_content = []
    for line in content:
        max_nl = max([len(str(x).split("\n")) for x in line])
        if max_nl > 1:
            split_cells = [str(x).split("\n") for x in line]
            for nl_cnt in range(max_nl):
                nl_line = []
                for cell in split_cells:
                    if len(cell) <= nl_cnt:
                        nl_line.append("")
                    else:
                        nl_line.append(cell[nl_cnt])
                new_content.append(nl_line)
        else:
            new_content.append(line)

    # Add Column Padding to widths
    widths = [x + column_padding for x in widths]

    # Create justifications array
    if isinstance(justification, list):
        if len(justification) != len(headers):
            raise TypeError(
                "justification passed as array and must be "
                f"same length as headers: headers length {len(headers)}, "
                f"justification length {len(justification)}"
            )
        justifications = justification
    else:
        justifications = [justification for _ in headers]

    # Generate Formatting strings
    line_item = " | ".join(
        [
            f"{{x[{index}]:{justifications[index]}{width}}}"
            for index, width in enumerate(widths)
        ]
    )
    header_line = " | ".join(
        [f"{{x[{index}]:^{width}}}" for index, width in enumerate(widths)]
    )
    divider = "-+-".join(
        [f"{{x[{index}]:-^{width}}}" for index, width in enumerate(widths)]
    )

    # Add Border
    if border:
        line_item = "| " + line_item + " |"
        header_line = "| " + header_line + " |"
        divider = "|-" + divider + "-|"
        border = "___".join(
            [f"{{x[{index}]:_^{width}}}" for index, width in enumerate(widths)]
        )
        yield "._" + border.format(x=["" for x in headers]) + "_."
        border = "_|_".join(
            [f"{{x[{index}]:_^{width}}}" for index, width in enumerate(widths)]
        )

    # Add Header and Divider
    yield header_line.format(x=[str(x) for x in headers])
    yield divider.format(x=["" for x in headers])

    # Add Line Items
    for line in new_content:
        if line == "break":
            yield divider.format(x=["" for x in headers])
        else:
            yield line_item.format(x=[str(x) for x in line])

    # Add Border
    if border:
        yield "|_" + border.format(x=["" for x in headers]) + "_|"


def secs_to_str(seconds: Union[int, float]) -> str:
    """Returns the string representation of the passed seconds in
    `%Hh %Mm %S.%ms` format
    """
    seconds = round(seconds, 3)
    hrs = int(seconds // 3600)
    time_left = seconds - (hrs * 3600)
    mins = int(time_left // 60)
    time_left -= (mins * 60)
    secs = int(time_left)
    time_left -= secs
    milli_secs = int(round(time_left, 3) * 1000)
    if hrs > 0:
        rtn_str = "{hrs}h {mins:>02}m {secs:>02}.{milli:>03}s".format(
            hrs=str(hrs),
            mins=str(mins),
            secs=str(int(secs)),
            milli=str(milli_secs))
    elif mins > 0:
        rtn_str = "{mins}m {secs:>02}.{milli:>03}s".format(
            mins=str(mins),
            secs=str(int(secs)),
            milli=str(milli_secs))
    else:
        rtn_str = "{secs}.{milli:>03}s".format(
            secs=str(int(secs)),
            milli=str(milli_secs))
    return rtn_str
