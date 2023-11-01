
from collections import namedtuple
from typing import List, NamedTuple

from .printing import generate_table, secs_to_str
from .timer import Timer

NL = "\n"


class TimerLap(NamedTuple):
    total_time: float
    lap_time: float
    lap_name: str
    tag: str


class LapWatch(Timer):
    lap_tuple = namedtuple(
        "TimerLap",
        ["total_time", "lap_time", "lap_name", "tag"]
    )

    def __init__(self, timer_name: str = None) -> None:
        self.laps = LapList()
        self.name = timer_name
        super(LapWatch, self).__init__()

    def __str__(self) -> str:
        return f"Timer: {self.name}{NL}{self.laps}"

    def lap(self, lap_name: str = None, tag: str = None) -> float:
        """Appends a lap to the lap list and returns the lap time"""
        total = self.elapsed
        if not lap_name:
            lap_name = "Lap %d" % (len(self.laps) + 1)
        if len(self.laps) == 0:
            lap_time = total
        else:
            lap_time = total - self.laps[-1][0]
        self.laps.append(self.lap_tuple(total, lap_time, lap_name, tag))
        return lap_time

    def reset_laps(self) -> None:
        """Clear out the current lap list"""
        self.laps = LapList()


class LapList(list):

    def __str__(self):
        return generate_table(
            ["Lap Name", "Lap Time", "Elapsed", "Tag"],
            [
                [
                    x.lap_name,
                    secs_to_str(x.lap_time),
                    secs_to_str(x.total_time),
                    x.tag
                ] for x in self
            ]
        )

    def average(self) -> float:
        """Returns the average of lap times"""
        if len(self) > 0:
            return self.sum() / len(self)
        else:
            return self.sum()

    def max(self) -> float:
        """Returns the max lap time"""
        return max(self, key=lambda x: x.lap_time)

    def min(self) -> float:
        """Returns the min lap time"""
        return min(self, key=lambda x: x.lap_time)

    def sum(self) -> float:
        """Returns the sum of lap times"""
        return sum([x.lap_time for x in self])

    def filter(self, tag_filter: List[str] = None) -> "LapList":
        """Returns a new Filtered LapList to include only laps whose tag
        matches a tag in the filter
        """
        if tag_filter is None:
            tag_filter = []
        return LapList([x for x in self if x.tag in tag_filter])

    def exclude(self, tag_exclude: List[str] = None) -> "LapList":
        """Returns a new Filtered LapList to include all laps whose tag does
        not matche a tag in the filter
        """
        if tag_exclude is None:
            tag_exclude = []
        return LapList([x for x in self if x.tag not in tag_exclude])
