from langchain.tools import tool
from tools import query_medgemma, call_emergency

@tool
def ask_mental_health_specialist(query: str) -> str:
    """
    Generate a therapeutic response using the medgemma model.
    Use this for all general user queries, mental health questions, emotional concerns,
    or to offer empathetic, evidence-based guidance in a conversational tone.
    """
    return query_medgemma(query)


@tool
def emergency_call_tool() -> None:
    """
    Place an emergency call to the safety helpline's phone number via Twilio.
    Use this only if the user expresses suicidal ideation, intent to self-harm,
    or describes a mental health emergency requiring immediate help.
    """
    call_emergency()

@tool
def find_nearby_therapists_by_location(location: str) -> str:
    """
    Finds and returns a list of licensed therapists near the specified location.

    Args:
        location (str): The name of the city or area in which the user is seeking therapy support.

    Returns:
        str: A newline-separated string containing therapist names and contact info.
    """
    return (
        f"Here are some therapists near {location}, {location}:\n"
        "- Dr. Ayesha Kapoor - +1 (555) 123-4567\n"
        "- Dr. James Patel - +1 (555) 987-6543\n"
        "- MindCare Counseling Center - +1 (555) 222-3333"
    )
#Step1: Create an AI Agent & Link to backend
from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from config import GROQ_API_KEY


tools = [ask_mental_health_specialist, emergency_call_tool, find_nearby_therapists_by_location]
llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0.2, api_key=GROQ_API_KEY).bind_tools(tools)

SYSTEM_PROMPT = """
You are an AI engine supporting mental health conversations with warmth and vigilance.
You have access to three tools:

1. `ask_mental_health_specialist`: Use this tool to answer all emotional or psychological queries with therapeutic guidance.
2. `locate_therapist_tool`: Use this tool if the user asks about nearby therapists or if recommending local professional help would be beneficial.
3. `emergency_call_tool`: Use this immediately if the user expresses suicidal thoughts, self-harm intentions, or is in crisis.

Always take necessary action. Respond kindly, clearly, and supportively.
"""

prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", "{input}")
])
graph = prompt | llm 


def parse_response(result):
    tool_called = "None"
    final_response = None

    if hasattr(result, "tool_calls") and result.tool_calls:
        tool_call = result.tool_calls[0]
        tool_called = tool_call["name"]
        tool_args = tool_call.get("args", {})

        if tool_called == "ask_mental_health_specialist":
            final_response = ask_mental_health_specialist.invoke(
                {"query": tool_args["query"]}
            )

        elif tool_called == "find_nearby_therapists_by_location":
            final_response = find_nearby_therapists_by_location.invoke(
                {"location": tool_args["location"]}
            )

        elif tool_called == "emergency_call_tool":
            emergency_call_tool.invoke({})  # 🔥 FIXED
            final_response = (
                "I’m really glad you reached out. "
                "If you’re feeling unsafe, please seek immediate help."
            )

    if not final_response:
        final_response = result.content

    return tool_called, final_response




