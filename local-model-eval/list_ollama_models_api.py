import requests

def list_ollama_models():
    """Lists all locally available Ollama models using the Ollama API."""
    try:
        response = requests.get("http://localhost:11434/api/tags")
        response.raise_for_status()
        data = response.json()
        print("Locally available Ollama models:")
        for model in data.get('models', []):
            print(f"- {model.get('name', 'unknown')} (size: {model.get('size', 'unknown')})")
    except requests.ConnectionError:
        print("Could not connect to Ollama API at http://localhost:11434. Is Ollama running?")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    list_ollama_models()
