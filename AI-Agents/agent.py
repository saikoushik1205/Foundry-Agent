import os
import requests

from dotenv import load_dotenv

from langchain.agents import create_agent
from langchain.chat_models import init_chat_model

from langchain_tavily import TavilySearch

from langchain.tools import tool


load_dotenv()

google_api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
tavily_api_key = os.getenv("TAVILY_API_KEY")
rapidapi_key = os.getenv("RAPIDAPI_KEY") or os.getenv("RAPID_API_KEY")


model=init_chat_model(
    model="gemini-2.5-flash",
    model_provider="google_genai",
    api_key=google_api_key
)

search_result=TavilySearch(
     max_results=5,
     search_depth="advanced",
     api_key=tavily_api_key,

)

 
@tool
def search_jobs(skill: str, location: str):
    """Search for job listings matching a skill and location."""
    url = "https://job-search4.p.rapidapi.com/api/v1/jobs/search"

    querystring = {"query":skill,"location":location}

    headers = {
        "X-RapidAPI-Key": rapidapi_key,
        "X-RapidAPI-Host": "job-search4.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)

    jobs = response.json().get("jobs", [])

    result=[]

    for job in jobs:
        job_info={
            "title": job.get("title"),
            "company": job.get("company"),
            "location": job.get("location"),
            "description": job.get("description")
        }
        result.append(job_info)

    return result 

system_prompt = """
You are a Skill Mapping Agent.

You help users:

1. Understand skill demand.
2. Understand salary trends.
3. Find jobs.
4. Provide apply links.

Always give structured responses.
"""

agent=create_agent(
    model=model,
    tools=[search_result,search_jobs],
    system_prompt=system_prompt
)

query = """
What's the demand for Generative AI
and show related jobs in India
"""

result=agent.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": query,
            }
        ]
    }
)

final_content = result["messages"][-1].content

if isinstance(final_content, list):
    print("\n".join(part.get("text", "") for part in final_content if part.get("type") == "text"))
else:
    print(final_content)
