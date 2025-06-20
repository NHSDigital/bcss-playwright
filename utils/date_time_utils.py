from datetime import datetime, timedelta
from typing import Optional
import random


class DateTimeUtils:
    """
    A utility class for doing common actions with datetimes.
    """

    @staticmethod
    def current_datetime(format_date: str = "%d/%m/%Y %H:%M") -> str:
        """Gets the current datetime in the specified format.

        Args:
            format_date (str): [Optional] The format to return the current datetime in. Defaults to dd/mm/yyyy hh:mm if not provided.

        Returns:
            str: The current datetime in the specified format.
        """
        return datetime.now().strftime(format_date)

    @staticmethod
    def format_date(date: datetime, format_date: str = "%d/%m/%Y") -> str:
        """Formats a specified datetime object.

        Args:
            date (datetime): The date to be formatted.
            format_date (str): [Optional] The format to return the datetime in. Defaults to dd/mm/yyyy if not provided.

        Returns:
            str: The formatted date in the specified format.
        """
        return date.strftime(format_date)

    @staticmethod
    def add_days(date: datetime, days: float) -> datetime:
        """Adds a specified number of days to a specified date.

        Args:
            date (datetime): The date to which the days will be added.
            days (float): The number of days to add to the specified date.

        Returns:
            datetime: The specified date plus the number of specified days (year, month, day, hour, minute, second, microsecond).
        """
        return date + timedelta(days=days)

    @staticmethod
    def get_day_of_week(date: Optional[datetime] = None) -> str:
        """
        Returns the day of the week (e.g., Monday, Tuesday) for the given date.
        If no date is provided, uses today’s date.

        Args:
            date (Optional[datetime]): The date to inspect. Defaults to now.

        Returns:
            str: Day of week corresponding to the date.
        """
        date = date or datetime.now()
        return date.strftime("%A")

    @staticmethod
    def report_timestamp_date_format() -> str:
        """Gets the current datetime in the timestamp format used on the report pages.
        Returns:
            str: The current date and time in the format 'dd/mm/yyyy at hh:mm:ss'.
            e.g. '24/01/2025 at 12:00:00'
        """

        return DateTimeUtils.format_date(datetime.now(), "%d/%m/%Y at %H:%M:%S")

    @staticmethod
    def fobt_kits_logged_but_not_read_report_timestamp_date_format() -> str:
        """Gets the current datetime in the format used for FOBT Kits Logged but Not Read report.
        Returns:
            str: The current date and time in the format 'dd MonthName yyyy hh:mm:ss'.
            e.g. '24 Jan 2025 12:00:00'
        """

        return DateTimeUtils.format_date(datetime.now(), "%d %b %Y %H:%M:%S")

    @staticmethod
    def screening_practitioner_appointments_report_timestamp_date_format() -> str:
        """Gets the current datetime in the format used for the screening practitioner appointments report.
        Returns:
            str: the current datetime in the format 'dd.mm.yyyy at hh:mm:ss'
            e.g. '24.01.2025 at 12:00:00'
        """

        return DateTimeUtils.format_date(datetime.now(), "%d.%m.%Y at %H:%M:%S")

    @staticmethod
    def month_string_to_number(string: str) -> int:
        """
        This is used to convert a month from a string to an integer.
        It accepts the full month or the short version and is not case sensitive
        """
        months = {
            "jan": 1,
            "feb": 2,
            "mar": 3,
            "apr": 4,
            "may": 5,
            "jun": 6,
            "jul": 7,
            "aug": 8,
            "sep": 9,
            "oct": 10,
            "nov": 11,
            "dec": 12,
        }
        month_short = string.strip()[:3].lower()

        try:
            out = months[month_short]
            return out
        except Exception:
            raise ValueError(
                f"'{string}' is not a valid month name. Accepted values are: {', '.join(months.keys())}"
            )

    @staticmethod
    def generate_unique_weekday_date(start_year: int = 2025) -> str:
        """
        Returns a random future weekday (Mon–Fri) date from the given year onward.

        The result is in 'dd/mm/yyyy' format and useful for automated tests needing
        unique, non-weekend dates. Uses non-cryptographic randomness for variability between runs.

        Args:
            start_year (int): The minimum year from which the date may be generated. Defaults to 2025.

        Returns:
            str: A future weekday date in the format 'dd/mm/yyyy'.
        """
        # Start from tomorrow to ensure future date
        base_date = datetime.now() + timedelta(days=1)

        # Keep moving forward until we find a weekday in 2025 or later
        while True:
            if base_date.weekday() < 5 and base_date.year >= start_year:
                break
            base_date += timedelta(days=1)

        # Add randomness to avoid repeated values across runs
        base_date += timedelta(days=random.randint(0, 10))

        # Re-check for weekday after shift
        while base_date.weekday() >= 5:
            base_date += timedelta(days=1)

        return base_date.strftime("%d/%m/%Y")
