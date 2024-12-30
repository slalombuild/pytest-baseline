from typing import (Any, Callable, List, Literal, Optional, Tuple, TypedDict,
                    Union)

from _pytest.nodes import Item
from _pytest.runner import CallInfo

FixtureInfoItem = Tuple[str, Any, Optional[Callable]]
FixtureInfoType = List[FixtureInfoItem]


class HtmlExtraReturnType(TypedDict):
    name: str
    format_type: str
    content: Any
    mime_type: str
    extension: str


HtmlExtraType = Optional[Callable[[
    Any,
    Literal["html", "image", "json", "text", "url", "video"],
    Optional[str],
    Optional[str],
    Optional[str]
], HtmlExtraReturnType]]

FixtureExtraPrintFunc = Optional[Callable[
    [Any, str, str, str, Item, CallInfo],
    Union[Tuple[Any, str], Any]
]]

FixtureExtraFilterFunc = Optional[Callable[[str, str, str, Any], bool]]
