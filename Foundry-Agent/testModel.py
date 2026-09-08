from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

# endpoint = "https://weather-agent-koushik-1.services.ai.azure.com/openai/v1"
endpoint = "https://weather-agent-koushik-1.services.ai.azure.com/openai/v1"
deployment_name = "gpt-5-mini-2"
api_key = os.getenv("AZURE_OPENAI_KEY")

client = OpenAI(
    base_url=endpoint,
    api_key=api_key
)

response = client.responses.create(
    model=deployment_name,
    input="What is the capital of France?",
)

print(f"answer: {response.output_text}")
