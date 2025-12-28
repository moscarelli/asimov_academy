from agno.agent import Agent
from agno.models.ollama import Ollama

agent = Agent(
    model=Ollama(
       id="tinyllama:1.1b",
       #id="phi:2.7b",
       host="http://localhost:11434"
    ),
    description="Agent to test local exeuciont of agno code with local llm models"
)

agent.print_response("Hello, are you aware?", verbose=True,stream=True)
