import openpyxl, pyquoks
import data


def main():
    workbooks = [
        "substitutions",
        "substitutions_old",
    ]

    for filename in workbooks:
        workbook = openpyxl.load_workbook(
            filename=pyquoks.utils.get_path(f"tables/{filename}.xlsx"),
        )

        worksheet = workbook.worksheets[0]

        print(
            f"\n{filename}:",
            *map(
                lambda model: model._data,
                data.get_substitutions(worksheet),
            ),
            sep="\n",
        )


if __name__ == "__main__":
    main()
