import os
from dotenv import load_dotenv
load_dotenv()
from groq import Groq
import json
import requests

client = Groq(
    api_key = os.getenv('GROQ_API_KEY')
)

def get_weather(location):
 api_key = os.getenv('WEATHER_API_KEY')
 url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&units=metric&appid={api_key}"
 response = requests.get(url)
 data = response.json()

 if data.get("cod") == 200:
    return json.dumps({
      "location": location,
      "temperature": data["main"]["temp"],
      "description": data["weather"][0]["description"]
    })
 else:
    return json.dumps({"Oops! Something went wrong."})

tools = [
  {
    "type": "function",
    "function": {
      "name": "get_weather",
      "description": "Get current weather for a city",
      "parameters": {
        "type": "object",
        "properties": {
          "location": {
            "type": "string",
            "description": "City name like Mumbai, London"
            }
            },
      "required": ["location"]
           }
       }
   }
]

llm_messages = [
  {
    "role": "system",
    "content": "You are a weather assistant. Use get_weather function when asked about weather."
  },
  {
    "role": "user",
    "content": "What's the weather in Mumbai?"
  }
]

response = client.chat.completions.create(
  model="llama-3.3-70b-versatile",
  messages=llm_messages,
  tools=tools,
  tool_choice="auto"
)

response_message = response.choices[0].message
print(response_message.content)


if response_message.tool_calls:
  tool_call = response_message.tool_calls[0]
  arguments = json.loads(tool_call.function.arguments)
  location = arguments['location']
  weather_data = get_weather(location)

  llm_messages.append(response_message)

  llm_messages.append({
      "role": "tool",
      "tool_call_id": tool_call.id,
      "content": json.dumps(weather_data)
  })

  final_response = client.chat.completions.create(
      messages = llm_messages,
      model = "llama-3.3-70b-versatile",
      tools = tools,
      tool_choice = "auto"
  )

  print(final_response.choices[0].message.content)