from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task, before_kickoff
from crewai_tools import FileReadTool
import json
import os
from typing import List, Dict, Any
from datetime import date, datetime

from gmail_crew_ai.tools.gmail_tools import (
    GetUnreadEmailsTool, SaveDraftTool, GmailOrganizeTool, 
    GmailDeleteTool, GmailArchiveTool, EmptyTrashTool
)
from gmail_crew_ai.tools.slack_tool import SlackNotificationTool
from gmail_crew_ai.tools.calendar_tool import CalendarAvailabilityTool
from gmail_crew_ai.models import (
    CategorizedEmail, OrganizedEmail, EmailResponse, 
    SlackNotification, EmailCleanupInfo, SimpleCategorizedEmail, EmailDetails
)
from gmail_crew_ai.utils import is_vip_sender, log_decision
from gmail_crew_ai.style_analyzer import get_user_writing_style

@CrewBase
class GmailCrewAi():
    """Crew that processes emails."""
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    @before_kickoff
    def fetch_emails(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch emails before starting the crew, calculate ages, and apply VIP rules."""
        print("Fetching emails before starting the crew...")
        
        email_limit = inputs.get('email_limit', 5)
        print(f"Fetching {email_limit} emails...")
        
        os.makedirs("output", exist_ok=True)
        
        email_tool = GetUnreadEmailsTool()
        email_tuples = email_tool._run(limit=email_limit)
        
        emails = []
        today = date.today()
        for email_tuple in email_tuples:
            email_detail = EmailDetails.from_email_tuple(email_tuple)
            
            if email_detail.date:
                try:
                    email_date_obj = datetime.strptime(email_detail.date, "%Y-%m-%d").date()
                    email_detail.age_days = (today - email_date_obj).days
                except Exception as e:
                    print(f"Error calculating age for email date {email_detail.date}: {e}")
                    email_detail.age_days = None
            
            # Check VIP sender override
            is_vip = is_vip_sender(email_detail.sender or "")
            email_dict = email_detail.dict()
            email_dict["is_vip"] = is_vip
            emails.append(email_dict)
        
        with open('output/fetched_emails.json', 'w', encoding='utf-8') as f:
            json.dump(emails, f, indent=2, ensure_ascii=False)
        
        print(f"Fetched and saved {len(emails)} emails to output/fetched_emails.json")
        return inputs
    
    model_name = os.getenv("MODEL", "gemini/gemini-2.0-flash")
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY") or "placeholder_key"
    
    llm = LLM(
        model=model_name,
        api_key=api_key,
    )

    @agent
    def categorizer(self) -> Agent:
        """The email categorizer agent."""
        return Agent(
            config=self.agents_config['categorizer'],
            tools=[FileReadTool()],
            llm=self.llm,
        )

    @agent
    def organizer(self) -> Agent:
        """The email organization agent."""
        return Agent(
            config=self.agents_config['organizer'],
            tools=[GmailOrganizeTool(), FileReadTool()],
            llm=self.llm,
        )
        
    @agent
    def response_generator(self) -> Agent:
        """The email response generator agent."""
        return Agent(
            config=self.agents_config['response_generator'],
            tools=[SaveDraftTool(), CalendarAvailabilityTool()],
            llm=self.llm,
        )
    
    @agent
    def notifier(self) -> Agent:
        """The email notification agent."""
        return Agent(
            config=self.agents_config['notifier'],
            tools=[SlackNotificationTool()],
            llm=self.llm,
        )

    @agent
    def cleaner(self) -> Agent:
        """The email cleanup agent."""
        return Agent(
            config=self.agents_config['cleaner'],
            tools=[GmailDeleteTool(), GmailArchiveTool(), EmptyTrashTool()],
            llm=self.llm,
        )

    @task
    def categorization_task(self) -> Task:
        """The email categorization task."""
        return Task(
            config=self.tasks_config['categorization_task'],
            output_pydantic=SimpleCategorizedEmail
        )
    
    @task
    def organization_task(self) -> Task:
        """The email organization task."""
        return Task(
            config=self.tasks_config['organization_task'],
            output_pydantic=OrganizedEmail,
        )

    @task
    def response_task(self) -> Task:
        """The email response task."""
        return Task(
            config=self.tasks_config['response_task'],
            output_pydantic=EmailResponse,
        )
    
    @task
    def notification_task(self) -> Task:
        """The email notification task."""
        return Task(
            config=self.tasks_config['notification_task'],
            output_pydantic=SlackNotification,
        )

    @task
    def cleanup_task(self) -> Task:
        """The email cleanup task."""
        return Task(
            config=self.tasks_config['cleanup_task'],
            output_pydantic=EmailCleanupInfo,
        )

    @crew
    def crew(self) -> Crew:
        """Creates the email processing crew."""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )
