import datetime
import itertools
import typing

import openpyxl.cell.cell
import openpyxl.worksheet.worksheet

import schedule_parser.constants
import schedule_parser.models


def _ensure_str(var: typing.Any) -> str:
    return str(var) if var else ""


def _ensure_int(var: typing.Any) -> int:
    return int(var) if var else 0


def parse_schedule(
        worksheet: openpyxl.worksheet.worksheet.Worksheet,
) -> typing.Generator[schedule_parser.models.GroupSchedule]:
    def _get_periods(
            columns: list[list[openpyxl.cell.cell.Cell]],
    ) -> typing.Generator[schedule_parser.models.Period]:
        def _get_number(row: int) -> typing.Any:
            return int(
                worksheet.cell(
                    row=row,
                    column=schedule_parser.constants.SCHEDULE_DATA_NUMBER_COLUMN,
                ).value
            )

        def _get_subgroup(column: int) -> typing.Any:
            return worksheet.cell(
                row=schedule_parser.constants.SCHEDULE_DATA_SUBGROUP_ROW,
                column=column,
            ).value

        split_columns = [
            [
                list(batched) for batched in itertools.batched(column, schedule_parser.constants.SCHEDULE_PERIOD_HEIGHT)
            ] for column in columns
        ]

        for period_values in [list(current_columns) for current_columns in zip(*split_columns)]:
            if isinstance(period_values[1][0], openpyxl.cell.cell.MergedCell):
                yield schedule_parser.models.Period(
                    lecturer=_ensure_str(period_values[0][1].value),
                    number=_ensure_int(_get_number(period_values[0][0].row)),
                    room=_ensure_str(period_values[3][0].value),
                    subgroup=schedule_parser.constants.SCHEDULE_DATA_NO_SUBGROUP,
                    subject=_ensure_str(period_values[0][0].value),
                )
            else:
                for first_column, second_column in [(0, 1), (2, 3)]:
                    if period_values[first_column][0].value:
                        yield schedule_parser.models.Period(
                            lecturer=_ensure_str(period_values[first_column][1].value),
                            number=_ensure_int(_get_number(period_values[first_column][0].row)),
                            room=_ensure_str(period_values[second_column][0].value),
                            subgroup=_ensure_int(_get_subgroup(period_values[first_column][0].column)),
                            subject=_ensure_str(period_values[first_column][0].value),
                        )

    def _get_day_schedule(
            columns: list[list[openpyxl.cell.cell.Cell]],
    ) -> typing.Generator[schedule_parser.models.DaySchedule]:
        def _get_weekday(row: int) -> schedule_parser.models.Weekday:
            return schedule_parser.models.Weekday.from_string(
                string=worksheet.cell(
                    row=row,
                    column=schedule_parser.constants.SCHEDULE_DATA_WEEKDAY_COLUMN,
                ).value,
            )

        split_columns = []

        for column in columns:
            current_columns = []
            current_column = []

            for cell in column:
                current_column.append(cell)
                if cell.border.bottom.style == schedule_parser.constants.SCHEDULE_DATA_WEEKDAY_BORDER:
                    current_columns.append(current_column.copy())
                    current_column.clear()

            split_columns.append(current_columns)

        for day_schedule in [list(current_columns) for current_columns in zip(*split_columns)]:
            yield schedule_parser.models.DaySchedule(
                weekday=_get_weekday(day_schedule[0][0].row).value,
                schedule=list(_get_periods(day_schedule)),
            )

    def _get_week_schedule(
            columns: list[tuple[openpyxl.cell.cell.Cell, ...]],
    ) -> typing.Generator[schedule_parser.models.WeekSchedule]:
        def _check_cell_color(cell_index: int) -> bool:
            return columns[0][cell_index].fill.fgColor.rgb == schedule_parser.constants.SCHEDULE_DATA_ODD_COLOR

        week_variants = [
            (
                [[cell for cell in column if _check_cell_color(column.index(cell)) == parity] for column in columns],
                not parity,
            ) for parity in (True, False)
        ]

        for week_variant in week_variants:
            yield schedule_parser.models.WeekSchedule(
                parity=week_variant[1],
                schedule=list(_get_day_schedule(week_variant[0])),
            )

    def _get_group(column: int) -> typing.Any:
        return worksheet.cell(
            row=schedule_parser.constants.SCHEDULE_DATA_GROUP_ROW,
            column=column,
        ).value

    for group_columns in itertools.batched(
            list(worksheet.columns)[
                schedule_parser.constants.SCHEDULE_SIDEBAR_WIDTH:schedule_parser.constants.SCHEDULE_JUNK_OFFSET
            ],
            schedule_parser.constants.SCHEDULE_GROUP_WIDTH,
    ):
        group_columns = [
            column[
                schedule_parser.constants.SCHEDULE_HEADER_INDEX:schedule_parser.constants.SCHEDULE_FOOTER_OFFSET
            ] for column in group_columns[-schedule_parser.constants.SCHEDULE_JUNK_OFFSET:]
        ]

        yield schedule_parser.models.GroupSchedule(
            group=_ensure_str(_get_group(group_columns[0][0].column)),
            schedule=list(_get_week_schedule(group_columns)),
        )


