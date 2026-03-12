import os
import json
import openai
from dotenv import load_dotenv
from openai import OpenAI
from anthropic import Anthropic
from rich.console import Console

load_dotenv(override=True)

openai_api_key = os.getenv("OPENAI_API_KEY")
anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
google_api_key = os.getenv("GOOGLE_API_KEY")

if openai_api_key:
    print(f"OPENAI_API_KEY exists and begins with : {openai_api_key[:8]}")
else:
    print(f"OPENAI_API_KEY doesn't exist")

if anthropic_api_key:
    print(f"ANTHROPIC_API_KEY exists and begins with : {anthropic_api_key[:7]}")
else:
    print(f"ANTHROPIC_API_KEY doesn't exist")

if google_api_key:
    print(f"GOOGLE_API_KEY exists and begins with : {google_api_key[:2]}")
else:
    print(f"GOOGLE_API_KEY doesn't exist")

print("All API Keys loaded from environment variables\n")

openai_client = OpenAI(api_key=openai_api_key)
competitors = []
answers = []


def create_question_by_gpt_nano(client) -> str:
    request = (
        "Please come up with a challenging nuanced question that I can ask "
        "a number of LLMs to evaluate their intelligence. "
        "Answer only with the question, no explanation."
    )

    response = client.chat.completions.create(
        model="gpt-4.1-nano",
        messages=[{"role": "user", "content": request}],
    )
    question_by_llm = response.choices[0].message.content
    print("Now asking GPT to create a question to be answered by various LLMs\n")
    return question_by_llm


question = create_question_by_gpt_nano(openai_client)
messages = [{"role": "user", "content": question}]


def answer_question_by_gpt_mini(client, question_to_gpt) -> str:
    print("Now asking GPT LLM to answer\n")
    messages_to_gpt = [{"role": "user", "content": question_to_gpt}]
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=messages_to_gpt
    )
    return response.choices[0].message.content

def answer_question_by_anthropic(question_to_anthropic) -> str:
    print("Now asking Anthropic LLM to answer\n")
    claude = Anthropic(api_key=anthropic_api_key)
    messages_to_anthropic = [{"role": "user", "content": question_to_anthropic}]
    response = claude.messages.create(
        model="claude-haiku-4-5",
        messages=messages_to_anthropic,
        max_tokens=1000
    )
    return response.content[0].text

def answer_question_by_gemini(question_to_gemini) -> str:
    print("Now asking Gemini LLM to answer\n")
    gemini = OpenAI(base_url="https://generativelanguage.googleapis.com/v1beta/openai/", api_key=google_api_key)
    messages_to_gemini = [{"role": "user", "content": question_to_gemini}]
    response = gemini.chat.completions.create(
        model="gemini-2.5-flash",
        messages=messages_to_gemini)

    return response.choices[0].message.content


answer_by_gpt = answer_question_by_gpt_mini(openai_client, question)
competitors.append("gpt-4.1-mini")
answers.append(answer_by_gpt)

answer_by_anthropic = answer_question_by_anthropic(question)
competitors.append("claude-haiku-4-5")
answers.append(answer_by_anthropic)

answer_by_gemini = answer_question_by_gemini(question)
competitors.append("gemini-2.5-flash")
answers.append(answer_by_gemini)


console = Console()

# print("\n\n===== LLM ANSWERS =====\n")

results = {
    "gpt-4.1-mini": answer_by_gpt,
    "claude-haiku-4-5": answer_by_anthropic,
    "gemini-2.5-flash": answer_by_gemini
}

together = ""
for idx, (model, answer) in enumerate(results.items(), start=1):
    together += f"Response from competitor {idx}\n\n"
    together += answer + "\n\n"


judge = f""" You are judging a competition between {len(competitors)} competitors.
Each model has been given with question:
{question}

Your job is to evaluate each response for clarity and strength of argument, and rank them in order of best to worst.
Respond with JSON, and only JSON with the following format:
{{"results": ["Best competitor number", "Second best competitor number", ...]}}

Here are the responses from each competitor:

{together}

Now respond with the JSON with the ranked order of competitors, nothing else. Do not include markdown formatting or code blocks.

"""

judge_messages = [{"role": "user", "content": judge}]

response = openai.chat.completions.create(
    model="gpt-4.1-mini",
    messages=judge_messages
)

results = response.choices[0].message.content

print("\nFinal Ranking:\n")

results_dicts = json.loads(results)
ranks = results_dicts["results"]
for rank, result in enumerate(ranks):
    model_name = competitors[int(result)-1]
    print(f"{rank+1}: {model_name}")