from pydantic import BaseModel

from app.providers.base import AIProvider


class MockProvider(AIProvider):
    name = "mock"

    def __init__(
        self,
        model: str = "modelo-mock",
        structured_response: BaseModel | dict | None = None,
        simulated_error: Exception | None = None,
    ) -> None:
        self.model = model
        self.structured_response = structured_response
        self.simulated_error = simulated_error
        self.prompts: list[str] = []

    async def run_structured(
        self, prompt: str, schema: type[BaseModel], temperature: float = 0.2
    ) -> BaseModel | None:
        self.prompts.append(prompt)
        if self.simulated_error is not None:
            raise self.simulated_error
        if self.structured_response is None:
            return None
        if isinstance(self.structured_response, BaseModel):
            return self.structured_response
        return schema.model_validate(self.structured_response)
