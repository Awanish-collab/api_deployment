# agent_runner.py
import os
import requests
from dotenv import load_dotenv
from autogen import AssistantAgent, UserProxyAgent, register_function

# Load API keys (Render will set these as env vars)
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

config_list = [
    {
        "model": "llama3-70b-8192",  # Correct Groq model name
        "api_key": GROQ_API_KEY,
        "api_type": "groq",
        "temperature": 0.7,
        "max_tokens": 1000
    }
]

def get_weather(city: str) -> str:
    url = "http://api.weatherapi.com/v1/current.json"
    params = {
        "key": WEATHER_API_KEY,
        "q": city
    }
    try:
        response = requests.get(url, params=params)
        data = response.json()
        if "error" in data:
            return f"API Error: {data['error'].get('message', 'Unknown error')}"
        temp = data['current']['temp_c']
        condition = data['current']['condition']['text']
        return f"Weather in {city}: {temp}°C, {condition}"
    except Exception as e:
        return f"❌ Exception occurred: {str(e)}"

def create_thinking_agent():
    assistant = AssistantAgent(
        name="ThinkingAgent",
        system_message="""
        You are a smart assistant who solves problems step-by-step.
        Use tools when external data is needed.
        Always explain your reasoning and steps.""",
        llm_config={"config_list": config_list}
    )

    user_proxy = UserProxyAgent(
        name="User",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=5,
        is_termination_msg=lambda x: "TERMINATE" in str(x.get("content", "")) if x else False,
        code_execution_config={"use_docker": False}
    )

    register_function(
        get_weather,
        caller=assistant,
        executor=user_proxy,
        name="get_weather",
        description="Get current weather for a city using WeatherAPI"
    )

    return assistant, user_proxy

def chat_with_agent(query: str):
    assistant, user_proxy = create_thinking_agent()
    result = user_proxy.initiate_chat(
        assistant,
        message=query,
        silent=True
    )
    return result.summary if hasattr(result, 'summary') else str(result)
