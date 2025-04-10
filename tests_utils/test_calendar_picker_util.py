import pytest
from utils.calendar_picker import CalendarPicker
from datetime import datetime
from playwright.sync_api import Page

pytestmark = [pytest.mark.utils]


def test_calculate_v2_calendar_variables(page: Page):
    calendar_picker = CalendarPicker(page)
    (
        current_month_long,
        month_long,
        month_short,
        current_year,
        year,
        end_of_current_decade,
        current_decade,
        decade,
        end_of_current_century,
        current_century,
        century,
    ) = calendar_picker.calculate_v2_calendar_variables(
        datetime(2025, 4, 9), datetime(2020, 6, 9)
    )

    assert current_month_long == "June"
    assert month_long == "April"
    assert month_short == "Apr"
    assert current_year == 2020
    assert year == 2025
    assert end_of_current_decade == "2029"
    assert current_decade == 2020
    assert decade == 2020
    assert end_of_current_century == "2090"
    assert current_century == 2000
    assert century == 2000

    (
        current_month_long,
        month_long,
        month_short,
        current_year,
        year,
        end_of_current_decade,
        current_decade,
        decade,
        end_of_current_century,
        current_century,
        century,
    ) = calendar_picker.calculate_v2_calendar_variables(
        datetime(1963, 1, 28), datetime(2020, 6, 9)
    )

    assert current_month_long == "June"
    assert month_long == "January"
    assert month_short == "Jan"
    assert current_year == 2020
    assert year == 1963
    assert end_of_current_decade == "2029"
    assert current_decade == 2020
    assert decade == 1960
    assert end_of_current_century == "2090"
    assert current_century == 2000
    assert century == 1900

    (
        current_month_long,
        month_long,
        month_short,
        current_year,
        year,
        end_of_current_decade,
        current_decade,
        decade,
        end_of_current_century,
        current_century,
        century,
    ) = calendar_picker.calculate_v2_calendar_variables(
        datetime(2356, 12, 18), datetime(2020, 6, 9)
    )

    assert current_month_long == "June"
    assert month_long == "December"
    assert month_short == "Dec"
    assert current_year == 2020
    assert year == 2356
    assert end_of_current_decade == "2029"
    assert current_decade == 2020
    assert decade == 2350
    assert end_of_current_century == "2090"
    assert current_century == 2000
    assert century == 2300
