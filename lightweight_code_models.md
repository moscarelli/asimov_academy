# Lightweight Code Analysis Models

A list of open-source models suitable for code analysis and business rules extraction, with approximate RAM requirements (for quantized versions where available):

| Model Name         | Parameters | Quantized Version | Approx. RAM Needed | Notes / Recommendation                |
|--------------------|------------|-------------------|--------------------|---------------------------------------|
| tinyllama:1.1b     | 1.1B       | Q4                | ~2 GB              | Very lightweight, good for simple tasks (**Recommended**) |
| phi:2.7b           | 2.7B       | -                 | ~3 GB              | Lightweight, strong for code/logic (**Recommended**)      |
| Llama-2 7B         | 7B         | Q4                | ~4–5 GB            | Good general-purpose, use quantized   |
| Llama-3 8B         | 8B         | Q4                | ~5 GB              | Newer, good for reasoning, use quantized |
| Mistral-7B         | 7B         | Q4                | ~4–5 GB            | Strong code/reasoning, use quantized  |
| CodeGemma-7B       | 7B         | Q4                | ~6 GB              | Heavier, not recommended for low RAM  |


## Ollama commands and model names
Use these model names to download and run with Ollama:
```bash
ollama run tinyllama:1.1b
ollama run phi:2.7b
ollama run llama2:7b-q4
ollama run llama3:8b-q4
ollama run mistral:7b-q4
```

**Summary:**
- For low RAM, start with **TinyLlama-1.1B** or **Phi-2**.
- For larger models, try **Llama-2 7B Q4**, **Llama-3 8B Q4**, or **Mistral-7B Q4**.
- Avoid CodeGemma-7B unless you have >6 GB free RAM.
