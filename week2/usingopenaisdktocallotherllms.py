import asyncio
import os

from dotenv import load_dotenv
from agents import Agent, Runner, trace, OpenAIChatCompletionsModel
from openai import AsyncOpenAI
from rich.console import Console

load_dotenv(override=True)
console = Console()

openrouter_api_key = os.getenv("OPEN_ROUTER_API_KEY")

if openrouter_api_key:
    print("OpenRouter API key loaded")
else:
    print("OpenRouter API key does not exist")

message = "Give me a fun fact about Chennai, which hardly people know, even people of Chennai"

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# ✅ OpenRouter client
openrouter_client = AsyncOpenAI(
    base_url=OPENROUTER_BASE_URL,
    api_key=openrouter_api_key,
)

# ✅ Gemini model via OpenRouter
gemini_model = OpenAIChatCompletionsModel(
    model="google/gemini-2.0-flash-001",
    openai_client=openrouter_client
)

instructions = "You give fun facts to users. Give short and crisp fun facts, detailing city asked and origin."

agent = Agent("Gemini Agent, talking about fun facts", instructions=instructions, model=gemini_model)

async def main():
    with trace("Gemini Fun Fact"):
        result = await Runner.run(agent, message)

        console.print("\n[bold green]Response:[/bold green]")
        console.print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main())