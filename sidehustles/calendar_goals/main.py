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
    weekday_header_height: float = 1.0 * cm

    # Day columns and month rows
    day_cell_width: float = 0.90 * cm
    month_row_height: float = 2.0 * cm

    # Goals area: we’ll create 3 labeled columns (Health, Wealth, Relationships)
    # each with some checkboxes
    goals_area_width: float = 2.0 * cm
    goals_column_count: int = 1
    checkbox_size: float = 0.30 * cm
    checkbox_line_spacing: float = 0.1 * cm
    checkbox_lines_per_column: int = 4  # how many checkboxes in each goal column

    # Fonts and sizes
    font_name: str = "Helvetica"
    title_size: int = 30
    month_label_size: int = 12
    day_font_size: int = 8
    goals_label_size: int = 0

    # Colors
    highlight_weekend_color = colors.whitesmoke


class AlignedWeekendPlanner:
    def __init__(self, config: AlignedWeekendPlannerConfig):
        self.c = config
        self.width, self.height = config.page_size
        self.styles = getSampleStyleSheet()
        self._setup_styles()

        # We’ll allow up to 38 columns (index 0..37) for days:
        # (If a month starts Sunday (6) and has 31 days => last day at col 6+30=36;
        #  so 37 or 38 columns is just a safe margin.)
        self.max_day_columns = 36

        # Short day-of-week names to show on the header
        # aligned to col % 7 => 0=Monday, 1=Tuesday, etc.
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

        # 2) Draw the day-of-week header row just below the title
        header_top_y = self.height - self.c.margin - self.c.weekday_header_height
        self._draw_weekday_header(pdf, header_top_y)

        # 3) Where the first month row starts (below the weekday header)
        top_y_for_months = header_top_y - 3 * cm  # small gap

        for month_index in range(12):
            # row_y descends for each month
            row_y = top_y_for_months - (month_index * self.c.month_row_height)
            self._draw_month_row(pdf, month_index + 1, row_y)

        pdf.save()

    def _draw_title(self, pdf: canvas.Canvas):
        """Draw the main title at the top center."""
        pdf.setFont(self.c.font_name, self.c.title_size)
        pdf.drawCentredString(
            self.width / 2,
            self.height - 2 * self.c.margin,
            f"Sweet Annual Planner {self.c.year}",
        )

    def _draw_annual_goals(self, pdf: canvas.Canvas) -> None:
        """
        Draw the Annual goals at the top below tht title
        """

    def _draw_weekday_header(self, pdf: canvas.Canvas, top_y: float):
        """
        Draw the row of weekday names across columns 0..self.max_day_columns,
        shifted right by self.c.month_label_width so it doesn't overlap the month label.
        """
        pdf.setFont(self.c.font_name, self.c.day_font_size)

        bottom_y = top_y - self.c.weekday_header_height

        # The day columns start after the month_label_width
        day_col_left_x = self.c.margin + self.c.month_label_width
        day_col_right_x = day_col_left_x + self.max_day_columns * self.c.day_cell_width

        # Horizontal lines for top & bottom of the header row
        pdf.setStrokeColor(colors.black)
        pdf.line(day_col_left_x, top_y, day_col_right_x, top_y)
        pdf.line(day_col_left_x, bottom_y, day_col_right_x, bottom_y)

        # For columns 0..max_day_columns, draw vertical lines + day-of-week labels
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

    def _draw_month_row(self, pdf: canvas.Canvas, month: int, y: float):
        """
        Draw a single row for the given month:
          - Month label on the left (width = month_label_width)
          - Aligned days in columns (shifted by month_label_width)
          - Vertical lines for each day, highlight weekends
          - 3 goals columns on the right
        """
        days_in_month = monthrange(self.c.year, month)[1]
        start_weekday = datetime.date(self.c.year, month, 1).weekday()

        pdf.setFont(self.c.font_name, self.c.month_label_size)
        month_str = datetime.date(self.c.year, month, 1).strftime("%B").upper()
        pdf.drawString(self.c.margin, y + self.c.month_row_height - 0.7 * cm, month_str)

        day_col_left_x = self.c.margin + self.c.month_label_width

        for day_num in range(1, days_in_month + 1):
            col_idx = start_weekday + (day_num - 1)  # 0-based
            x_day = day_col_left_x + col_idx * self.c.day_cell_width

            # Highlight weekend if col_idx % 7 in [5,6] => Sat=5, Sun=6
            if col_idx % 7 in [5, 6]:
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

            # Draw the day number
            pdf.setFont(self.c.font_name, self.c.day_font_size)
            pdf.drawString(
                x_day + 2, y + self.c.month_row_height - 0.3 * cm, str(day_num)
            )

        # 3) Draw vertical lines for day columns
        pdf.setStrokeColor(colors.black)
        for col in range(self.max_day_columns + 1):
            x_line = day_col_left_x + col * self.c.day_cell_width
            pdf.line(x_line, y, x_line, y + self.c.month_row_height)

        # 4) Also draw top/bottom bounding lines
        # The bounding lines should go from the *left edge* of the entire row
        # to day columns + goals area
        row_left_x = self.c.margin
        row_right_x = (
            day_col_left_x
            + self.max_day_columns * self.c.day_cell_width
            + self.c.goals_area_width
        )

        pdf.line(
            row_left_x,
            y + self.c.month_row_height,
            row_right_x,
            y + self.c.month_row_height,
        )
        pdf.line(
            row_left_x,
            y,
            row_right_x,
            y,
        )

        x_goals_start = day_col_left_x + self.max_day_columns * self.c.day_cell_width
        self._draw_goals_area(pdf, x_goals_start, y)

    def _draw_goals_area(self, pdf: canvas.Canvas, x_start: float, y: float):
        """
        Draw 3 columns side by side: Health, Wealth, Relationships,
        each with a few checkboxes.
        """
        column_width = self.c.goals_area_width / self.c.goals_column_count

        # Outline the entire goals area
        pdf.rect(x_start, y, self.c.goals_area_width, self.c.month_row_height)

        labels = ["Health", "Wealth", "Relationships"]
        for i, label in enumerate(labels):
            col_x = x_start + i * column_width
            # Internal vertical line between columns
            if i > 0:
                pdf.line(col_x, y, col_x, y + self.c.month_row_height)

            # Label near the top
            pdf.setFont(self.c.font_name, self.c.goals_label_size)
            pdf.drawString(col_x + 2, y + self.c.month_row_height - 0.6 * cm, label)

            # Place checkboxes
            pdf.setFont(self.c.font_name, self.c.day_font_size)
            top_checkbox_y = y + self.c.month_row_height - 0.5 * cm
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

        # Right boundary for the last column
        pdf.line(
            x_start + self.c.goals_area_width,
            y,
            x_start + self.c.goals_area_width,
            y + self.c.month_row_height,
        )


# --- Example Usage ---
if __name__ == "__main__":
    config = AlignedWeekendPlannerConfig(year=2025)
    planner = AlignedWeekendPlanner(config)
    planner.create_planner("Sweet_Annual_Planner_2025.pdf")
