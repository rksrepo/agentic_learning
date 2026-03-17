import asyncio

from dotenv import load_dotenv
from agents import Agent, Runner, trace, function_tool
import sendgrid
import os
from sendgrid.helpers.mail import Mail, Email, To, Content, subject

load_dotenv(override=True)

print("\n[INIT] Environment variables loaded")

instructions1 = ("You are sales agent working for ComplAI, "
                 "a company that provides Saas tool for ensuring SOC2 compliance and preparing audits, powered by AI. "
                 "You write professional serious cold emails")

instructions2 = ("You are humorous, engaging sales agent working for ComplAI, "
                 "a company that provides Saas tool for ensuring SOC2 compliance and preparing audits, powered by AI. "
                 "You write witty, engaging cold emails that are likely to get a response.")

instructions3 = ("You are a busy sales agent working for ComplAI, "
                 "a company that provides Saas tool for ensuring SOC2 compliance and preparing audits, powered by AI. "
                 "You write concise, to the point cold emails")

print("[INIT] Instructions defined for email generation by 3 sales agent.")

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

print("[INIT] Sales agents created:",
      sales_agent1.name, ",",
      sales_agent2.name, ",",
      sales_agent3.name)

# How to convert an Agent into a Tool
tool1 = sales_agent1.as_tool(tool_name="sales_agent1", tool_description=instructions1)
tool2 = sales_agent2.as_tool(tool_name="sales_agent2", tool_description=instructions2)
tool3 = sales_agent3.as_tool(tool_name="sales_agent3", tool_description=instructions3)

print("[INIT] Sales tools created")

subject_instructions = ("You can write a subject for cold sales email. You are given a message and you need to write "
                        "a subject for the email that is likely to get a response.")

html_instructions = ("You can convert a text body to HTML email body. You are given a text email body which might have"
                     "some markdown and you need to convert it to an HTML email body with simpler, clear, "
                     "compelling layout and design")

subject_writer = Agent(name="Email Subject Writer",instructions=subject_instructions,model="gpt-4.1-nano")
subject_tool = subject_writer.as_tool(tool_name="subject_writer",tool_description="Write a subject for cold sales email")


html_convertor = Agent(name="HTML email body convertor",instructions=html_instructions,model="gpt-4.1-nano")
html_tool = html_convertor.as_tool(tool_name="html_convertor",tool_description="Convert a text email body to HTML email body")

print("[INIT] Subject + HTML tools ready")

@function_tool
def send_html_email(subject: str, html_body: str):
    """ Send out an email with the given subject and HTML body to all sales prospectors """

    print("\n[TOOL] send_html_email CALLED")
    print("[TOOL] Subject:", subject)
    print("[TOOL] HTML Body (first 200 chars):", html_body[:200])

    sg = sendgrid.SendGridAPIClient(api_key=os.getenv("SENDGRID_API_KEY"))
    from_email = Email("carthikislearning@gmail.com")
    to_email = To("karthikiyer.r@gmail.com")
    content = Content("text/html", html_body)
    mail = Mail(from_email, to_email, subject, content).get()

    print("[TOOL] Sending email via SendGrid...")

    response = sg.client.mail.send.post(request_body=mail)

    print("[TOOL] Email sent. Status Code:", response.status_code)

    return {"status": "success"}

handoff_tools = [subject_tool, html_tool, send_html_email]

instructions = ("You are an email formatter and sender. You receive the body of an email to be sent."
                "You first use the subject_writer tool to write subject for an email, then use html_convertor tool"
                "to convert email body into html. Then use send_html_email tool to send an email with HTML email ")

emailer_agent = Agent(
    name="Emailer Agent",
    instructions=instructions,
    tools=handoff_tools,
    model="gpt-4.1-nano",
    handoff_description="Convert an email to HTML and send it"
)

print("[INIT] Emailer agent ready")

email_generation_tool = [tool1, tool2, tool3]
handoffs = [emailer_agent]

instructions = ("You are a sales manager working for ComplAI. You use tools to generate cold sales emails. You never generate"
                "sales email yourself, you always use only tools. You try all 3 sales_agent tools once before choosing the best one."
                "You can use tools multiple times if you are not satisfied with the results in first try. "
                "You pick the single best email and use send_email tool to send the best email (only the best email to user)."
                "After picking the email you handoff to the Email Manager agent to format and send the email")

sales_manager = Agent(
    name="Sales Manager",
    instructions=instructions,
    tools=email_generation_tool,
    model="gpt-4.1-nano",
    handoffs=handoffs
)

print("[INIT] Sales manager ready")

message = "Send out a cold sales email addressed to Dear CEO from RK"

print("\n[INPUT] Message:", message)

async def main():
    print("\n[START] Running SDR pipeline...\n")

    with trace("Automated SDR"):
        print("[TRACE] Started trace: Automated SDR")

        result = await Runner.run(sales_manager, message)

        print("\n[RESULT] Raw result object:", result)

        try:
            print("\n[RESULT] Final Output:\n", result.final_output)
        except Exception as e:
            print("[ERROR] Could not extract final_output:", str(e))

    print("\n[END] Execution completed")

asyncio.run(main())