from typing import List

from crewai import Agent, Crew, Process, Task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.project import CrewBase, agent, crew, task

from src.task_manager.dto.chat_summary import TaskSummary
from src.task_manager.flow.llm_factory import build_crew_llm, crew_agent_kwargs


@CrewBase
class TaskSummaryCrew:
    """Crew для анализа тем в диалогах"""

    agents: List[BaseAgent]
    tasks: List[Task]

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    def __init__(self):
        """Инициализация Crew с настройками LLM"""
        super().__init__()
        self._llm = build_crew_llm()
        self._agent_kwargs = crew_agent_kwargs()

    @agent
    def task_summary_agent(self) -> Agent:
        """Агент для постановки задачи"""
        return Agent(
            config=self.agents_config["task_summary_agent"],
            llm=self._llm,
            verbose=True,
            **self._agent_kwargs,
        )

    @task
    def task_summary(self) -> Task:
        """Задача выделения заголовка и описания для задачи"""
        return Task(
            config=self.tasks_config["task_summary"],
            agent=self.task_summary_agent(),
            output_pydantic=TaskSummary,
        )

    @crew
    def crew(self) -> Crew:
        """Создание и настройка Crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