def parse_substitutions(
        worksheet: openpyxl.worksheet.worksheet.Worksheet,
) -> typing.Generator[schedule_parser.models.Substitution]:
    def _get_period(*args, number: int) -> schedule_parser.models.Period:
        return schedule_parser.models.Period(
            lecturer=_ensure_str(args[2]),
            number=number,
            room=_ensure_str(args[3]),
            subgroup=_ensure_int(args[0]),
            subject=_ensure_str(args[1]),
        )

    for row in list(worksheet.rows)[schedule_parser.constants.SUBSTITUTIONS_HEADER_INDEX:]:
        row_values = [cell.value for cell in row[:schedule_parser.constants.SUBSTITUTIONS_WIDTH]]

        if set(row_values) == {
            None,
        }:
            continue

        group, period_number, *row_values = row_values
        period_number = int(period_number)

        yield schedule_parser.models.Substitution(
            group=group,
            period=_get_period(
                *row_values[:4],
                number=period_number,
            ),
            substitution=_get_period(
                *row_values[4:],
                number=period_number,
            ),
        )


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


def get_schedule_with_substitutions(
        schedule: list[schedule_parser.models.GroupSchedule],
        substitutions: list[schedule_parser.models.Substitution],
        group: str,
        date: datetime.datetime,
) -> list[schedule_parser.models.Period]:
    def sort_and_filter_same_but_subgroup(periods: list[schedule_parser.models.Period]) -> list[
        schedule_parser.models.Period]:
        filtered_periods = []

        for first_period in periods:
            for second_period in periods:
                if (not first_period.is_same_period(second_period)
                        and first_period.is_same_metadata(second_period)):
                    first_period.subgroup = 0
                    filtered_periods.append(first_period)
                    break
            else:
                filtered_periods.extend([first_period] * 2)

        filtered_periods.sort(
            key=lambda period: (period.number, period.subgroup),
        )

        return filtered_periods[::2]

    schedule = (
        schedule_parser.models.GroupSchedule.get_group_schedule_by_group(schedule, group)
        .get_week_schedule_by_parity(get_week_number(date) % 2 == 0)
        .get_day_schedule_by_weekday(schedule_parser.models.Weekday(date.weekday()))
        .schedule
    )

    substitutions = schedule_parser.models.Substitution.get_substitutions_by_group(substitutions, group)

    new_schedule = schedule.copy()

    for substitution in substitutions:
        for index, period_model in enumerate(new_schedule):
            if period_model.is_same_period(substitution.period):
                new_schedule[index] = substitution.substitution
                break
        else:
            if not substitution.substitution.is_empty:
                new_schedule.append(substitution.substitution)

    return sort_and_filter_same_but_subgroup([period for period in new_schedule if not period.is_empty])
