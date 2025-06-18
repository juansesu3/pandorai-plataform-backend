# app/services/calendar_agent_service.py

from langchain.agents import initialize_agent, Tool, AgentType
from langchain.memory import ConversationBufferMemory
from langchain_openai import ChatOpenAI
from langchain.schema import AIMessage, HumanMessage, BaseMessage
from langchain.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate, ChatPromptTemplate, MessagesPlaceholder
from app.core.config import settings
from app.services.agent_calendar.appointments_service import create_appointment
from app.services.agent_calendar.availability_service import get_available_slots
from typing import Dict, Any
import os
import re
import asyncio
from datetime import datetime
from langchain.tools import StructuredTool
from app.services.mongo_chat_history import ConversationChatHistory

def convert_markdown_to_html(text: str) -> str:
    text = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"_(.*?)_", r"<em>\1</em>", text)
    text = re.sub(r"```(.*?)```", r"\1", text, flags=re.DOTALL)
    return text

def ensure_html_format(response: str) -> str:
    response = convert_markdown_to_html(response)
    if not any(tag in response.lower() for tag in ["<p>", "<ul>", "<ol>", "<li>", "<div>", "<span>", "<strong>", "<em>"]):
        return f"<p>{response}</p>"
    return response

# OpenAI model setup
llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0,
    openai_api_key=settings.openai_api_key
)

# LangChain environment
if settings.langchain_tracing_v2:
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_ENDPOINT"] = settings.langchain_endpoint
    os.environ["LANGCHAIN_API_KEY"] = settings.langchain_api_key
    os.environ["LANGCHAIN_PROJECT"] = settings.langchain_project

# Tools
tools = [
    StructuredTool.from_function(
        name="get_available_slots",
        description="Consulta los horarios disponibles. Requiere: professional_name y date.",
        func=get_available_slots,
        coroutine=get_available_slots  # si es async
    ),
    
    Tool(
        name="create_appointment",
        func=create_appointment,            # Para usar en modo síncrono
        coroutine=create_appointment,       # Para uso asíncrono
        description="Crea una cita con un profesional. Requiere: clientId, professionalId, date, time, duration, userInfo"
    ),
    # Tool(
    #     name="modify_appointment",
    #     func=modify_event,
    #     coroutine=modify_event,
    #     description="Modifica una cita existente con los nuevos detalles."
    # ),
    # Tool(
    #     name="cancel_appointment",
    #     func=cancel_event,
    #     coroutine=cancel_event,
    #     description="Cancela una cita existente."
    # )
]

# System Prompt
system_prompt = """
You are Aurora, a professional calendar assistant. Your role is to help users:
- get available slots
- Create, modify, or cancel appointments
- Send appointment confirmations or reminders

Always reply in the same language as the user's message.

Your responses must always be valid HTML:
- Use <p> for paragraphs
- Use <strong> for bold and <em> for italic
- Use <ul><li> or <ol><li> for lists
- Never use code blocks or JSON

Only help with scheduling. If a user asks something unrelated, explain politely that you only manage appointments.
"""

human_prompt = "{input}"
prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(system_prompt),
    MessagesPlaceholder("chat_history"),
    HumanMessagePromptTemplate.from_template("Hoy es {current_date}. {input}")
])

class CalendarAgentService:

    @staticmethod
    async def generate_answer(question: str, client_id: str, agent_id: str, contact_id: str) -> Dict[str, Any]:
        
        print(f"Generating answer for question: {question}")
        # Ensure the chat history is loaded
        
       
        
        chat_history = ConversationChatHistory(client_id, agent_id, contact_id)
        # 🧠 Carga el historial manualmente
        messages = await chat_history.aget_messages()
        chat_history.messages = messages
        print(f"Chat history messages: {chat_history.messages}")

        memory = ConversationBufferMemory(
            chat_memory=chat_history,
            memory_key="chat_history",
            return_messages=True,
            output_key="output"
        )
        
        agent_executor = initialize_agent(
            tools=tools,
            llm=llm,
            agent=AgentType.OPENAI_FUNCTIONS,
            verbose=True,
            memory=memory,
            agent_kwargs={"system_message": system_prompt},
            return_intermediate_steps=True,
            max_iterations=3
        )

        # await chat_history.add_message(HumanMessage(content=question))
        
        today_str = datetime.utcnow().strftime("%Y-%m-%d")
        combined_input = f"Hoy es {today_str}. {question}"
        result = await agent_executor.ainvoke({
            "input": combined_input
        })

        if isinstance(result, dict):
            response = result.get("output", "")
        else:
            response = result

        response_text = response.content if isinstance(response, BaseMessage) else response
        response_text = ensure_html_format(response_text)

        # if response_text:
        #     await chat_history.add_message(AIMessage(content=response_text))

        return {
            "response": response_text,
            "metadata": {
                "client_id": client_id,
                "agent_id": agent_id,
                "contact_id": contact_id
            }
        }
