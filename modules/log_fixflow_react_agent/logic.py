import os
import openai
import re
from dotenv import load_dotenv

# 🔒 Load your OpenAI key from environment
load_dotenv()
openai.api_key = os.getenv("OPEN_AI_API_KEY")
MODEL = "gpt-4o"

# 🧠 Send a prompt to OpenAI and return the response
def call_openai(prompt: str) -> str:
    response = openai.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    return response.choices[0].message.content

# 🔍 Extract Thought, Action, and Observation from LLM output block
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

# 🧱 Builds full prompt (used when not waiting for input)
def build_full_prompt(history: list, log_text: str) -> str:
    intro = (
        "You are a log analysis agent using ReAct logic.\n"
        "Your task is to analyze the error log below and determine the cause of the failure.\n"
        "You must never assume the user’s answer. If you perform ask_user(\"...\") – stop and wait for input.\n"
        "Respond only in this format:\n"
        "<start>\nThought: ...\nAction: ...\nObservation: ...\n<end>\n\n"
    )

    log_block = f"<log>\n{log_text}\n</log>\n\n"

    # Add all blocks including ask_user blocks
    history_block = "\n".join([
        f"<start>\nThought: {h['thought']}\nAction: {h['action']}\nObservation: {h['observation']}\n<end>"
        for h in history
    ])

    return intro + history_block + "\n" + log_block

# 🧱 Builds partial prompt that EXCLUDES ask_user blocks waiting for input
def build_prompt_until_question(history: list, log_text: str) -> str:
    intro = (
        "You are a log analysis agent using ReAct logic.\n"
        "Your task is to analyze the error log below and determine the cause of the failure.\n"
        "You must never assume the user’s answer. If you perform ask_user(\"...\") – stop and wait for input.\n"
        "Respond only in this format:\n"
        "<start>\nThought: ...\nAction: ...\nObservation: ...\n<end>\n\n"
    )

    log_block = f"<log>\n{log_text}\n</log>\n\n"
    block_list = []

    for h in history:
        # ❌ If we are waiting for user input, don't include this block at all!
        if h['action'].startswith("ask_user") and h['observation'] == "Waiting for user input.":
            break
        block_list.append(
            f"<start>\nThought: {h['thought']}\nAction: {h['action']}\nObservation: {h['observation']}\n<end>"
        )

    history_block = "\n".join(block_list)
    return intro + history_block + "\n" + log_block

# 🔧 Simulate available actions (in real world you'd replace with actual tools)
def simulate_action(action: str, log_text: str) -> str:
    if action == "read_log()":
        return log_text
    elif action.startswith("search_error("):
        term = re.search(r'search_error\("(.*?)"\)', action)
        keyword = term.group(1) if term else "unknown"
        return f"🧠 Simulated result: Found threads about '{keyword}'"
    elif action == "suggest_fix()":
        return "🛠️ Suggested fix generated."
    else:
        return "❓ Unknown action."

# 🎯 Main agent loop
def react_agent(log_text: str):
    history = []  # Holds all past steps

    while True:
        # 🛑 If last step was ask_user and we're still waiting — request user input now
        if history and history[-1]["action"].startswith("ask_user") and history[-1]["observation"] == "Waiting for user input.":
            question = re.search(r'ask_user\("(.*?)"\)', history[-1]["action"])
            question_text = question.group(1) if question else "Please answer:"
            print(f"\n🤖 Agent asks: {question_text}")
            user_input = input("🧑 Your answer: ")

            # Save user input as the observation
            history[-1]["observation"] = user_input
            continue  # Rebuild prompt with new input

        # 🧱 Choose prompt building method based on state
        # Check if any block in history is waiting for user input
        waiting_for_input = any(
            h["action"].startswith("ask_user") and h["observation"] == "Waiting for user input."
            for h in history
        )

        if waiting_for_input:
            prompt = build_prompt_until_question(history, log_text)
        else:
            prompt = build_full_prompt(history, log_text)

        # 🛰️ Send prompt to OpenAI
        response = call_openai(prompt)
        print("🔁 Agent response:\n", response)

        # 🔍 Parse model output
        try:
            block = extract_react_block(response)
        except Exception as e:
            print("❌ Could not parse response:", e)
            break

        print(f"\n🧠 Thought: {block['thought']}\n⚙️ Action: {block['action']}")

        # ✋ Intercept ask_user and pause until user provides real answer
        if block["action"].startswith("ask_user"):
            block["observation"] = "Waiting for user input."
            history.append(block)
            continue  # Wait for next loop to ask

        # ✅ If done
        if block["action"] == "suggest_fix()":
            block["observation"] = "Fix suggestion complete."
            print("✅ Agent has suggested a fix.")
            history.append(block)
            break

        # ⚙️ Simulate action
        block["observation"] = simulate_action(block["action"], log_text)
        history.append(block)

    return history
log_example = """
[2025-08-05 13:21:00] Error: Groovy script failed to compile.
  at org.codehaus.groovy.control.ErrorCollector.failIfErrors(ErrorCollector.java:309)
  at WorkflowScript.run(WorkflowScript:10)
"""

react_agent(log_example)



