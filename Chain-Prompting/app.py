from dotenv import load_dotenv
from google import genai
import os

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

def revision_buddy(user_prompt):
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=user_prompt
    )

    return response.text

summary = revision_buddy("Summarize Operating System basics in 5 bullet points.")
generate_questions=revision_buddy(f"Generate 5 questions based on the {summary} of Operating System basics.")
revision_sheet = revision_buddy(
    f"Create a final revision sheet using this summary and questions.\n"
    f"Summary:\n{summary}\nQuestions:\n{generate_questions}"
)
print("\nREVISION SHEET:\n", revision_sheet)