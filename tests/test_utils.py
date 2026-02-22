import datetime
import textwrap

import openpyxl
import pyquoks

import schedule_parser.models
import schedule_parser.utils


class TestUtils:
    @classmethod
    def setup_class(cls) -> None:
        cls._GROUP_NAME = "ЭОЭЭО 25-02"
        cls._CORRECT_SCHEDULES = {
            "11_02_26": textwrap.dedent(
                """\
                1. Информ. (теор.) | 305
                2. Физика | 110
                3. Математика | 411
                4. Русс.яз. | 213
                5. Биология | 410
                """,
            ),
            "12_02_26": textwrap.dedent(
                """\
                0. Классный час | 410
                1. Химия | 102
                2. Физ-ра | с.з.
                3. Лит-ра | 213
                4. История | 301
                """,
            ),
            "13_02_26": textwrap.dedent(
                """\
                1. (1) Информ. (пр.) | 305
                2. ОБиЗР | 201
                3. Математика | 308
                4. Инж. граф. | 210
                5. История | 301
                """,
            ),
            "16_02_26": textwrap.dedent(
                """\
                4. География | 401
                5. Физика | 110
                """,
            ),
            "17_02_26": textwrap.dedent(
                """\
                1. Лит-ра | 213
                2. География | 401
                3. Математика | 411
                4. Химия | 103М
                """,
            ),
            "18_02_26": textwrap.dedent(
                """\
                1. Математика | 308
                2. Физика | 110
                3. Математика | 308
                4. Русс.яз. | 213
                5. Биология | 410
                """,
            ),
            "19_02_26": textwrap.dedent(
                """\
                0. Классный час | 410
                1. Химия | 102
                2. Физ-ра | с.з.
                3. Биология | 410
                4. История | 301
                """,
            ),
            "20_02_26": textwrap.dedent(
                """\
                0. Разговоры о важном | 410
                1. (1) Информ. (пр.) | 305
                1. (2) Ин. язык | 309
                2. ОБиЗР | 201
                3. Физ-ра | спортзал
                4. (1) Ин. язык | 309
                4. (2) Информ. (пр.) | 305
                """,
            ),
        }

    def test_parse_schedule(self):
        workbook = openpyxl.load_workbook(
            filename=pyquoks.utils.get_path("resources/tables/schedule.xlsx"),
        )

        for model in schedule_parser.utils.parse_schedule(workbook.worksheets[0]):
            assert isinstance(model, schedule_parser.models.GroupSchedule), "objects in parsed schedules list"

    def test_parse_substitutions(self):
        for string_date in self._CORRECT_SCHEDULES.keys():
            workbook = openpyxl.load_workbook(
                filename=pyquoks.utils.get_path(f"resources/tables/substitutions_{string_date}.xlsx"),
            )

            for substitution in schedule_parser.utils.parse_substitutions(workbook.worksheets[0]):
                assert isinstance(
                    substitution,
                    schedule_parser.models.Substitution,
                ), f"({string_date}) objects in parsed substitutions list"

    def test_schedule_with_substitutions(self):
        workbook_schedule = openpyxl.load_workbook(
            filename=pyquoks.utils.get_path("resources/tables/schedule.xlsx"),
        )

        for string_date, correct_schedule in self._CORRECT_SCHEDULES.items():
            workbook_substitutions = openpyxl.load_workbook(
                filename=pyquoks.utils.get_path(f"resources/tables/substitutions_{string_date}.xlsx"),
            )

            current_date = datetime.datetime.strptime(string_date, "%d_%m_%y")

            current_schedule = schedule_parser.utils.apply_substitutions_to_schedule(
                schedule=list(
                    schedule_parser.utils.parse_schedule(
                        worksheet=workbook_schedule.worksheets[0],
                    )
                ),
                substitutions=list(
                    schedule_parser.utils.parse_substitutions(
                        worksheet=workbook_substitutions.worksheets[0],
                    )
                ),
                group_name=self._GROUP_NAME,
                date=current_date,
            )

            assert "".join(
                f"{period.readable}\n" for period in current_schedule
            ) == correct_schedule, f"({string_date}) compare parsed schedule with correct one"
