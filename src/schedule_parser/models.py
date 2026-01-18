import enum
import typing

import pydantic


# region Enums

class Weekday(enum.Enum):
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6

    @staticmethod
    def from_string(string: str) -> Weekday:
        match string.lower():
            case "понедельник":
                return Weekday.MONDAY
            case "вторник":
                return Weekday.TUESDAY
            case "среда":
                return Weekday.WEDNESDAY
            case "четверг":
                return Weekday.THURSDAY
            case "пятница":
                return Weekday.FRIDAY
            case "суббота":
                return Weekday.SATURDAY
            case "воскресенье":
                return Weekday.SUNDAY
            case _:
                raise ValueError(f"Unknown weekday: {string!r}")


# endregion

# region Models

class Period(pydantic.BaseModel):
    lecturer: str
    number: int
    room: str
    subgroup: int
    subject: str

    @property
    def formatted_room(self) -> str:
        if self.room.isdigit():
            return f"{self.room} к."
        else:
            return self.room

    @property
    def is_empty(self) -> bool:
        return not bool(self.lecturer and self.room and self.subject)

    @property
    def readable(self) -> str:
        if self.is_empty:
            raise ValueError("Period is empty!")
        else:
            return " | ".join([
                " ".join([
                    i for i in [
                        f"{self.number}.",
                        f"({self.subgroup})" if self.subgroup else "",
                        self.subject,
                    ] if i
                ]),
                self.formatted_room,
            ])

    def is_same_period(self, period: typing.Self) -> bool:
        return (
            self.number,
            self.subgroup,
        ) == (
            period.number,
            period.subgroup,
        )

    def is_same_metadata(self, period: typing.Self) -> bool:
        return (
            self.lecturer,
            self.number,
            self.room,
            self.subject,
        ) == (
            period.lecturer,
            period.number,
            period.room,
            period.subject,
        )


class DaySchedule(pydantic.BaseModel):
    schedule: list[Period]
    weekday: int


class WeekSchedule(pydantic.BaseModel):
    parity: bool
    schedule: list[DaySchedule]

    def get_day_schedule_by_weekday(self, weekday: Weekday) -> DaySchedule | None:
        try:
            return [model for model in self.schedule if model.weekday == weekday.value][0]
        except IndexError:
            raise ValueError(f"Could not find schedule for weekday: {weekday!r}")


class GroupSchedule(pydantic.BaseModel):
    group: str
    schedule: list[WeekSchedule]

    @classmethod
    def get_group_schedule_by_group(cls, iterable: typing.Iterable[typing.Self], group: str) -> typing.Self:
        try:
            return [model for model in iterable if model.group == group][0]
        except IndexError:
            raise ValueError(f"Could not find schedule for group: {group!r}")

    def get_week_schedule_by_parity(self, parity: bool) -> WeekSchedule | None:
        try:
            return [model for model in self.schedule if model.parity == parity][0]
        except IndexError:
            raise ValueError(f"Could not find schedule for parity: {parity!r}")


class Substitution(pydantic.BaseModel):
    group: str
    period: Period
    substitution: Period

    @classmethod
    def get_substitutions_by_group(cls, iterable: typing.Iterable[typing.Self], group: str) -> list[typing.Self]:
        return [model for model in iterable if model.group == group]

    @property
    def number(self) -> int:
        return self.substitution.number

    @property
    def subgroup(self) -> int:
        return self.substitution.subgroup

# endregion
