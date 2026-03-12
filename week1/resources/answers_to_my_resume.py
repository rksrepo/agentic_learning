from dotenv import load_dotenv
from openai import OpenAI
import gradio as gr
from PyPDF2 import PdfReader
from rich.markdown import Markdown
from rich.console import Console

load_dotenv(override=True)

openai = OpenAI()

reader = PdfReader("MyResume.pdf")
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
console.print(Markdown(system_prompt))

def chat(message, history):
    messages = [{"role": "system", "content": system_prompt}] + history + [{"role": "user", "content": message}]
    response = openai.chat.completions.create(
        model="gpt-4.1-nano",
        messages=messages
    )

    return response.choices[0].message.content

view = gr.ChatInterface(fn=chat,title="About Karthik")
view.launch(inbrowser=True)
