import datetime
import json
import time
from inspect import cleandoc
from textwrap import indent
from typing import Any, Dict, Generator, List, Optional, Union

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

    if len(obj_dir) > 0:

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
    else:
        attr_str = (
            "No attributes to display, attributes may have been filtered by "
            f"`filter_`(passed:{filter_}) and `filter__`(passed:{filter__})"
        )
    return f"{NL}{type(obj)}:{NL}{attr_str}{NL}"


def center_dict_str(
    data: Dict[str, Any],
    delimiter: str = " : ",
    fill: str = " ",
    indent_len: int = 0,
    key_justification: str = ">",
    value_justification: str = "<"
) -> str:
    """Generates the string for a Dictionary centering on the delimiter
    between the Key and Value, Values whose __str__ method returns a string
    with `\n` will be indented to fit in Value column.  Any sub dictionaries
    will be centered and indented to fit in the Value column.  Any sub item
    that is JSON Serializable will be json.dump'd indented to fit in the Value
    column.
    """
    def new_lines(item: Any, ind_len: int) -> str:
        if isinstance(item, dict):
            return center_dict_str(
                item,
                delimiter=delimiter,
                fill=fill,
                indent_len=ind_len,
                key_justification=key_justification,
                value_justification=value_justification
            )[ind_len:]
        if isinstance(item, list):
            try:
                temp_rtn = json_dumps(item, indent=4)
            except Exception:
                temp_rtn = str(item)
        else:
            temp_rtn = str(item)
        if f"{NL}" in temp_rtn:
            temp_rtn = cleandoc(temp_rtn)
            return indent(temp_rtn, " " * ind_len)[ind_len:]
        return temp_rtn

    def get_str_value(obj, key):
        key_value = obj.get(key)
        try:
            str(key_value)
            return key_value
        except TypeError:
            return f"TypeError: None {type(key_value)}"

    if len(data.keys()) == 0:
        return ""

    hdr_w = max(
        [
            len(str(k)) for k in data.keys()
            if not str(k).startswith("LEAVE_LINE_AS_IS")
        ]
    )
    val_ind = hdr_w + len(delimiter) + indent_len
    val_w = max([
        len(i)
        for k in data.keys()
        if not str(k).startswith("LEAVE_LINE_AS_IS")
        for i in new_lines(get_str_value(data, k), 0).split("\n")
    ])
    ind_str = f"{'':{fill}^{indent_len}}"
    val_just = value_justification
    return NL.join([
        (
            f"{ind_str}{str(k):{fill}{key_justification}{hdr_w}}{delimiter}"
            f"{new_lines(get_str_value(data, k), val_ind):{val_just}{val_w}}"
        ).rstrip(" ")
        if not str(k).startswith("LEAVE_LINE_AS_IS")
        else f"{ind_str}{str(get_str_value(data, k)):{val_just}{val_w}}"
        for k in data.keys()
    ])


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
    headers: Union[List[str], None],
    content: List[List[str]],
    border: bool = True,
    column_padding: int = 0,
    justification: Union[str, List[str]] = "^",
    use_checks: bool = False,
    cell_limit: int = 500
) -> Generator[str, None, None]:
    """Returns a printable Table line that has the formatting and spacing"""

    # Check for No Headers
    if headers is None:
        include_header = False
        headers = [
            "" for _ in range(max([len(x) for x in content if x != "break"]))
        ]
    else:
        include_header = True

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
                max_width = max([
                    len(x) if len(x) <= cell_limit else cell_limit
                    for x in split_nl
                ])
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
                        nl_line.append(cell[nl_cnt][0:cell_limit])
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
    if include_header:
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


class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        """Default Encoder that will try to just provide the string value if
        not JSON Serizable
        """
        try:
            rtn_encoded = json.JSONEncoder.default(self, obj)
        except TypeError:
            rtn_encoded = str(obj)
        else:
            raise
        return rtn_encoded


def json_dumps(obj, *args, **kwargs):
    """JSON dumps wrapper that will auto indent and a Custom Encoder to print
    more pythonic objects
    """
    if "indent" not in kwargs:
        kwargs["indent"] = 2
    if "cls" not in kwargs:
        kwargs["cls"] = CustomEncoder
    return json.dumps(obj, *args, **kwargs)


def list_compare_printout(
    list_names: List[str],
    list_1: List[str],
    list_2: List[str],
    *args
) -> str:
    """Generates a table printout of a list comparison"""
    full_set = set()
    full_set.update(list_1)
    full_set.update(list_2)
    for extra_list in args:
        full_set.update(extra_list)
    list_o_lists = [list_1, list_2, *args]
    output = []
    for item in sorted(list(full_set)):
        line = []
        for sub_list in list_o_lists:
            if item in sub_list:
                line.append(item)
            else:
                line.append("--")
        output.append(line)
    return generate_table(list_names, output)


def generate_list_strings(
    list_of_strs: List[str],
    title: str,
    list_format: str = "  {index:>{padding}} - {item}"
):
    """Returns a New line delimited string in the following:
    {TITLE}[:]
      ## - ITEM 0
      ## - ITEM 1
      ...
    """
    padding = len(str(len(list_of_strs)))
    rtn_str = f"{title}{':' if not title.endswith(':') else ''}\n"
    if len(list_of_strs) == 0:
        rtn_str += "    - No Items in List."
    rtn_str += "\n".join([
        list_format.format(item=item, index=index + 1, padding=padding)
        for index, item in enumerate(list_of_strs)
    ])
    return rtn_str


def generate_list_count_table(list_o_values: List[Any], **kwargs) -> str:
    """Counts all the unique values in a list of values and returns a table
    with the counts of each value, sorted by the number of each (highest
    to lowest) the items in the list must be hashable
    """
    values = [[x, list_o_values.count(x)] for x in set(list_o_values)]
    values.sort(key=lambda x: x[1], reverse=True)
    return generate_table(["Value", "Count"], values, **kwargs)
