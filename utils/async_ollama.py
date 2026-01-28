# utils/async_ollama.py (new file maybe)
import asyncio
from actions.brain import ollamaReply as sync_reply, ollamaJson as sync_json

async def ollamaReply_async(text: str):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, sync_reply, text)

async def ollamaJson_async(text: str):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, sync_json, text)
