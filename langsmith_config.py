import os

def setup_langsmith_config():
    os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com" # Update with your API URL if using a hosted instance of Langsmith.
    os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY") # Update with your API key
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    project_name = "GPT-4-VISION-DEMO" # Update with your project name
    os.environ["LANGCHAIN_PROJECT"] = project_name # Optional: "default" is used if not set