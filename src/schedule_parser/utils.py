import datetime
import typing

import openpyxl.worksheet.worksheet

import schedule_parser.models


# region Utils

def apply_substitutions_to_schedule(
        schedule: list[schedule_parser.models.GroupSchedule],
        substitutions: list[schedule_parser.models.Substitution],
        group_name: str,
        date: datetime.datetime,
) -> list[schedule_parser.models.Period]:
    ...  # TODO


def get_week_number(date: datetime.datetime) -> int:
    current_week_number = date.isocalendar().week

    first_school_week_number = datetime.datetime(
        year=date.year - 1 if current_week_number < datetime.datetime(
            year=date.year - 1,
            month=9,
            day=1,
        ).isocalendar().week else date.year,
        month=9,
        day=1,
    ).isocalendar().week

    last_year_week_number = datetime.datetime(
        year=date.year - 1 if current_week_number < datetime.datetime(
            year=date.year - 1,
            month=12,
            day=28,
        ).isocalendar().week else date.year,
        month=12,
        day=28,
    ).isocalendar().week

    if first_school_week_number <= current_week_number:
        return current_week_number - first_school_week_number + 1
    else:
        return last_year_week_number - first_school_week_number + current_week_number + 1


# endregion

# region Parsing

def parse_schedule(
        worksheet: openpyxl.worksheet.worksheet.Worksheet,
) -> typing.Generator[schedule_parser.models.GroupSchedule]:
    ...  # TODO


def parse_substitutions(
        worksheet: openpyxl.worksheet.worksheet.Worksheet,
) -> typing.Generator[schedule_parser.models.Substitution]:
    ...  # TODO

# endregion
