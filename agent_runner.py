import os
import requests
from dotenv import load_dotenv
from autogen import AssistantAgent, UserProxyAgent, register_function

# Load API keys from .env
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

# AutoGen config for Groq LLM
config_list = [
    {
        "model": "llama-3.3-70b-versatile",  # Groq's model name (corrected)
        "api_key": GROQ_API_KEY,
        "api_type": "groq",
        "temperature": 0.7,
        "max_tokens": 1000
    }
]

# Global counter for API calls
api_call_count = 0

# ✅ Define Weather Tool Function
def get_weather(city: str) -> str:
    """Get current weather for a city using WeatherAPI"""
    global api_call_count
    api_call_count += 1
    
    print(f"🌤️  WEATHER TOOL CALLED: Getting weather for '{city}' (Call #{api_call_count})")
    
    url = "http://api.weatherapi.com/v1/current.json"
    params = {
        "key": WEATHER_API_KEY,
        "q": city
    }
    
    print(f"📡 Making API request to: {url}")
    print(f"📋 Request params: {params}")
    
    try:
        print("⏳ Sending request...")
        response = requests.get(url, params=params)
        
        print(f"✅ Response received!")
        print(f"📊 Status Code: {response.status_code}")
        print(f"📄 Response Headers: {dict(response.headers)}")
        
        data = response.json()
        print(f"📦 Response Data: {data}")
        
        if "error" in data:
            error_msg = f"API Error: {data['error'].get('message', 'Unknown error')}"
            print(f"❌ {error_msg}")
            return error_msg
            
        temp = data['current']['temp_c']
        condition = data['current']['condition']['text']
        result = f"Weather in {city}: {temp}°C, {condition}"
        #print(f"🌟 Final result: {result}")
        return data
        
    except Exception as e:
        error_msg = f"❌ Exception occurred: {str(e)}"
        print(f"💥 {error_msg}")
        return error_msg

# ✅ Create agents with tool
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

    # ✅ Register the weather function for both agents
    register_function(
        get_weather,
        caller=assistant,
        executor=user_proxy,
        name="get_weather",
        description="""Get the current weather information for a given city using WeatherAPI.
        Return important details such as:
        - city, region, and country
        - temperature in Celsius and Fahrenheit
        - feels-like temperature
        - humidity and wind (with direction and speed)
        - cloud coverage, UV index, and visibility
        - pressure, dew point, and precipitation
        - location coordinates (latitude and longitude)
        Respond with a well-structured and user-friendly weather summary."""
    )

    return assistant, user_proxy

# ✅ Communication Logic
def chat_with_agent(query: str):
    assistant, user_proxy = create_thinking_agent()

    print(f"\n🧠 Query: {query}")
    print("=" * 60)

    result = user_proxy.initiate_chat(
        assistant,
        message=query,
        silent=False
    )
    return result


