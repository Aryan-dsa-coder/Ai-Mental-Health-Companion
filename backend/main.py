#Step1: Setup FastAPI backend
from fastapi import FastAPI, Form
from pydantic import BaseModel
import uvicorn

from ai_agents import graph, SYSTEM_PROMPT, parse_response
app = FastAPI()


#Step2: Receive and validate request from Frontend
class Query(BaseModel):
    message: str
    
@app.post("/ask")
async def ask(query: Query):
    try:
        result = graph.invoke({"input": query.message})
        tool_called_name, final_response = parse_response(result)

        return {
            "response": final_response,
            "tool_called": tool_called_name
        }

    except Exception as e:
        print("🔥 SERVER ERROR:", repr(e))  # <-- THIS LINE IS CRITICAL
        raise e

    

from fastapi.responses import PlainTextResponse
from xml.etree.ElementTree import Element, tostring
import html

def _twiml_message(body: str) -> PlainTextResponse:
    """Create minimal TwiML <Response><Message>...</Message></Response>"""
    response_el = Element('Response')
    message_el = Element('Message')
    message_el.text = html.escape(body)
    response_el.append(message_el)
    xml_bytes = tostring(response_el, encoding='utf-8')
    return PlainTextResponse(content=xml_bytes, media_type='application/xml')

@app.post("/Whatsapp_ask")
async def Whatsapp_ask(Body: str = Form(...)):
    print("📩 WhatsApp message received:", Body)

    result = graph.invoke({"input": Body})
    _, final_response = parse_response(result)

    if not final_response:
        final_response = "I’m here with you. Can you tell me a little more?"

    SAFE_PREFIX = (
        "I’m here to support you. "
        "You’re not alone.\n\n"
    )

    final_response = SAFE_PREFIX + final_response

    MAX_LEN = 900
    if len(final_response) > MAX_LEN:
        final_response = final_response[:MAX_LEN] + "\n\n(continued…)"

    print("🤖 Sending reply to WhatsApp:", final_response)

    return _twiml_message(final_response)
    

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

