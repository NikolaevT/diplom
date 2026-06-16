from typing import List

from crewai import Agent, Crew, Process, Task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.project import CrewBase, agent, crew, task

from src.task_manager.dto.chat_summary import Topics
from src.task_manager.flow.llm_factory import build_crew_llm, crew_agent_kwargs


@CrewBase
class TopicAnalyzeCrew:
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
    def topic_analyze_agent(self) -> Agent:
        """Агент для анализа тем в диалогах"""
        return Agent(
            config=self.agents_config["topic_analyze_agent"],
            llm=self._llm,
            verbose=True,
            **self._agent_kwargs,
        )

    @task
    def analyze_messages(self) -> Task:
        """Задача анализа сообщений и извлечения тем"""
        return Task(
            config=self.tasks_config["analyze_messages"],
            agent=self.topic_analyze_agent(),
            output_pydantic=Topics,
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
