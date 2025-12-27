from agno.agent import Agent
from agno.tools.tavily import TavilyTools
from agno.models.openai import OpenAIChat


from dotenv import load_dotenv
load_dotenv()

agent = Agent(
    model= OpenAIChat(id="gpt-5-mini-2025-08-07") ,
    tools=[TavilyTools()],
    debug_mode=True
)

agent.print_response("use suas ferramentas para pesquisar a temperatura de hoje em Capõ da canoa")
