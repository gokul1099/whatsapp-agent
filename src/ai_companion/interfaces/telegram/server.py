import os
import httpx
from fastapi import FastAPI, Request, BackgroundTasks
from pydantic import BaseModel
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from ai_companion.graph.graph import graph_builder
from langchain_core.messages import HumanMessage
from ai_companion.settings import settings



app = FastAPI()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TOKEN}"

async def process_message_and_reply(chat_id: int, user_text: str):
    print(f"Processing message from chat {chat_id}: {user_text}")
    async with AsyncSqliteSaver.from_conn_string(settings.SHORT_TERM_MEMORY_DB_PATH) as memory:
        agent = graph_builder.compile(checkpointer=memory)
        config = {"configurable": {"thread_id": str(chat_id)}}

        state = await agent.ainvoke(
            {"message": [HumanMessage(content=user_text)]},
            config=config
        )

        response_text = state.get("messages")[-1].content
        print(f"Agent reply: {response_text}")

        async with httpx.AsyncClient() as client:
            payload = {
                "chat_id": chat_id,
                "text": response_text
            }
            await client.post(f"{TELEGRAM_API_URL}/sendMessage", json=payload)
            print("message sent successfuly")



@app.post("/webhook/telegram")
async def telegram_webhook(request: Request, background_tasks: BackgroundTasks):
    try:
        data = await request.json()

        if "message" in data and "text" in data["message"]:
            chat_id = data["message"]["chat"]["id"]
            user_text = data["message"]["text"]

            background_tasks.add_task(process_message_and_reply, chat_id, user_text)
    except Exception as e:
        print(f"Error parsing webhook payload: {e}")

    return {"status": "ok"}
