import asyncio
import os

from dotenv import load_dotenv
from agents import Agent, Runner, trace, OpenAIChatCompletionsModel
from openai import AsyncOpenAI
from rich.console import Console

load_dotenv(override=True)
console = Console()

claude_api_key = os.getenv("ANTHROPIC_API_KEY")

if claude_api_key:
    print("Anthropic api key loaded")
else:
    print("Anthropic api key does not exist")

message = "Give me a fun fact about Chennai, which hardly people know, even people of Chennai"

ANTHROPIC_BASE_URL = "https://api.anthropic.com/v1/"

anthropic_client = AsyncOpenAI(base_url=ANTHROPIC_BASE_URL, api_key=claude_api_key)

anthropic_model = OpenAIChatCompletionsModel(model="claude-haiku-4-5", openai_client=anthropic_client)

instructions = "You give fun facts to users. Give short and crisp fun facts, detailing city asked and origin."

agent = Agent("Claude Agent, talking about fun facts", instructions=instructions, model=anthropic_model)

async def main():
    with trace("Claude Fun Fact"):
        result = await Runner.run(agent, message)

        console.print("\n[bold green]Response:[/bold green]")
        console.print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main())