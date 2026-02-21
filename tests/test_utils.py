import datetime
import textwrap

import openpyxl
import pyquoks
import pytest

import schedule_parser


class TestUtils:
    @classmethod
    def setup_class(cls) -> None:
        cls._GROUP_NAME = "ЭОЭЭО 25-02"
        cls._CORRECT_SCHEDULES = {
            "11_02_26": textwrap.dedent(
                """\
                """,
            ),
            "12_02_26": textwrap.dedent(
                """\
                """,
            ),
            "13_02_26": textwrap.dedent(
                """\
                """,
            ),
            "16_02_26": textwrap.dedent(
                """\
                """,
            ),
            "17_02_26": textwrap.dedent(
                """\
                """,
            ),
            "18_02_26": textwrap.dedent(
                """\
                """,
            ),
            "19_02_26": textwrap.dedent(
                """\
                """,
            ),
            "20_02_26": textwrap.dedent(
                """\
                """,
            ),
        }  # TODO

    @pytest.mark.skip(reason="waiting for fix")  # FIXME
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

    @pytest.mark.skip(reason="waiting for fix")  # FIXME
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
