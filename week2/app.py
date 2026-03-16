import asyncio

from dotenv import load_dotenv
from agents import Agent, Runner, trace
from rich.console import Console
from rich.pretty import Pretty

load_dotenv(override=True)
console = Console()

# Here the instructions is the system prompt to the LLM
agent = Agent(
    name="My First OpenAI SDK Agent",
    instructions="Being my first agent, you answer very simple questions about OpenAI SDK",
    model="gpt-4.1-nano"
)

# console.print(Pretty(vars(agent)))


async def main():
    with trace("About OpenAI SDK Agent"):
        result = await Runner.run(
            agent,
            "What is OpenAI SDK, what all should I know to get started and also to become an expert?"
        )
        print(result.final_output)



asyncio.run(main())

# result = Runner.run_sync(agent, "What is OpenAI SDK, what all should I know to get started and also to become an expert?")
# print(result.final_output)

