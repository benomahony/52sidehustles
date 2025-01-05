from dataclasses import dataclass
from reportlab.lib import colors
from reportlab.lib.pagesizes import A3
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from calendar import monthcalendar, month_name


@dataclass
class CalendarConfig:
    year: int
    page_size: tuple[float, float] = A3
    margin: float = 1 * cm
    cell_height: float = 1.2 * cm
    cell_width: float = 2 * cm
    goals_height: float = 8 * cm
    font_name: str = "Helvetica"
    title_size: int = 24
    header_size: int = 14
    body_size: int = 10


class YearCalendar:
    def __init__(self, config: CalendarConfig) -> None:
        self.config = config
        self.width, self.height = config.page_size
        self.styles = getSampleStyleSheet()
        self._setup_styles()

    def _setup_styles(self) -> None:
        """Set up custom paragraph styles for the calendar."""
        self.styles.add(
            ParagraphStyle(
                name="GoalHeader",
                fontName=self.config.font_name,
                fontSize=self.config.header_size,
                spaceAfter=5,
                spaceBefore=5,
            )
        )

    def _draw_goals_section(self, pdf: canvas.Canvas, y_position: float) -> None:
        """Draw the goals section at the top of the calendar."""
        # Goals box
        pdf.setStrokeColor(colors.black)
        pdf.rect(
            self.config.margin,
            y_position,
            self.width - 2 * self.config.margin,
            self.config.goals_height,
        )

        # Goals header
        pdf.setFont(self.config.font_name, self.config.header_size)
        pdf.drawString(
            self.config.margin + 0.5 * cm,
            y_position + self.config.goals_height - 2 * cm,
            "YEARLY GOALS",
        )

        # Goal categories
        categories = ["Personal:", "Professional:", "Health:", "Financial:"]
        y = y_position + self.config.goals_height - 3 * cm
        for category in categories:
            pdf.setFont(self.config.font_name, self.config.body_size)
            pdf.drawString(self.config.margin + cm, y, category)
            # Draw a line for writing
            pdf.line(
                self.config.margin + 4 * cm,
                y,
                self.width - 2 * self.config.margin - cm,
                y,
            )
            y -= 1 * cm

    def _draw_month(
        self,
        pdf: canvas.Canvas,
        month: int,
        x: float,
        y: float,
        width: float,
        height: float,
    ) -> None:
        """Draw a single month in the calendar grid."""
        # Month header
        pdf.setFont(self.config.font_name, self.config.header_size)
        pdf.drawString(x, y + height - 0.8 * cm, month_name[month])

        # Week headers
        days = "Mo Tu We Th Fr Sa Su".split()
        pdf.setFont(self.config.font_name, self.config.body_size)
        for i, day in enumerate(days):
            pdf.drawString(
                x + i * self.config.cell_width + 2, y + height - 1.5 * cm, day
            )

        # Calendar days
        cal = monthcalendar(self.config.year, month)
        for week_num, week in enumerate(cal):
            for day_num, day in enumerate(week):
                if day != 0:
                    pdf.drawString(
                        x + day_num * self.config.cell_width + 2,
                        y + height - (2.5 + week_num) * cm,
                        str(day),
                    )

    def create_calendar(self, output_path: str) -> None:
        """Generate the complete calendar PDF."""
        pdf = canvas.Canvas(output_path, pagesize=self.config.page_size)

        # Draw title
        pdf.setFont(self.config.font_name, self.config.title_size)
        pdf.drawCentredString(
            self.width / 2, self.height - 2 * cm, f"Calendar {self.config.year}"
        )

        # Draw goals section
        self._draw_goals_section(pdf, self.height - 3 * cm - self.config.goals_height)

        # Calculate grid layout
        months_start_y = (
            self.height - 3 * cm - self.config.goals_height - self.config.margin
        )
        month_height = (months_start_y - self.config.margin) / 3
        month_width = (self.width - 2 * self.config.margin) / 4

        # Draw months grid
        for i in range(12):
            row = i // 4
            col = i % 4
            x = self.config.margin + col * month_width
            y = months_start_y - (row + 1) * month_height
            self._draw_month(pdf, i + 1, x, y, month_width, month_height)

        pdf.save()


if __name__ == "__main__":
    config = CalendarConfig(year=2025)
    calendar = YearCalendar(config)
    calendar.create_calendar("year_calendar_2025.pdf")
