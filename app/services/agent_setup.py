# agent_setup.py

from langchain.agents import Tool, initialize_agent, AgentType
from tools.calendar_tools import (
    check_availability_tool,
    create_appointment_tool,
    modify_appointment_tool,
    cancel_appointment_tool
)
from langchain.chat_models import ChatOpenAI

# Definir cada tool con un nombre, descripción y función asociada
tools = [
    Tool(
        name="check_availability",
        func=check_availability_tool,
        description="Consulta los horarios disponibles para una fecha dada. Input: fecha 'YYYY-MM-DD'."
    ),
    Tool(
        name="create_appointment",
        func=create_appointment_tool,
        description="Crea una cita en el calendario. Input: fecha 'YYYY-MM-DDTHH:MM', duración en minutos, teléfono del usuario."
    ),
    Tool(
        name="modify_appointment",
        func=modify_appointment_tool,
        description="Modifica una cita existente. Input: ID de evento, nueva fecha 'YYYY-MM-DDTHH:MM', nueva duración."
    ),
    Tool(
        name="cancel_appointment",
        func=cancel_appointment_tool,
        description="Cancela una cita existente. Input: ID de evento."
    ),
    # Podrías añadir herramientas extra, p. ej. ver detalles de citas, listar próximas citas, etc.
]

# Inicializar el LLM (asegúrate de haber configurado tu OPENAI_API_KEY en variables de entorno)
llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0.2)

# Crear el agente conversacional
agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
    verbose=True,  # Para que imprima logs en consola (útil en desarrollo)
)
