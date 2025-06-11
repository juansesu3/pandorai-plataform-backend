# app/services/calendar_agent_service.py

from langchain.agents import initialize_agent, Tool, AgentType
from langchain.memory import ConversationBufferMemory
from langchain_openai import ChatOpenAI
from langchain.schema import AIMessage, HumanMessage, BaseMessage
from langchain.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate, ChatPromptTemplate, MessagesPlaceholder
from app.services.mongo_chat_history import MongoDBChatMessageHistory
from app.core.config import settings
from app.services.agent_calendar.calendar_service import get_availability, create_event, modify_event, cancel_event
from typing import Dict, Any
import os
import re

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
    Tool(
        name="check_availability",
        func=get_availability,
        coroutine=get_availability,
        description="Consulta los horarios disponibles para una fecha específica."
    ),
    Tool(
        name="create_appointment",
        func=create_event,
        coroutine=create_event,
        description="Crea una nueva cita con la información proporcionada por el usuario."
    ),
    Tool(
        name="modify_appointment",
        func=modify_event,
        coroutine=modify_event,
        description="Modifica una cita existente con los nuevos detalles."
    ),
    Tool(
        name="cancel_appointment",
        func=cancel_event,
        coroutine=cancel_event,
        description="Cancela una cita existente."
    )
]

# System Prompt
system_prompt = """
You are Aurora, a professional calendar assistant. Your role is to help users:
- Check availability
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
    HumanMessagePromptTemplate.from_template(human_prompt)
])

class CalendarAgentService:

    @staticmethod
    async def generate_answer(question: str, session_id: str) -> Dict[str, Any]:
        agent_name = "Aurora"
        chat_history = MongoDBChatMessageHistory(agent_name, session_id)
        await chat_history._load_messages()

        memory = ConversationBufferMemory(
            chat_memory=chat_history,
            memory_key="chat_history",
            return_messages=True,
            output_key="output"
        )

        agent_executor = initialize_agent(
            tools=tools,
            llm=llm,
            agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
            verbose=True,
            memory=memory,
            agent_kwargs={"system_message": system_prompt},
            return_intermediate_steps=True,
            max_iterations=3
        )

        await chat_history.add_message(HumanMessage(content=question))
        result = await agent_executor.ainvoke({"input": question})

        if isinstance(result, dict):
            response = result.get("output", "")
        else:
            response = result

        response_text = response.content if isinstance(response, BaseMessage) else response
        response_text = ensure_html_format(response_text)

        if response_text:
            await chat_history.add_message(AIMessage(content=response_text))

        return {
            "response": response_text,
            "metadata": {
                "session_id": session_id
            }
        }
