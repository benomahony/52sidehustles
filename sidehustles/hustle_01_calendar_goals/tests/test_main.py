import os
import tempfile
from calendar import monthrange
from datetime import date

import pytest
from reportlab.lib import colors
from .sidehustles.hustle_01_calendar_goals.main import darken_color

####################
# darken_color TESTS
####################


@pytest.mark.parametrize(
    "base_color, factor, expected",
    [
        # Simple test: mid-gray color, 90% darkening => 0.45, 0.45, 0.45
        (colors.Color(0.5, 0.5, 0.5), 0.9, (0.45, 0.45, 0.45)),
        # Test clamp at 0 => factor=0 is black
        (colors.Color(0.2, 0.4, 0.6), 0.0, (0.0, 0.0, 0.0)),
        # Test clamp at 1 => factor=2 tries to lighten but is clamped
        (colors.Color(0.6, 0.8, 1.0), 2.0, (1.0, 1.0, 1.0)),
        # Slight darkening of a typical color
        (colors.Color(0.2, 0.5, 1.0), 0.8, (0.16, 0.4, 0.8)),
    ],
)
def test_darken_color(base_color, factor, expected):
    result = darken_color(base_color, factor)
    # Compare approximately due to floating-point rounding
    assert pytest.approx(result.red, 0.001) == expected[0]
    assert pytest.approx(result.green, 0.001) == expected[1]
    assert pytest.approx(result.blue, 0.001) == expected[2]


###################################
# AlignedWeekendPlannerConfig TESTS
###################################


def test_config_defaults():
    """
    Test that the config's default values are set as expected.
    """
    from reportlab.lib.pagesizes import landscape
    from reportlab.lib.units import cm, mm

    default_config = AlignedWeekendPlannerConfig(year=2025)

    # Check the default year
    assert default_config.year == 2025

    # Check the default page size
    # By default: landscape((305 * mm, 428 * mm))
    expected_width, expected_height = landscape((305 * mm, 428 * mm))
    assert default_config.page_size == (expected_width, expected_height)

    # Check a few other defaults
    assert default_config.margin == pytest.approx(0.9 * cm, 0.001)
    assert default_config.font_name == "Helvetica"
    assert default_config.title_size == 30


def test_config_custom():
    """
    Test that custom values in config are stored properly.
    """
    custom_config = AlignedWeekendPlannerConfig(
        year=2030,
        month_label_width=4.0,
        goals_labels=["A", "B", "C"],
    )
    assert custom_config.year == 2030
    assert custom_config.month_label_width == 4.0
    assert custom_config.goals_labels == ["A", "B", "C"]


########################################
# AlignedWeekendPlanner Integration TESTS
########################################


def test_aligned_weekend_planner_creates_pdf():
    """
    Test that the AlignedWeekendPlanner can create a PDF without errors
    and that the PDF is not empty.
    """
    config = AlignedWeekendPlannerConfig(year=2025)
    planner = AlignedWeekendPlanner(config)

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_file:
        temp_pdf_path = tmp_file.name

    try:
        # Generate the planner PDF
        planner.create_planner(temp_pdf_path)

        # Ensure the file exists and is non-empty
        assert os.path.exists(temp_pdf_path), "PDF file was not created!"
        assert os.path.getsize(temp_pdf_path) > 0, "PDF file is empty!"
    finally:
        # Cleanup temp file
        if os.path.exists(temp_pdf_path):
            os.remove(temp_pdf_path)


def test_aligned_weekend_planner_calendar_correctness():
    """
    A lightweight logic check to ensure days_in_month and start_weekday
    are used correctly. This doesn't parse the final PDF but checks
    that each month's days are drawn in the correct columns (no crash).
    """
    config = AlignedWeekendPlannerConfig(year=2025)
    planner = AlignedWeekendPlanner(config)

    for month_number in range(1, 13):
        days_in_month = monthrange(config.year, month_number)[1]
        start_wkday = date(config.year, month_number, 1).weekday()
        # If code is correct, should not raise any exceptions
        # in _draw_month_row
        try:
            planner._draw_month_row(
                pdf=planner.c,  # We can pass the config or mock a canvas here
                month=month_number,
                row_bottom_y=100,
            )
        except Exception as e:
            pytest.fail(
                f"Drawing month row failed for {month_number=}, {days_in_month=}, {start_wkday=}. Error: {e}"
            )
