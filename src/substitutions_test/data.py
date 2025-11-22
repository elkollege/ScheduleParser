import typing
import openpyxl.worksheet.worksheet
import models, constants


def get_substitutions(worksheet: openpyxl.worksheet.worksheet.Worksheet) -> typing.Generator[models.SubstitutionModel]:
    for row in list(worksheet.rows)[constants.TABLE_HEADER_INDEX:]:
        row = list(
            map(
                lambda cell: cell.value,
                list(row[:constants.TABLE_WIDTH]),
            )
        )

        if set(row) == {None}:
            continue

        row_values = dict(
            zip(
                [
                    "group",
                    "number",
                    "period_subgroup",
                    "period_subject",
                    "period_lecturer",
                    "period_room",
                    "substitution_subgroup",
                    "substitution_subject",
                    "substitution_lecturer",
                    "substitution_room",
                ],
                row,
            )
        )

        yield models.SubstitutionModel(
            data={
                "group": row_values["group"],
                "period": {
                    "lecturer": row_values["period_lecturer"],
                    "number": int(row_values["number"]),
                    "room": row_values["period_room"],
                    "subgroup": int(row_values["period_subgroup"]) if row_values["period_subgroup"] else 0,
                    "subject": row_values["period_subject"],
                },
                "substitution": {
                    "lecturer": row_values["substitution_lecturer"],
                    "number": int(row_values["number"]),
                    "room": row_values["substitution_room"],
                    "subgroup": int(row_values["substitution_subgroup"]) if row_values["substitution_subgroup"] else 0,
                    "subject": row_values["substitution_subject"],
                },
            },
        )
