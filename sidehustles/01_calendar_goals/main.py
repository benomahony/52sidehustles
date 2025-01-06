from dataclasses import dataclass, field
from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape
from reportlab.lib.units import cm, mm
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from calendar import monthrange
import datetime


def darken_color(base_color: colors.Color, factor: float = 0.9) -> colors.Color:
    """
    Return a darkened version of `base_color` by multiplying each
    RGB component by `factor` (less than 1 => darker).
    """
    # Ensure the color is an RGBColor or HexColor
    r = base_color.red
    g = base_color.green
    b = base_color.blue
    # Darken them
    dr = max(0, min(1, r * factor))
    dg = max(0, min(1, g * factor))
    db = max(0, min(1, b * factor))
    return colors.Color(dr, dg, db)


@dataclass
class AlignedWeekendPlannerConfig:
    year: int

    # Page Layout
    page_size: tuple[float, float] = landscape((305 * mm, 428 * mm))
    margin: float = 0.9 * cm

    # Extra space on the left to place the month name
    month_label_width: float = 3 * cm

    # The height of the top row that shows "Mon, Tue, Wed..."
    weekday_header_height: float = 0.7 * cm

    # Day columns and month rows
    day_cell_width: float = 0.90 * cm
    month_row_height: float = 2 * cm

    # Goals area
    goals_area_width: float = 5.5 * cm
    goals_column_count: int = 3
    checkbox_size: float = 0.30 * cm
    checkbox_line_spacing: float = 0.1 * cm
    checkbox_lines_per_column: int = 4

    # The labels for each goals column
    goals_labels: list[str] = field(
        default_factory=lambda: ["Health", "Wealth", "Happiness"]
    )

    # Fonts and sizes
    font_name: str = "Helvetica"
    title_size: int = 30
    month_label_size: int = 12
    day_font_size: int = 10
    goals_label_size: int = 10

    # Default pastel Tailwind-like rainbow:
    # (These are approximations of *-50 shades from Tailwind.)
    # Red -> Orange -> Amber -> Yellow -> Lime -> Green -> Teal -> Sky -> Blue -> Indigo -> Violet -> Purple
    # You can, of course, substitute your own palette.
    month_colors: list[colors.Color] = field(
        default_factory=lambda: [
            colors.HexColor("#fef2f2"),  # red-50
            colors.HexColor("#fff7ed"),  # orange-50
            colors.HexColor("#fffbeb"),  # amber-50
            colors.HexColor("#fefce8"),  # yellow-50
            colors.HexColor("#f7fee7"),  # lime-50
            colors.HexColor("#f0fdf4"),  # green-50
            colors.HexColor("#f0fdfa"),  # teal-50
            colors.HexColor("#f0f9ff"),  # sky-50
            colors.HexColor("#eff6ff"),  # blue-50
            colors.HexColor("#eef2ff"),  # indigo-50
            colors.HexColor("#f5f3ff"),  # violet-50
            colors.HexColor("#faf5ff"),  # purple-50
        ]
    )


