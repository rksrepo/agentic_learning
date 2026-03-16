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

async def main():
    result = Runner.run_streamed(sales_agent1, input="Write a cold sales email")
    async for event in result.stream_events():
        if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
            print(event.data.delta, end="", flush=True)

asyncio.run(main())