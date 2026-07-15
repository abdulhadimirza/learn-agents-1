from pydantic import BaseModel
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

from content_review_flow.tools.character_counter import CharacterCounterTool

class ReviewResult(BaseModel):
    score: int
    feedback: str

@CrewBase
class ReviewerCrew:
    """Reviewer Crew for the content review flow."""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def reviewer(self) -> Agent:
        return Agent(  # type: ignore
            config=self.agents_config["reviewer"],  # type: ignore
            tools=[CharacterCounterTool()],
            verbose=True
        )

    @task
    def review_task(self) -> Task:
        return Task(  # type: ignore
            config=self.tasks_config["review_task"],  # type: ignore
            output_pydantic=ReviewResult
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,  # type: ignore
            tasks=self.tasks,  # type: ignore
            process=Process.sequential,
            verbose=True,
        )
