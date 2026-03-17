import asyncio

from dotenv import load_dotenv
from agents import Agent, Runner, trace, function_tool
from openai.types.responses import ResponseTextDeltaEvent
from typing import Dict
import sendgrid
import os, json
from sendgrid.helpers.mail import Mail, Email, To, Content, subject

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
#
# asyncio.run(main())


sales_picker = Agent(
    name="Sales Picker",
    instructions="You pick the best cold emails from the given options. Imagine you are a customer"
                 "and pick the one you are most likely to respond to. Do not give explanation, reply"
                 "with selected email only"
)

# async def main():
#     message = "Write a cold sales email"
#
#     with trace("Selection from sales people"):
#         results = await asyncio.gather(
#             Runner.run(sales_agent1, message),
#             Runner.run(sales_agent2, message),
#             Runner.run(sales_agent3, message)
#         )
#
#         outputs = [result.final_output for result in results]
#
#         emails = "Cold Sales email:\n\n".join(outputs)
#
#         best = await Runner.run(sales_picker, emails)
#
#         print(f"Best sales email:\n{best.final_output}")


# if __name__ == "__main__":
#     asyncio.run(main())


@function_tool
def send_email(body: str):
    """ Send out an email with the given body to all sales prospectors """

    sg = sendgrid.SendGridAPIClient(api_key=os.getenv("SENDGRID_API_KEY"))
    from_email = Email("carthikislearning@gmail.com")
    to_email = To("karthikiyer.r@gmail.com")
    content = Content("text/plain", body)
    mail = Mail(from_email, to_email, "Sales Email", content).get()
    response = sg.client.mail.send.post(request_body=mail)
    return {"status": "success"}

# How to convert an Agent into a Tool
tool1 = sales_agent1.as_tool(tool_name="sales_agent1", tool_description=instructions1)
tool2 = sales_agent1.as_tool(tool_name="sales_agent2", tool_description=instructions2)
tool3 = sales_agent1.as_tool(tool_name="sales_agent3", tool_description=instructions3)

tools = [tool1, tool2, tool3, send_email]

print(tools)


instructions = ("You are a sales manager working for ComplAI. You use tools to generate cold sales emails. You never generate"
                "sales email yourself, you always use only tools. You try all 3 sales_agent tools once before choosing the best one."
                "You pick the single best email and use send_email tool to send the best email (only the best email to user)")

sales_manager = Agent(
    name="Sales Manager",
    instructions=instructions,
    tools=tools,
    model="gpt-4.1-nano"
)

message = "Send a cold sales email addressed to Dear CEO"

async def main():
    with trace("Sales Manager"):
        results = await Runner.run(sales_manager, message)
        print(results.final_output)

if __name__ == "__main__":
    asyncio.run(main())