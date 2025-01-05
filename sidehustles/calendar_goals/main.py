from dataclasses import dataclass
from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, A3
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from calendar import monthrange
import datetime


@dataclass
class AlignedWeekendPlannerConfig:
    year: int

    # Page Layout
    page_size: tuple[float, float] = landscape(A3)
    margin: float = 0.5 * cm

    # Extra space on the left to place the month name
    month_label_width: float = 3 * cm

    # The height of the top row that shows "Mon, Tue, Wed..."
    weekday_header_height: float = 0.7 * cm

    # Day columns and month rows
    day_cell_width: float = 0.90 * cm
    month_row_height: float = 2 * cm

    # Goals area: 3 columns (Health, Wealth, Relationships),
    # each with some checkboxes
    goals_area_width: float = 5.5 * cm
    goals_column_count: int = (
        3  # number of columns, e.g. 3 = Health, Wealth, Relationships
    )
    checkbox_size: float = 0.30 * cm
    checkbox_line_spacing: float = 0.1 * cm
    checkbox_lines_per_column: int = 4

    # Fonts and sizes
    font_name: str = "Helvetica"
    title_size: int = 30
    month_label_size: int = 12
    day_font_size: int = 8
    # We don't actually need a separate goals_label_size if the monthly rows
    # won't display column labels. We'll keep it anyway in case you want it.
    goals_label_size: int = 8

    # Colors
    highlight_weekend_color = colors.whitesmoke


