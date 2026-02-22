import enum

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
    number: int
    subgroup: int
    subject: str
    lecturer: str
    room: str

    @property
    def is_empty(self) -> bool:
        return not bool(self.subject and self.lecturer and self.room)

    @property
    def readable(self) -> str:
        return " | ".join([
            " ".join([
                i for i in [
                    f"{self.number}.",
                    f"({self.subgroup})" if self.subgroup != 0 else None,
                    self.subject,
                ] if i
            ]),
            self.room,
        ])

    def is_same_period(self, other: Period) -> bool:
        return (
            self.number,
            self.subgroup,
        ) == (
            other.number,
            other.subgroup,
        )

    def is_same_metadata(self, other: Period) -> bool:
        return (
            self.number,
            self.subject,
            self.lecturer,
            self.room,
        ) == (
            other.number,
            other.subject,
            other.lecturer,
            other.room,
        )


class DaySchedule(pydantic.BaseModel):
    weekday: int
    periods_list: list[Period]


# class WeekSchedule(pydantic.BaseModel):
#     parity: bool
#     day_schedules_list: list[DaySchedule]
#
#     def get_day_schedule_by_weekday(self, weekday: int) -> DaySchedule | None:
#         return next(model for model in self.day_schedules_list if model.weekday == weekday)


class GroupSchedule(pydantic.BaseModel):
    group_name: str
    day_schedules_list: list[DaySchedule]

    @classmethod
    def get_group_schedule_by_group_name(
            cls,
            iterable: list[GroupSchedule],
            group_name: str,
    ) -> GroupSchedule:
        return next(model for model in iterable if model.group_name == group_name)

    def get_day_schedule_by_weekday(self, weekday: int) -> DaySchedule | None:
        return next(model for model in self.day_schedules_list if model.weekday == weekday)

    # def get_week_schedule_by_parity(self, parity: bool) -> WeekSchedule | None:
    #     return next(model for model in self.week_schedules_list if model.parity == parity)


class Substitution(pydantic.BaseModel):
    group_name: str
    period: Period
    substitution: Period

    @classmethod
    def get_substitutions_by_group_name(cls, iterable: list[Substitution], group_name: str) -> list[Substitution]:
        return [model for model in iterable if model.group_name == group_name]

    @property
    def number(self) -> int:
        return self.substitution.number

    @property
    def subgroup(self) -> int:
        return self.substitution.subgroup

# endregion
