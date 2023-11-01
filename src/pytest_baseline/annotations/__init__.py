from typing import Any, Callable, List, Optional, Tuple, Union
from _pytest.nodes import Item
from _pytest.runner import CallInfo

from pytest_html import extras

FixtureInfoItem = Tuple[str, Any, Optional[Callable]]
FixtureInfoType = List[FixtureInfoItem]

HtmlExtraType = Optional[Union[
    extras.extra,
    extras.html,
    extras.image,
    extras.jpg,
    extras.json,
    extras.mp4,
    extras.png,
    extras.svg,
    extras.text,
    extras.url,
    extras.video,
]]

FixtureExtraPrintFunc = Optional[Callable[
    [Any, str, str, str, Item, CallInfo],
    Union[Tuple[Any, str], Any]
]]

FixtureExtraFilterFunc = Optional[Callable[[str, str, str, Any], bool]]
