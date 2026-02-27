import datetime
import textwrap

import pydantic


class TestSubstitution(pydantic.BaseModel):
    date: datetime.date
    test_schedules_list: list[TestCorrectSchedule]


class TestCorrectSchedule(pydantic.BaseModel):
    group_name: str
    correct_schedule: str

    @property
    def correct_schedule_dedent(self) -> str:
        return textwrap.dedent(self.correct_schedule).rstrip()