class AlignedWeekendPlanner:
    def __init__(self, config: AlignedWeekendPlannerConfig):
        self.c = config
        self.width, self.height = config.page_size
        self.styles = getSampleStyleSheet()
        self._setup_styles()

        # Up to 37 or 38 columns for all possible start-days + 31 days
        # We'll do 36 or so if you prefer fewer.
        self.max_day_columns = 36

        # Short day-of-week names for the header
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
        """Generate the PDF file."""
        pdf = canvas.Canvas(output_path, pagesize=self.c.page_size)

        # 1) Draw the overall title at the very top
        self._draw_title(pdf)

        # 2) Draw the annual goals just below the title
        #    This can be a rectangle or lines for writing, etc.
        annual_goals_bottom = self._draw_annual_goals(pdf)

        # 3) Draw the day-of-week header row below the Annual Goals
        header_top_y = annual_goals_bottom - self.c.weekday_header_height + 0.2 * cm
        self._draw_weekday_header(pdf, header_top_y)

        # 4) Draw the goals header (Health, Wealth, Relationships)
        #    aligned with the day-of-week row on the right side
        self._draw_goals_header(pdf, header_top_y)

        # 5) The first month row starts below the weekday header
        top_y_for_months = header_top_y - 2.7 * cm

        for month_index in range(12):
            row_y = top_y_for_months - (month_index * self.c.month_row_height)
            self._draw_month_row(pdf, month_index + 1, row_y)

        pdf.save()

    def _draw_title(self, pdf: canvas.Canvas):
        """Draw the main title at the top center."""
        pdf.setFont(self.c.font_name, self.c.title_size)
        pdf.drawCentredString(
            self.width / 2,
            self.height - 1.0 * cm,  # or self.c.margin if you prefer
            f"Sweet Annual Planner {self.c.year}",
        )

    def _draw_annual_goals(self, pdf: canvas.Canvas) -> float:
        """
        Draw a section labeled "Annual Goals" (or any text you want) below the title,
        return the y-coordinate for the bottom of this section.
        """
        top_y = self.height - 2.0 * cm  # a bit below the title
        box_height = 2.0 * cm  # how tall you want the annual goals box

        # Outline a rectangle
        pdf.setStrokeColor(colors.black)
        pdf.rect(
            self.c.margin,
            top_y - box_height,
            self.width - 2 * self.c.margin,
            box_height,
        )

        # Optional: label "ANNUAL GOALS"
        pdf.setFont(self.c.font_name, 14)
        pdf.drawString(self.c.margin + 0.3 * cm, top_y - 0.5 * cm, "ANNUAL GOALS:")

        # Return the bottom y of this box
        return top_y - box_height

    def _draw_weekday_header(self, pdf: canvas.Canvas, top_y: float):
        """
        Draw the row of weekday names across columns 0..max_day_columns,
        shifted right by month_label_width so it doesn't overlap the month label.
        """
        pdf.setFont(self.c.font_name, self.c.day_font_size)
        bottom_y = top_y - self.c.weekday_header_height

        # The day columns start after the month_label_width
        day_col_left_x = self.c.margin + self.c.month_label_width
        day_col_right_x = day_col_left_x + self.max_day_columns * self.c.day_cell_width

        # Horizontal lines for top & bottom of the header row
        pdf.setStrokeColor(colors.black)
        # Top line
        pdf.line(day_col_left_x, top_y, day_col_right_x, top_y)
        # Bottom line
        pdf.line(day_col_left_x, bottom_y, day_col_right_x, bottom_y)

        # Also a vertical line at the left to separate the month-label area
        pdf.line(self.c.margin, bottom_y, self.c.margin, top_y)  # left boundary
        # Another line at day_col_left_x to separate month label from days
        pdf.line(day_col_left_x, bottom_y, day_col_left_x, top_y)

        # And a vertical line at the right edge
        pdf.line(day_col_right_x, bottom_y, day_col_right_x, top_y)

        # For columns 0..max_day_columns, draw vertical lines + day-of-week labels
        for col_idx in range(self.max_day_columns + 1):
            x_line = day_col_left_x + col_idx * self.c.day_cell_width
            # The vertical lines inside the range
            pdf.line(x_line, bottom_y, x_line, top_y)

            if col_idx < self.max_day_columns:
                # short day name
                dow_label = self.short_dow[col_idx % 7]
                pdf.drawCentredString(
                    x_line + self.c.day_cell_width / 2,
                    bottom_y + (self.c.weekday_header_height / 4),
                    dow_label,
                )

    def _draw_goals_header(self, pdf: canvas.Canvas, top_y: float):
        """
        Draw a single row at the top for the goals columns labels:
        "Health", "Wealth", "Relationships" only once,
        aligned with the day-of-week row on the far right.
        """
        # The day columns end at:
        day_col_left_x = self.c.margin + self.c.month_label_width
        day_col_right_x = day_col_left_x + self.max_day_columns * self.c.day_cell_width

        # So the goals area is from day_col_right_x .. day_col_right_x + goals_area_width
        x_goals_start = day_col_right_x
        x_goals_end = x_goals_start + self.c.goals_area_width

        header_bottom_y = top_y - self.c.weekday_header_height
        # We'll outline it similarly to the day-of-week row
        pdf.line(x_goals_start, top_y, x_goals_end, top_y)
        pdf.line(x_goals_start, header_bottom_y, x_goals_end, header_bottom_y)
        # Vertical boundaries
        pdf.line(x_goals_start, header_bottom_y, x_goals_start, top_y)
        pdf.line(x_goals_end, header_bottom_y, x_goals_end, top_y)

        # Now draw 3 columns inside
        col_width = self.c.goals_area_width / self.c.goals_column_count
        labels = ["Health", "Wealth", "Relationships"]

        for i, label in enumerate(labels):
            col_x = x_goals_start + i * col_width
            # vertical line
            if i > 0:
                pdf.line(col_x, header_bottom_y, col_x, top_y)

            # label (centered in that sub-column)
            pdf.setFont(self.c.font_name, self.c.day_font_size)
            # just place it near the middle
            pdf.drawCentredString(
                col_x + col_width / 2,
                header_bottom_y + self.c.weekday_header_height / 4,
                label,
            )

    def _draw_month_row(self, pdf: canvas.Canvas, month: int, y: float):
        """
        Draw a single row for the given month:
          - Outline on the left for month label
          - Aligned days in columns
          - a vertical line at day_col_left_x
          - highlight weekends
          - a goals area on the right with checkboxes only (no titles)
        """
        days_in_month = monthrange(self.c.year, month)[1]
        start_weekday = datetime.date(self.c.year, month, 1).weekday()

        # BOUNDING LINES for the month row
        row_left_x = self.c.margin
        row_right_x = (
            self.c.margin
            + self.c.month_label_width
            + self.max_day_columns * self.c.day_cell_width
            + self.c.goals_area_width
        )
        top_y = y + self.c.month_row_height

        # 1) top & bottom lines
        pdf.line(row_left_x, top_y, row_right_x, top_y)
        pdf.line(row_left_x, y, row_right_x, y)
        # 2) left vertical boundary
        pdf.line(row_left_x, y, row_left_x, top_y)
        # 3) vertical line between the month label & day columns
        day_col_left_x = row_left_x + self.c.month_label_width
        pdf.line(day_col_left_x, y, day_col_left_x, top_y)

        # 4) Month label inside that left box
        pdf.setFont(self.c.font_name, self.c.month_label_size)
        month_str = datetime.date(self.c.year, month, 1).strftime("%B").upper()
        label_x = row_left_x + 0.3 * cm
        label_y = y + self.c.month_row_height - 0.7 * cm
        pdf.drawString(label_x, label_y, month_str)

        # 5) Draw each day
        for day_num in range(1, days_in_month + 1):
            col_idx = start_weekday + (day_num - 1)
            x_day = day_col_left_x + col_idx * self.c.day_cell_width

            # highlight weekend
            if col_idx % 7 in [5, 6]:  # sat, sun
                pdf.setFillColor(self.c.highlight_weekend_color)
                pdf.rect(
                    x_day,
                    y,
                    self.c.day_cell_width,
                    self.c.month_row_height,
                    stroke=0,
                    fill=1,
                )
                pdf.setFillColor(colors.black)

            # day number
            pdf.setFont(self.c.font_name, self.c.day_font_size)
            pdf.drawString(
                x_day + 2, y + self.c.month_row_height - 0.3 * cm, str(day_num)
            )

        # 6) vertical lines for day columns
        pdf.setStrokeColor(colors.black)
        for col in range(self.max_day_columns + 1):
            x_line = day_col_left_x + col * self.c.day_cell_width
            pdf.line(x_line, y, x_line, top_y)

        # 7) The goals area on the right
        x_goals_start = day_col_left_x + self.max_day_columns * self.c.day_cell_width
        self._draw_monthly_goals_area(pdf, x_goals_start, y, top_y)

    def _draw_monthly_goals_area(
        self, pdf: canvas.Canvas, x_start: float, y_bottom: float, y_top: float
    ):
        """
        Draw the monthly goals box with only checkboxes (no "Health/Wealth/Relationships" label).
        """
        # Outline
        pdf.rect(x_start, y_bottom, self.c.goals_area_width, self.c.month_row_height)

        # We have 3 columns, but for each month row, we only place checkboxes
        column_width = self.c.goals_area_width / self.c.goals_column_count
        for i in range(self.c.goals_column_count):
            col_x = x_start + i * column_width
            # internal vertical line
            if i > 0:
                pdf.line(col_x, y_bottom, col_x, y_top)

            # place checkboxes
            pdf.setFont(self.c.font_name, self.c.day_font_size)
            top_checkbox_y = y_top - 0.5 * cm
            for j in range(self.c.checkbox_lines_per_column):
                cy = top_checkbox_y - j * (
                    self.c.checkbox_size + self.c.checkbox_line_spacing
                )
                # checkbox
                pdf.rect(
                    col_x + 0.3 * cm, cy, self.c.checkbox_size, self.c.checkbox_size
                )
                # line for writing
                line_x1 = col_x + 0.3 * cm + self.c.checkbox_size + 0.3 * cm
                line_y = cy + self.c.checkbox_size / 2
                pdf.line(line_x1, line_y, col_x + column_width - 0.3 * cm, line_y)


# --- Example Usage ---
if __name__ == "__main__":
    config = AlignedWeekendPlannerConfig(year=2025)
    planner = AlignedWeekendPlanner(config)
    planner.create_planner("Sweet_Annual_Planner_2025.pdf")
