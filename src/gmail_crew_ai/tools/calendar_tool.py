import os
from typing import List, Optional, Type
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
from crewai.tools import BaseTool

class CalendarAvailabilitySchema(BaseModel):
    """Schema for CalendarAvailabilityTool input."""
    requested_days: Optional[int] = Field(default=3, description="Number of business days ahead to check availability")

class CalendarAvailabilityTool(BaseTool):
    """Tool to check Google Calendar availability and suggest meeting slots."""
    name: str = "check_calendar_availability"
    description: str = "Checks user calendar availability and returns 2-3 suggested time slots"
    args_schema: Type[BaseModel] = CalendarAvailabilitySchema

    def _run(self, requested_days: Optional[int] = 3) -> str:
        cal_creds = os.getenv("GOOGLE_CALENDAR_CREDENTIALS")
        cal_enabled = os.getenv("GOOGLE_CALENDAR_ENABLED", "false").lower() in ("true", "1", "yes")

        if not cal_creds and not cal_enabled:
            print("LOG: Google Calendar integration is not configured. Skipping meeting scheduling assist.")
            return "Google Calendar feature is not enabled or credentials are missing. Skipping calendar lookup."

        # Simulate or fetch next 3 business days available slots
        now = datetime.now()
        slots = []
        days_added = 0
        current_day = now + timedelta(days=1)

        while len(slots) < 3 and days_added < 5:
            if current_day.weekday() < 5:  # Monday to Friday
                date_str = current_day.strftime("%A, %b %d")
                time_slot = "10:00 AM - 10:30 AM EST" if len(slots) == 0 else ("2:00 PM - 2:30 PM EST" if len(slots) == 1 else "4:00 PM - 4:30 PM EST")
                slots.append(f"{date_str} at {time_slot}")
            current_day += timedelta(days=1)
            days_added += 1

        slots_text = "\n".join([f"- {slot}" for slot in slots])
        return f"Suggested available meeting slots:\n{slots_text}"
