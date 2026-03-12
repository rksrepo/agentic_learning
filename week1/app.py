from dotenv import load_dotenv
import os
from openai import OpenAI
from rich.markdown import Markdown
from rich.console import Console

load_dotenv(override=True)

openai_api_key = os.getenv("OPENAI_API_KEY")

if openai_api_key:
    print(f"OPENAI_API_KEY exists and begins with : {openai_api_key[:8]}")
else:
    print(f"OPENAI_API_KEY doesn't exist")

openai = OpenAI(api_key=openai_api_key)

messages = [{"role": "user", "content": "What is 2+2?"}]

response = openai.chat.completions.create(
    model="gpt-4.1-nano",
    messages=messages
)

print("First test call to LLM using OpenAI library")
print(response.choices[0].message.content)
print("********************************************************************************")
question = "Please propose a hard, challenging question to assess someone's IQ from an Indian context. Respond only with the question"
messages = [{"role": "user", "content": question}]

response = openai.chat.completions.create(
    model="gpt-4.1-nano",
    messages=messages
)

print("Asking an LLM to give a question to test someone's IQ")
print(response.choices[0].message.content)
print("********************************************************************************")


messages = [{"role": "user", "content": response.choices[0].message.content}]

response = openai.chat.completions.create(
    model="gpt-4.1-nano",
    messages=messages
)

answer = response.choices[0].message.content
print("Now asking the same OpenAI to answer the question")
console = Console()
console.print(Markdown(answer))
print("********************************************************************************")