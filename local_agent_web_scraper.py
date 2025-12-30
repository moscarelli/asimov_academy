from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse

from agno.agent import Agent
from agno.tools.website import WebsiteTools
from agno.models.ollama import Ollama


# ---------------- Configuração ----------------

URL = "https://www.irs.gov/retirement-plans/401k-plans"
OUT_DIR = Path("./out")
OUT_DIR.mkdir(parents=True, exist_ok=True)

model=Ollama(id="granite3.2:2b",host="http://localhost:11434")

agent = Agent(
    model=model,
    tools=[WebsiteTools()],
    instructions="""
You are a content normalizer.

Rules:
- Keep only the main article content
- Ignore headers, footers, banners, navigation and language selectors
- Keep English content only
- Merge all chunks into a single coherent document
- Output clean, well-structured Markdown
- Do not add explanations or comments
"""
)

# ---------------- Execução ----------------

response = agent.run(
    f"Read {URL} and return clean markdown of the main content only."
)

markdown = response.content.strip()

# ---------------- Persistência ----------------

host = (urlparse(URL).hostname or "site").replace(".", "_")
ts = datetime.now().strftime("%Y%m%d-%H%M%S")
md_path = OUT_DIR / f"{host}-401k-{ts}.md"

md_path.write_text(markdown, encoding="utf-8")

print(f"Arquivo gerado com sucesso: {md_path}")


# from agno.agent import Agent
# from agno.tools.website import WebsiteTools
# from agno.models.ollama import Ollama

# model=Ollama(id="granite3.2:2b",host="http://localhost:11434")

# agent = Agent(
#     model=model,
#     tools=[WebsiteTools()],
#     instructions="""
#     You are a content normalizer.
#     - Read the website content
#     - Ignore banners, headers, footers and language selectors
#     - Keep only the main article content in English
#     - Merge all chunks
#     - Output clean Markdown
#     """
# )

# agent.print_response(
#     "Read https://www.irs.gov/retirement-plans/401k-plans and return clean markdown",
#     markdown=True
# )