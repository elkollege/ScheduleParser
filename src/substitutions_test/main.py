import typing
import openpyxl, openpyxl.worksheet.worksheet, openpyxl.cell, pyquoks
import constants


def get_formatted_row(
        worksheet: openpyxl.worksheet.worksheet.Worksheet,
        row: tuple[openpyxl.cell.Cell, ...]
) -> typing.Generator[str]:
    for cell in row[:constants.TABLE_WIDTH]:
        column_max_len = max([
            len(str(c_cell.value).replace(str(None), "")) for c_cell in list(
                worksheet.columns
            )[cell.column - 1][constants.TABLE_HEADER_INDEX:]
        ])

        yield str(cell.value).replace(str(None), "").ljust(column_max_len) if row[0].value else "—" * column_max_len


def main() -> None:
    workbook = openpyxl.load_workbook(
        filename=pyquoks.utils.get_path("tables/substitutions.xlsx"),
    )

    worksheet = workbook.worksheets[0]

    for row in list(worksheet.rows)[constants.TABLE_HEADER_INDEX:]:
        print(f"| {" | ".join(get_formatted_row(worksheet, row))} |")


if __name__ == "__main__":
    main()
