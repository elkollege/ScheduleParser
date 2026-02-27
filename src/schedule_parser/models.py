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

    @classmethod
    def from_string(cls, string: str) -> Weekday:
        match string.lower():
            case "понедельник":
                return cls.MONDAY
            case "вторник":
                return cls.TUESDAY
            case "среда":
                return cls.WEDNESDAY
            case "четверг":
                return cls.THURSDAY
            case "пятница":
                return cls.FRIDAY
            case "суббота":
                return cls.SATURDAY
            case "воскресенье":
                return cls.SUNDAY
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


class DaySchedule(pydantic.BaseModel):
    weekday: int
    periods_list: list[Period]


class GroupSchedule(pydantic.BaseModel):
    group_name: str
    day_schedules_list: list[DaySchedule]

    def get_day_schedule_by_weekday(self, weekday: int) -> DaySchedule | None:
        return next(model for model in self.day_schedules_list if model.weekday == weekday)

    @staticmethod
    def get_group_schedule_by_group_name(iterable: list[GroupSchedule], group_name: str) -> GroupSchedule:
        return next(model for model in iterable if model.group_name == group_name)


class Substitution(pydantic.BaseModel):
    group_name: str
    period: Period
    substitution: Period

    @staticmethod
    def get_substitutions_by_group_name(iterable: list[Substitution], group_name: str) -> list[Substitution]:
        return [model for model in iterable if model.group_name == group_name]

# endregion
