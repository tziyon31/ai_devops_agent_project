import os
import openai
import re
from dotenv import load_dotenv

# 🔒 Load your OpenAI key
load_dotenv()
openai.api_key = os.getenv("OPEN_AI_API_KEY")
MODEL = "gpt-4o"

# 🧠 Send prompt to OpenAI
def call_openai(prompt: str) -> str:
    response = openai.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    return response.choices[0].message.content

# 🔍 Parse ReAct block
def extract_react_block(text: str) -> dict:
    block_match = re.search(r"<start>(.*?)<end>", text, re.DOTALL)
    if not block_match:
        raise ValueError("❌ No valid ReAct block found.")

    block_text = block_match.group(1)
    thought = re.search(r"Thought:\s*(.*)", block_text)
    action = re.search(r"Action:\s*(.*)", block_text)
    observation = re.search(r"Observation:\s*(.*)", block_text)

    return {
        "thought": thought.group(1).strip() if thought else "",
        "action": action.group(1).strip() if action else "",
        "observation": observation.group(1).strip() if observation else "",
    }

# 🧱 Build full prompt from history (includes ask_user blocks)
def build_full_prompt(history: list, input_text: str) -> str:
    intro = (
        "You are an AI agent using ReAct logic.\n"
        "Your role is:\n"
        "👉 TODO: describe your agent’s job clearly.\n"
        "You can use actions like:\n"
        "👉 TODO: list the allowed actions here (e.g. search_docs, ask_user, summarize_section, suggest_fix).\n"
        "Use this format only:\n"
        "<start>\nThought: ...\nAction: ...\nObservation: ...\n<end>\n"
        "If you use ask_user(\"...\"), stop and wait.\n"
    )

    input_block = f"<input>\n{input_text}\n</input>\n\n"

    history_block = "\n".join([
        f"<start>\nThought: {h['thought']}\nAction: {h['action']}\nObservation: {h['observation']}\n<end>"
        for h in history
    ])

    return intro + history_block + "\n" + input_block

# 🧱 Partial prompt that skips "ask_user" waiting blocks
def build_prompt_until_question(history: list, input_text: str) -> str:
    intro = (
        "You are an AI agent using ReAct logic.\n"
        "Your role is:\n"
        "👉 TODO: describe your agent’s job clearly.\n"
        "You can use actions like:\n"
        "👉 TODO: list allowed actions.\n"
        "Use this format only:\n"
        "<start>\nThought: ...\nAction: ...\nObservation: ...\n<end>\n"
        "If you use ask_user(\"...\"), stop and wait.\n"
    )

    input_block = f"<input>\n{input_text}\n</input>\n\n"
    block_list = []

    for h in history:
        if h['action'].startswith("ask_user") and h['observation'] == "Waiting for user input.":
            break
        block_list.append(
            f"<start>\nThought: {h['thought']}\nAction: {h['action']}\nObservation: {h['observation']}\n<end>"
        )

    history_block = "\n".join(block_list)
    return intro + history_block + "\n" + input_block

# 🧪 Simulate agent actions
def simulate_action(action: str, input_text: str) -> str:
    # TODO: Add your custom action logic here
    if action == "read_input()":
        return input_text
    elif action.startswith("search_docs("):
        term = re.search(r'search_docs\("(.*?)"\)', action)
        keyword = term.group(1) if term else "unknown"
        return f"📚 Simulated result: Found related documentation for '{keyword}'."
    elif action == "suggest_fix()":
        return "✅ Fix suggested successfully."
    else:
        return "🤔 Unknown action."

# 🎯 Agent loop
def react_agent(input_text: str):
    history = []

    while True:
        # ⏸️ If waiting for user response
        if history and history[-1]["action"].startswith("ask_user") and history[-1]["observation"] == "Waiting for user input.":
            question = re.search(r'ask_user\("(.*?)"\)', history[-1]["action"])
            question_text = question.group(1) if question else "Please answer:"
            print(f"\n🤖 Agent asks: {question_text}")
            user_input = input("🧑 Your answer: ")
            history[-1]["observation"] = user_input
            continue

        # 🤔 Choose prompt building strategy
        waiting_for_input = any(
            h["action"].startswith("ask_user") and h["observation"] == "Waiting for user input."
            for h in history
        )
        prompt = build_prompt_until_question(history, input_text) if waiting_for_input else build_full_prompt(history, input_text)

        # 🚀 Call LLM
        response = call_openai(prompt)
        print("🔁 Agent response:\n", response)

        # 🧠 Extract reasoning
        try:
            block = extract_react_block(response)
        except Exception as e:
            print("❌ Parsing error:", e)
            break

        print(f"\n🧠 Thought: {block['thought']}\n⚙️ Action: {block['action']}")

        # ⛔ Stop if asked user something
        if block["action"].startswith("ask_user"):
            block["observation"] = "Waiting for user input."
            history.append(block)
            continue

        # ✅ TODO: Customize stop condition
        if block["action"] == "suggest_fix()":
            block["observation"] = "✅ Final suggestion complete."
            history.append(block)
            print("🎉 Agent finished.")
            break

        # 🔧 Simulate action
        block["observation"] = simulate_action(block["action"], input_text)
        history.append(block)

    return history

# ▶️ TODO: Replace with your actual input
example_input = """
Please analyze this input and respond accordingly.
You can simulate any content here.
"""

react_agent(example_input)

