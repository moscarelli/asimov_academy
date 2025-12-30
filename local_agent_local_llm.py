# import os
# os.environ["CUDA_VISIBLE_DEVICES"] = ""
from agno.agent import Agent
from agno.models.ollama import Ollama
from agno.tools.yfinance import YFinanceTools
from agno.db.sqlite import SqliteDb
from agno.knowledge.knowledge import Knowledge
from agno.knowledge.reader.pdf_reader import PDFReader
from agno.knowledge.chunking.semantic import SemanticChunking
from agno.knowledge.embedder.ollama   import OllamaEmbedder
from agno.vectordb.chroma import ChromaDb
#from agno.models.openai import OpenAIChat
#from airllm import AutoModel
import logging
#from huggingface_hub import hf_hub_download
# from dotenv import load_dotenv
# load_dotenv()


logging.basicConfig(level=logging.INFO)

# ADP Annual Report url https://investors.adp.com/financials/annual-reports/default.aspx
db=SqliteDb(db_file="tmp/pdfreaderagent.db")
#model = AutoModel.from_pretrained("meta-llama/Meta-Llama-3-8B-Instruct")
#modelLLM = AutoModel.from_pretrained("mistralai/Mistral-7B-Instruct-v0.2")


#embeddings =OllamaEmbedder(id="nomic-embed-text", host="http://localhost:11434",dimensions=768, timeout=30)
embeddings =OllamaEmbedder(id="llama3.2:latest", host="http://localhost:11434",dimensions=3072, timeout=30)

#RAG with PDF Reader
vector_db = ChromaDb(
    collection="pdf_docs",
    #embedder=OllamaEmbedder(id="granite3.1-moe", dimensions=1536),
    embedder=embeddings,
    persistent_client=True,
    path="tmp/chroma_pdfreaderagent",
    
)

# Create knowledge base from PDF
knowledge = Knowledge(
    vector_db=vector_db,
)

knowledge.add_content(
    path="pdfs/adp-fy24-10-k.pdf",
    reader=PDFReader(
        chunking_strategy=SemanticChunking(
            chunk_size=350   # moderate chunk size (words or tokens, adjust as needed
        )
    ),
    metadata={
        "source": "ADP FY24 report",
        "sector": "HR Solutions",
        "country": "US"
    },
    skip_if_exists=False
)
results = vector_db.search("PEO Services", limit=10)
for i, d in enumerate(results, 1):
    meta = getattr(d, "metadata", None)
    content = getattr(d, "content", "") or ""
    print(f"\n--- RESULT {i} ---")
    print("METADATA:", meta)
    print("CONTENT:", content[:500])
#### Models with no tools #####
# openhermes:latest
# nomic-embed-text:latest
# llama3:8b
# llama2:7b
# phi:2.7b
# tinyllama:1.1b
# codegemma:7b
###############################
#### avoid models ###
# llama3.2:3b - to much memory consuption take long time to return information.
# mistral:7b-instruct - to much memory consuption take long time to return information.
# qwen2.5:1.5b-instruct - - to much memory consuption take long time to return information.
# llama3.2:latest - to much memory consuption take long time to return information.
# mistral:7b - to much memory consuption take long time to return information.
#######################

### possible models #####
# the models bellow doesn't obey instructions to return in json
# granite3.1-moe:latest - takes time, works but still return not needed information and hallucinate.
# llama3.2:1b-instruct-q5_1 - takes time, works but still return not needed information and hallucinate.
# granite3.1-dense:2b-instruct-q5_1 - takes time, works but still return not needed information and hallucinate.
# granite3.2:2b
############################
agent = Agent(
    debug_mode=True,
    tool_choice= "auto",
    session_id="local_agent_local_llm",
    user_id="test_user",
    name="Local Agent with Local LLM",
    #model=OpenAIChat(id="gpt-5-mini"),
    #model=modelLLM,
    model=Ollama(id="llama3.2:latest",host="http://localhost:11434", format="json",  
        # options={
        #     "temperature": 0.1,
        #     "top_p": 0.8,
        #     "top_k": 40,
        #     "repeat_penalty": 1.15,
        #     "num_predict": 256,
        #     "num_ctx": 4096,
        # }
        ## fast option
#         options={
#   "temperature": 0.1, "top_p": 0.8, "top_k": 20, "repeat_penalty": 1.12,
#   "num_ctx": 1024, "num_predict": 128,
#   "num_threads": 8, "num_batch": 64,
#   "keep_alive": "10m",
# }
      ## fast but more acurate
#        options={
#   "temperature": 0.1, "top_p": 0.9, "top_k": 30, "repeat_penalty": 1.10,
#   "num_ctx": 2048, "num_predict": 256,
#   "num_threads": 8, "num_batch": 96,
#   "keep_alive": "10m",
#    "format":"json",  
# }
    ),
    tools=[
        YFinanceTools()
    ],
    db=db,
    add_culture_to_context=True,
    enable_agentic_culture=True,
    knowledge=knowledge,
    add_knowledge_to_context=True,
    instructions="Do not summarize;For document questions, answer ONLY using the provided knowledge context; if the answer is not explicitly supported, reply exactly 'NOT FOUND IN DATABASE' and do not guess.",
    description="Agent to test local exeuciont of agno code with local llm models"
)

agent.print_response(
    "What is 2024 PEO services value ?If is not explicitly present in the provided context, return {\"value\": null, \"evidence\": null}.",
    verbose=False,
    stream=True,
    session_id="local_agent_local_llm",
    user_id="test_user"
)