class AlignedWeekendPlanner:
    def __init__(self, config: AlignedWeekendPlannerConfig):
        self.c = config
        self.width, self.height = config.page_size
        self.styles = getSampleStyleSheet()
        self._setup_styles()

        self.max_day_columns = 36
        self.short_dow = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    def _setup_styles(self):
        """Define custom paragraph styles if needed."""
        self.styles.add(
            ParagraphStyle(
                name="MonthLabel",
                fontName=self.c.font_name,
                fontSize=self.c.month_label_size,
                spaceAfter=5,
            )
        )

    def create_planner(self, output_path: str):
        pdf = canvas.Canvas(output_path, pagesize=self.c.page_size)

        # 1) Title
        self._draw_title(pdf)

        # 2) Annual Goals box
        annual_goals_bottom = self._draw_annual_goals(pdf)

        # 3) Weekday header (without the left boundary line)
        header_top_y = annual_goals_bottom - self.c.weekday_header_height + 0.2 * cm
        self._draw_weekday_header(pdf, header_top_y)

        # 4) Goals header row
        self._draw_goals_header(pdf, header_top_y)

        # 5) The first month row starts below the header
        top_y_for_months = header_top_y - 2.7 * cm

        for idx in range(12):
            month_number = idx + 1
            row_y = top_y_for_months - (idx * self.c.month_row_height)
            self._draw_month_row(pdf, month_number, row_y)

        pdf.save()

    def _draw_title(self, pdf: canvas.Canvas):
        pdf.setFont(self.c.font_name, self.c.title_size)
        pdf.drawCentredString(
            self.width / 2,
            self.height - 1.4 * cm,
            f"Annual Planner {self.c.year}",
        )

    def _draw_annual_goals(self, pdf: canvas.Canvas) -> float:
        top_y = self.height - 2.0 * cm
        box_height = 2.0 * cm

        pdf.setStrokeColor(colors.CMYKColor(0, 0, 0, 1))
        pdf.rect(
            self.c.margin,
            top_y - box_height,
            self.width - 2 * self.c.margin,
            box_height,
        )

        pdf.setFont(self.c.font_name, 14)
        pdf.drawString(self.c.margin + 0.3 * cm, top_y - 0.5 * cm, "ANNUAL GOALS:")

        return top_y - box_height

    def _draw_weekday_header(self, pdf: canvas.Canvas, top_y: float):
        """Draw Mon..Sun row across columns 0..max_day_columns, skipping left boundary above January."""
        pdf.setFont(self.c.font_name, self.c.day_font_size)
        bottom_y = top_y - self.c.weekday_header_height

        day_col_left_x = self.c.margin + self.c.month_label_width
        day_col_right_x = day_col_left_x + self.max_day_columns * self.c.day_cell_width

        pdf.setStrokeColor(colors.CMYKColor(0, 0, 0, 1))
        pdf.line(day_col_left_x, top_y, day_col_right_x, top_y)
        pdf.line(day_col_left_x, bottom_y, day_col_right_x, bottom_y)

        # No vertical line on the far left
        # Right boundary:
        pdf.line(day_col_right_x, bottom_y, day_col_right_x, top_y)

        # Vertical lines & day-of-week labels
        for col_idx in range(self.max_day_columns + 1):
            x_line = day_col_left_x + col_idx * self.c.day_cell_width
            pdf.line(x_line, bottom_y, x_line, top_y)

            if col_idx < self.max_day_columns:
                dow_label = self.short_dow[col_idx % 7]
                pdf.drawCentredString(
                    x_line + self.c.day_cell_width / 2,
                    bottom_y + (self.c.weekday_header_height / 4),
                    dow_label,
                )

    def _draw_goals_header(self, pdf: canvas.Canvas, top_y: float):
        day_col_left_x = self.c.margin + self.c.month_label_width
        day_col_right_x = day_col_left_x + self.max_day_columns * self.c.day_cell_width
        x_goals_start = day_col_right_x
        x_goals_end = x_goals_start + self.c.goals_area_width

        header_bottom_y = top_y - self.c.weekday_header_height
        pdf.line(x_goals_start, top_y, x_goals_end, top_y)
        pdf.line(x_goals_start, header_bottom_y, x_goals_end, header_bottom_y)
        pdf.line(x_goals_start, header_bottom_y, x_goals_start, top_y)
        pdf.line(x_goals_end, header_bottom_y, x_goals_end, top_y)

        col_width = self.c.goals_area_width / self.c.goals_column_count

        for i, label in enumerate(self.c.goals_labels):
            col_x = x_goals_start + i * col_width
            if i > 0:
                pdf.line(col_x, header_bottom_y, col_x, top_y)

            pdf.setFont(self.c.font_name, self.c.day_font_size)
            pdf.drawCentredString(
                col_x + col_width / 2,
                header_bottom_y + self.c.weekday_header_height / 4,
                label,
            )

    def _draw_month_row(self, pdf: canvas.Canvas, month: int, row_bottom_y: float):
        days_in_month = monthrange(self.c.year, month)[1]
        start_weekday = datetime.date(self.c.year, month, 1).weekday()

        row_left_x = self.c.margin
        row_right_x = (
            row_left_x
            + self.c.month_label_width
            + self.max_day_columns * self.c.day_cell_width
            + self.c.goals_area_width
        )
        row_top_y = row_bottom_y + self.c.month_row_height

        # 1) Fill entire row with the month color
        row_color = (
            self.c.month_colors[month - 1]
            if (month - 1 < len(self.c.month_colors))
            else colors.white
        )
        pdf.setFillColor(row_color)
        pdf.rect(
            row_left_x,
            row_bottom_y,
            row_right_x - row_left_x,
            self.c.month_row_height,
            stroke=0,
            fill=1,
        )

        # 2) Fill weekends in a darker shade
        for day_num in range(1, days_in_month + 1):
            col_idx = start_weekday + (day_num - 1)
            if col_idx % 7 in [5, 6]:  # Sat/Sun
                weekend_color = darken_color(row_color, 0.90)
                x_day = (
                    row_left_x
                    + self.c.month_label_width
                    + col_idx * self.c.day_cell_width
                )
                pdf.setFillColor(weekend_color)
                pdf.rect(
                    x_day,
                    row_bottom_y,
                    self.c.day_cell_width,
                    self.c.month_row_height,
                    stroke=0,
                    fill=1,
                )

        # 3) Now draw the row outline (top, bottom, left boundary)
        pdf.setStrokeColor(colors.CMYKColor(0, 0, 0, 1))
        pdf.setFillColor(colors.CMYKColor(0, 0, 0, 1))
        pdf.line(row_left_x, row_bottom_y, row_right_x, row_bottom_y)
        pdf.line(row_left_x, row_top_y, row_right_x, row_top_y)
        pdf.line(row_left_x, row_bottom_y, row_left_x, row_top_y)

        # vertical line after the month label
        day_col_left_x = row_left_x + self.c.month_label_width
        pdf.line(day_col_left_x, row_bottom_y, day_col_left_x, row_top_y)

        # 4) Now the vertical day lines
        for col in range(self.max_day_columns + 1):
            x_line = day_col_left_x + col * self.c.day_cell_width
            pdf.line(x_line, row_bottom_y, x_line, row_top_y)

        # 5) Finally, draw the month label + day numbers
        # Month label
        pdf.setFont(self.c.font_name, self.c.month_label_size)
        pdf.drawString(
            row_left_x + 0.3 * cm,
            row_bottom_y + self.c.month_row_height - 0.7 * cm,
            datetime.date(self.c.year, month, 1).strftime("%B").upper(),
        )

        # Day numbers
        pdf.setFont(self.c.font_name, self.c.day_font_size)
        for day_num in range(1, days_in_month + 1):
            col_idx = start_weekday + (day_num - 1)
            x_day = day_col_left_x + col_idx * self.c.day_cell_width
            pdf.drawString(
                x_day + 2,
                row_bottom_y + self.c.month_row_height - 0.4 * cm,
                str(day_num),
            )

        # 6) Goals area last
        x_goals_start = day_col_left_x + self.max_day_columns * self.c.day_cell_width
        self._draw_monthly_goals_area(pdf, x_goals_start, row_bottom_y, row_top_y)

    def _draw_monthly_goals_area(
        self, pdf: canvas.Canvas, x_start: float, y_bottom: float, y_top: float
    ):
        pdf.rect(x_start, y_bottom, self.c.goals_area_width, self.c.month_row_height)

        col_width = self.c.goals_area_width / self.c.goals_column_count
        for i in range(self.c.goals_column_count):
            col_x = x_start + i * col_width
            if i > 0:
                pdf.line(col_x, y_bottom, col_x, y_top)

            pdf.setFont(self.c.font_name, self.c.day_font_size)
            top_checkbox_y = y_top - 0.5 * cm
            for j in range(self.c.checkbox_lines_per_column):
                cy = top_checkbox_y - j * (
                    self.c.checkbox_size + self.c.checkbox_line_spacing
                )
                pdf.rect(
                    col_x + 0.3 * cm, cy, self.c.checkbox_size, self.c.checkbox_size
                )
                line_x1 = col_x + 0.3 * cm + self.c.checkbox_size + 0.3 * cm
                line_y = cy + self.c.checkbox_size / 2
                pdf.line(line_x1, line_y, col_x + col_width - 0.3 * cm, line_y)


# --- Example usage ---
if __name__ == "__main__":
    config = AlignedWeekendPlannerConfig(
        year=2025,
        month_colors=[
            colors.HexColor("#fef2f2"),  # Jan - red-50
            colors.HexColor("#fff7ed"),  # Feb - orange-50
            colors.HexColor("#fffbeb"),  # Mar - amber-50
            colors.HexColor("#fefce8"),  # Apr - yellow-50
            colors.HexColor("#f7fee7"),  # May - lime-50
            colors.HexColor("#f0fdf4"),  # Jun - green-50
            colors.HexColor("#f0fdfa"),  # Jul - teal-50
            colors.HexColor("#f0f9ff"),  # Aug - sky-50
            colors.HexColor("#eff6ff"),  # Sep - blue-50
            colors.HexColor("#eef2ff"),  # Oct - indigo-50
            colors.HexColor("#f5f3ff"),  # Nov - violet-50
            colors.HexColor("#faf5ff"),  # Dec - purple-50
        ],
        goals_labels=["Health", "Wealth", "Happiness"],
    )
    planner = AlignedWeekendPlanner(config)
    planner.create_planner("Sweet_Annual_Planner_2025.pdf")
