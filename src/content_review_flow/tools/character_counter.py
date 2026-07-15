from typing import Type

from pydantic import BaseModel, Field

from crewai.tools import BaseTool


class CharacterCounterToolInput(BaseModel):
    """Input schema for CharacterCounterTool."""

    text: str = Field(..., description="The text to count the characters of.")


class CharacterCounterTool(BaseTool):
    name: str = "Character Counter Tool"
    description: str = "Counts the number of characters in the given text."
    args_schema: Type[BaseModel] = CharacterCounterToolInput

    def _run(self, text: str) -> str:
        return f"Number of characters: {len(text)}"
