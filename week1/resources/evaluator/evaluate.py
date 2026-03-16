from pydantic import BaseModel
from dotenv import load_dotenv
from openai import OpenAI
import gradio as gr
from PyPDF2 import PdfReader
from rich.markdown import Markdown
from rich.console import Console
import os

load_dotenv(override=True)

openai = OpenAI()

reader = PdfReader("../MyResume.pdf")
resume = ""

for page in reader.pages:
    text = page.extract_text()
    if text:
        resume += text

name = "Karthik Ramakrishnan"

system_prompt = f"""You are acting as {name}. You are answering questions on {name}'s resume particularly questions
related to {name}'s career, background, skills and experience. Your responsibility is to represent {name} for interactions
on the resume as faithfully as possible. You are given latest resume which you can use to answer questions. 
Be professional and engaging, as if talking to a potential client or future employer who came across your resume.
If you don't know the answer say so.

"""

system_prompt += f"Resume page content: \n {resume}\n\n"
system_prompt += f"With this context, please chat with the user, always staying as: {name}."

console = Console()


# console.print(Markdown(system_prompt))


class Evaluation(BaseModel):
    is_acceptable: bool
    feedback: str


evaluator_system_prompt = (f"You are an evaluator that decides whether a response to a question in acceptable."
                           f"You are provided with a conversation between an agent and user. Your task is to decide"
                           f"whether the Agent's latest response is acceptable"
                           f"The Agent is playing the role of {name} and is representing {name} on their profile"
                           f"The Agent has been instructed to be professional and engaging as if talking to future client or employer"
                           f"The Agent has been provided with context as {name} in form of resume details. Here's the information: ")

evaluator_system_prompt += f"Resume content: \n {resume}\n\n"
evaluator_system_prompt += f"With this context, please evaluate the latest response, replying whether the response is acceptable"


def evaluator_user_prompt(reply, message, history):
    user_prompt = f"Here is the conversation between User and Agent: \n\n{history}\n\n"
    user_prompt += f"Here is the latest message from the User: \n\n{message}\n\n"
    user_prompt += f"Here is the latest response from the Agent: \n\n{reply}\n\n"
    user_prompt += f"Please evaluate the response, replying it whether the response is acceptable and your feedback"
    return user_prompt


claude = OpenAI(
    api_key=os.getenv("ANTHROPIC_API_KEY"),
    base_url="https://api.anthropic.com/v1"
)


def evaluate(reply, message, history) -> Evaluation:
    messages = ([{"role": "system", "content": evaluator_system_prompt}] +
                [{"role": "user", "content": evaluator_user_prompt(reply, message, history)}])
    response = claude.beta.chat.completions.parse(
        model="claude-haiku-4-5",
        messages=messages,
        response_format=Evaluation
    )
    return response.choices[0].message.parsed


messages = [{"role": "system", "content": system_prompt}] + [
    {"role": "user", "content": "Do you have AWS Certifications?"}]
response = openai.chat.completions.create(
    model="gpt-4.1-nano",
    messages=messages
)
reply = response.choices[0].message.content

# print(console.print(Markdown(reply)))

evaluatedResponse = evaluate(reply, "I hope you have some GCP certification like you do for AWS?", messages[:1])
# print(console.print(Markdown(evaluatedResponse.feedback)))
# print(evaluatedResponse.is_acceptable)


def rerun(reply, message, history, feedback):
    updated_system_prompt = system_prompt + f"\n\n## Previous answer was rejected\nYou just tried to reply, but the quality control rejected your answer"
    updated_system_prompt += f"## Your attempted answer:\n{reply}\n\n"
    updated_system_prompt += f"## Reason for rejection:\n{feedback}\n\n"
    messages = [{"role": "system", "content": updated_system_prompt}] + history + [{"role": "user", "content": message}]
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )
    return response.choices[0].message.content


def chat(message, history):
    system = system_prompt
    messages = [{"role": "system", "content": system}] + history + [{"role": "user", "content": message}]
    response = openai.chat.completions.create(model="gpt-4.1-nano", messages=messages)
    reply = response.choices[0].message.content
    print(f"Printing before doing evaluation: {reply}")
    evaluation = evaluate(reply, message, history)
    if evaluation.is_acceptable:
        print("Pass evaluation")
    else:
        print("Fail evaluation - retrying")
        print(evaluation.feedback)
        reply = rerun(reply, message, history, evaluation.feedback)
        print(f"Printing after doing evaluation: {reply}")
    return reply


view = gr.ChatInterface(fn=chat,title="About Karthik")
view.launch(inbrowser=True)