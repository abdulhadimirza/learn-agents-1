from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

@CrewBase
class WriterCrew:
    """Writer Crew for the self healing flow."""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def writer(self) -> Agent:
        return Agent(  # type: ignore
            config=self.agents_config["writer"],  # type: ignore
            verbose=True
        )

    @task
    def drafting_task(self) -> Task:
        return Task(  # type: ignore
            config=self.tasks_config["drafting_task"]  # type: ignore
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,  # type: ignore
            tasks=self.tasks,  # type: ignore
            process=Process.sequential,
            verbose=True,
        )
