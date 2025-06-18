# app/services/agent_calendar/conversation_chat_history.py

from langchain.memory.chat_memory import BaseChatMessageHistory
from langchain.schema import AIMessage, HumanMessage, BaseMessage
from typing import List
from app.db.mongo import conversations_collection
from datetime import datetime


class ConversationChatHistory(BaseChatMessageHistory):
    def __init__(self, client_id: str, agent_id: str, contact_id: str):
        self.client_id = client_id
        self.agent_id = agent_id
        self.contact_id = contact_id
        self.messages: List[BaseMessage] = []

    async def aget_messages(self) -> List[BaseMessage]:
        convo = await conversations_collection.find_one({
            "clientId": self.client_id,
            "agentId": self.agent_id,
            "contactId": self.contact_id
        })
        
        
        
        if not convo or "messages" not in convo:
            print("⚠️ No se encontraron mensajes previos.")
            return []

        raw_messages = convo["messages"][-10:]
        print(f"⚠️ Cargando {len(raw_messages)} mensajes previos.")
        messages = []

        for msg in raw_messages:
            if msg["sender"] == "admin" or msg["sender"] == self.contact_id:
                messages.append(HumanMessage(content=msg["content"]))
            elif msg["sender"] == "agent":
                messages.append(AIMessage(content=msg["content"]))

        self.messages = messages
        return messages

    def add_message(self, message: BaseMessage):
        # noop: handled by backend already
        pass

    async def clear(self):
        await conversations_collection.update_one(
            {
                "clientId": self.client_id,
                "agentId": self.agent_id,
                "contactId": self.contact_id
            },
            {
                "$set": {
                    "messages": [],
                    "updatedAt": datetime.utcnow()
                }
            }
        )
        self.messages = []