import json
import os
from ollama import chat, ChatResponse
from utils.log import log_to_file
from utils.memory import get_memory
import asyncio

localMem = []

# Load the sampleActionJson.json file
with open("actions/sampleActionJson.json", "r") as f:
    sampleActionJson = json.load(f)
with open("config.json", "r") as f:
    config = json.load(f)
with open("ollama_prompt.txt", "r") as f:
    ollama_prompt = f.read().strip()

JSON_MODEL = config.get("json_model", "gemma3:4b")
CONVERSATION_MODEL = config.get("conversation_model", "llama3.1")
IMAGE_MODEL = config.get("image_model", "minicpm-v:8b")
assistant_name = config.get("name", "Assistant")

with open("actions/actions.txt", "r") as f:
    ACTIONS = f.read().strip()

def checkMemory():
    if len(get_memory()) > 15:
        return True
    return False

def ollamaReply(input_text: str):
    response: ChatResponse = chat(
        model=str(CONVERSATION_MODEL),
        messages=[
            {"role": "system", "content": ollama_prompt},
            {"role": "system", "content": f"Memory: {json.dumps(get_memory())}"},
            {"role": "system", "content": f"Local memory: {json.dumps(localMem)}"},
            {"role": "user", "content": input_text},
        ]
    )

    reply = response["message"]["content"]

    print(f"🤖 {assistant_name} says: {reply}")
    log_to_file("ollama_reply", reply)
    # Append to local memory
    if checkMemory() == True:
        localMem.pop(0)  # remove oldest entry
    localMem.append({"user_input": input_text, "my_reply": reply})
    return reply

# '{"actions": "action_name", "details": "details", "remember": "boolean", "memory_key": "string", "memory_value": "string"}'
# Use the sampleActionJson as a guide for the structure of the JSON
def ollamaJson(input_text: str):
    response: ChatResponse = chat(
        model=str(JSON_MODEL),
        messages=[
            {
                "role": "system",
                "content": (
                    'You are an action classifier for an AI assistant integrated into a computer system.'
                    'Respond ONLY with valid JSON in the format:'
                    f'{json.dumps(sampleActionJson)}. '
                    'The list of possible actions are: ' + ACTIONS +
                    '. Ensure the JSON is properly formatted.'
                    'THESE ACTIONS ARE TO BE PERFORMED ONLY WHEN EXPLICITLY ASKED BY THE USER.'
                    'DO NOT USE SEARCH UNLESS THE USER ASKS YOU TO SEARCH FOR SOMETHING.'
                    'DO NOT USE REMEMBER OR SEE_SCREEN OR ANY OTHER ACTION UNLESS THE USER IS ASKING FOR IT'
                    'IF the user input contains the action word THEN ONLY you can use that action.'
                    'If the user input contains the word "search" THEN ONLY you can use the action "search_browser". Else NEVER use it.'
                    'Unless the user specifies an action, you default to speak.'
                    'Make sure to include all keys in the JSON.'
                )
            },
            {"role": "system", "content": f"Memory: {json.dumps(get_memory())}"},
            {"role": "system", "content": ollama_prompt},
            {"role": "user", "content": input_text},
        ],
    )
    raw_reply = response["message"]["content"]
    log_to_file("ollama_raw", raw_reply)

    # Clean up markdown wrappers if present
    cleaned = raw_reply.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`").strip()
        if cleaned.startswith("json"):
            cleaned = cleaned[4:].strip()

    # Try parsing JSON safely
    try:
        parsed = json.loads(cleaned)
        for action in parsed:
            if "action" not in action or "details" not in action:
                raise ValueError("Missing keys in JSON action")
            if "remember" not in action:   # default fallback
                action["remember"] = False
    except Exception as e:
        parsed = [{"action": "speak", "details": input_text, "remember": False}]
        log_to_file("ollama_parse_error", f"Error: {e}\nRaw: {raw_reply}")
    else:
        log_to_file("ollama_parsed", json.dumps(parsed, indent=2))

    return parsed

def ollamaSeeImage(image_info: str, userInput: str):
    response: ChatResponse = chat(
        model=str(CONVERSATION_MODEL),
        messages=[
            {"role": "system", "content": os.getenv("OLLAMA_PROMPT")},
            {"role": "system", "content": f"Memory: {json.dumps(get_memory())}"},
            {"role": "user", "content": userInput},
            {"role": "user", "content": f"I have just taken a screenshot and extracted text from it. Here is the text: {image_info}. What do you make of it? Keep your response concise."},
        ]
    )

    reply = response["message"]["content"]

    print(f"🤖 {assistant_name} says: {reply}")
    log_to_file("ollama_reply", reply)
    if checkMemory() == True:
        localMem.pop(0)  # remove oldest entry
    # Append to local memory
    localMem.append({"image_info": image_info, "my_reply": reply})
    return reply

def ollamaGenerateContent(prompt: str):
    response: ChatResponse = chat(
        model=str(CONVERSATION_MODEL),
        messages=[
            {"role": "system", "content": "You are a helpful assistant that generates content for files. Output ONLY the content requested. Do not wrap in markdown code blocks unless requested. Do not add conversational filler. If asked for code, output ONLY the code."},
            {"role": "user", "content": prompt},
        ]
    )
    return response["message"]["content"]

if __name__ == "__main__":
    input_text = input("You: ")
    #check if the user_input CONTAINS json or conversation
    if "json" in input_text.lower():
        ollamaJson(input_text)
    else:
        ollamaReply(input_text)