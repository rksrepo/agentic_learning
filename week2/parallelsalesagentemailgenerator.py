import asyncio

from dotenv import load_dotenv
from agents import Agent, Runner, trace, function_tool
from openai.types.responses import ResponseTextDeltaEvent
from typing import Dict
import sendgrid
import os, json
from sendgrid.helpers.mail import Mail, Email, To, Content

load_dotenv(override=True)

instructions1 = ("You are sales agent working for ComplAI, "
                 "a company that provides Saas tool for ensuring SOC2 compliance and preparing audits, powered by AI. "
                 "You write professional serious cold emails")

instructions2 = ("You are humorous, engaging sales agent working for ComplAI, "
                 "a company that provides Saas tool for ensuring SOC2 compliance and preparing audits, powered by AI. "
                 "You write witty, engaging cold emails that are likely to get a response.")

instructions3 = ("You are a busy sales agent working for ComplAI, "
                 "a company that provides Saas tool for ensuring SOC2 compliance and preparing audits, powered by AI. "
                 "You write concise, to the point cold emails")


sales_agent1 = Agent(
    name="Professional Sales Agent",
    instructions=instructions1,
    model="gpt-4.1-nano"
)

sales_agent2 = Agent(
    name="Engaging Sales Agent",
    instructions=instructions2,
    model="gpt-4.1-nano"
)

sales_agent3 = Agent(
    name="Busy Sales Agent",
    instructions=instructions3,
    model="gpt-4.1-nano"
)

message = "Write a cold sales email"

# async def main():
#     with trace("Parallel cold emails"):
#         results = await asyncio.gather(
#             Runner.run(sales_agent1, message),
#             Runner.run(sales_agent2, message),
#             Runner.run(sales_agent3, message)
#         )
#
#     for r in results:
#         print("\n-------------------\n")
#         print(r.final_output)

# asyncio.run(main())


sales_picker = Agent(
    name="Sales Picker",
    instructions="You pick the best cold emails from the given options. Imagine you are a customer"
                 "and pick the one you are most likely to respond to. Do not give explanation, reply"
                 "with selected email only"
)

async def main():
    message = "Write a cold sales email"

    with trace("Selection from sales people"):
        results = await asyncio.gather(
            Runner.run(sales_agent1, message),
            Runner.run(sales_agent2, message),
            Runner.run(sales_agent3, message)
        )

        outputs = [result.final_output for result in results]

        emails = "Cold Sales email:\n\n".join(outputs)

        best = await Runner.run(sales_picker, emails)

        print(f"Best sales email:\n{best.final_output}")


if __name__ == "__main__":
    asyncio.run(main())