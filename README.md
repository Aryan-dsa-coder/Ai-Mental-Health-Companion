# AI Mental Health Support Companion

This is an AI-powered mental health companion that combines a chat-style frontend, an LLM-based backend agent, and integrations with Twilio WhatsApp. It is designed to offer empathetic, tool-augmented support, including:

- Conversational mental health guidance using a therapeutic LLM (MedGemma via Groq)
- Detection of crisis scenarios with an emergency call tool (Twilio voice)
- A simple Streamlit chat UI for web, plus a Twilio WhatsApp webhook for chat over WhatsApp

The project is structured as a small, opinionated demo of how to build a **tool-using AI agent** for mental health support.

> **Important:** This project is for educational/demo purposes only and is **not** a substitute for professional mental health care. Do not rely on it for emergency situations.

---

## Project Structure

```text
AI Mental Health Companion/
├── backend/
│   ├── ai_agent.py         # LangGraph-based AI agent + tools (LLM, emergency call, therapist finder)
│   ├── config.py           # API keys and configuration (not shown here; you create it)
│   ├── main.py             # FastAPI backend (JSON /ask + Twilio WhatsApp /whatsapp_ask)
│   ├── tools.py            # Low-level tool implementations (MedGemma, Twilio call, etc.)
├── frontend.py              # Streamlit chat UI (web client) talking to FastAPI backend
├── pyproject.toml           # Project metadata and Python dependencies (managed with uv)
└── README.md                # Main project README
```

### Key Components

- **`frontend.py`**
  - A Streamlit app that:
    - Renders a chat interface with `st.chat_input` and `st.chat_message`.
    - Sends user messages to the backend endpoint `POST /ask` on `http://localhost:8000/ask`.
    - Displays the AI agent's response along with the name of any tool that was used.

- **`backend/main.py`**
  - Defines a FastAPI application with two main endpoints:
    - `POST /ask`: JSON API used by the Streamlit frontend.
    - `POST /whatsapp_ask`: Twilio WhatsApp webhook endpoint that receives form-encoded messages (Body field) and responds with TwiML.
  - Uses `ai_agent.graph` (LangGraph REAct agent) with `parse_response` to generate responses.
  - Includes a helper `_twiml_message()` to build minimal TwiML XML responses for Twilio.

- **`backend/ai_agent.py`**
  - Declares several LangChain tools using `@tool`:
    - `ask_mental_health_specialist(query: str) -> str`
      - Uses `query_medgemma()` (from `tools.py`) to call a MedGemma-based model for therapeutic responses.
    - `emergency_call_tool() -> None`
      - Uses `call_emergency()` (from `tools.py`) to trigger a Twilio voice call to a safety helpline.
    - `find_nearby_therapists_by_location(location: str) -> str`
     
  - Configures the LLM:
    - Uses `ChatGroq` with model `"openai/gpt-oss-120b"` and `GROQ_API_KEY` from `config.py`.
    - Uses a tool-enabled language model (`llm.bind_tools(...)`) to reason about user input and invoke tools when needed.
  - Defines a `SYSTEM_PROMPT` with instructions for when to use each tool.
  - Provides `parse_response(result)` to extract the final message and which tool was called from the streaming agent output.

- **`backend/config.py`** (implied)
  - Should provide configuration values such as:
    - `GROQ_API_KEY`
    - Twilio credentials (e.g., `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, phone numbers)
  - You create this file yourself and **do not commit your secrets**.

- **`backend/tools.py`** (implied)
  - Implements the concrete integrations:
    - `query_medgemma(query: str) -> str`
    - `call_emergency() -> None`
    - Optional helpers for Twilio

---

## Tech Stack

- **Language:** Python (>= 3.11)
- **Environment & packaging:** [`uv`](https://github.com/astral-sh/uv) (for virtualenv + dependency management via `pyproject.toml`)
- **Backend:** FastAPI + Uvicorn
- **Frontend:** Streamlit
- **LLM / Agent:**
  - `langchain`
  - `langgraph`
  - `langchain-groq` with `ChatGroq`
- **Integrations:**
  - Twilio (WhatsApp + Voice)
  - Requests (supporting utilities)

Dependencies (from `pyproject.toml`):

- `fastapi`
- `langchain`
- `langchain-groq`
- `langgraph`
- `ollama`
- `pydantic`
- `python-multipart` (needed for FastAPI form parsing, e.g. Twilio webhooks)
- `requests`
- `streamlit`
- `twilio`
- `uvicorn`

---

## Prerequisites

- Python **3.11+** installed on your system.
- [`uv`](https://github.com/astral-sh/uv) installed (for virtual environment + dependency management).
- API keys / credentials for:
  - **Groq** (LLM): `GROQ_API_KEY`
  - **Twilio**:
    - `TWILIO_ACCOUNT_SID`
    - `TWILIO_AUTH_TOKEN`
    - Verified phone numbers / WhatsApp sandbox setup.

---

## Setup with `uv`

All commands below assume you are in the project root: `AI Mental Health Companion/`.

### 1. Clone and install

```bash
git clone https://github.com/Aryan-dsa-coder/Ai-Mental-Health-Companion.git
cd AI Mental Health Companion

# Install dependencies and create .venv using uv
uv sync
```


### 3. Configure environment variables and `config.py`

Create a file `backend/config.py` with your keys. For example:

```python
# backend/config.py

GROQ_API_KEY = "your_groq_api_key_here"

# Twilio (used by tools.py / emergency_call_tool)
TWILIO_ACCOUNT_SID = "your_twilio_account_sid_here"
TWILIO_AUTH_TOKEN = "your_twilio_auth_token_here"
TWILIO_FROM_NUMBER = "+1234567890"  # your Twilio phone or WhatsApp-enabled number
TWILIO_EMERGENCY_TO_NUMBER = "+1987654321"  # safety helpline / emergency contact
```

> **Security note:** Don’t commit real keys; use `.env` or environment variables in production.

If you prefer environment variables, adapt `config.py` to read from `os.environ`.

---

## Running the Backend (FastAPI + Twilio webhook)

### Option A: Using uv directly

From the project root:

```bash
uv run uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

### Option B: Using the activated venv

```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

This exposes:

- `POST /ask` – JSON API for the Streamlit frontend.
- `POST /whatsapp_ask` – Twilio WhatsApp webhook endpoint.

### `POST /ask` – JSON endpoint

- **URL:** `http://localhost:8000/ask`
- **Method:** `POST`
- **Content-Type:** `application/json`
- **Body:**

```json
{
  "message": "I’ve been feeling really anxious lately."
}
```

- **Response (example):**

```json
{
  "response": "Empathetic therapeutic guidance here...",
  "tool_called": "ask_mental_health_specialist"
}
```

### `POST /whatsapp_ask` – Twilio WhatsApp webhook

- **Local URL:** `http://localhost:8000/whatsapp_ask`
- **Public URL (via ngrok or similar):** `https://<your-ngrok-domain>/whatsapp_ask`
- **Method:** `POST`
- **Expected content-type:** `application/x-www-form-urlencoded`
- **Key parameters (from Twilio):**
  - `Body`: the incoming text message
  - `From`: the sender’s WhatsApp number (may be used in tools)

Example local test with `curl`:

```bash
curl -X POST \
  http://localhost:8000/whatsapp_ask \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "Body=Hello, I’m feeling overwhelmed."
```

Response (simplified):

```xml
<Response>
  <Message>AI therapist response here...</Message>
</Response>
```

> If you see `422 Unprocessable Entity`, it usually means the `Body` form field is missing or the content-type is not `application/x-www-form-urlencoded`.

---

## Running the Frontend (Streamlit)

With the backend running on `http://localhost:8000`:

From the project root:

```bash
uv run streamlit run frontend.py
```

This will:

- Open (or provide a URL to) a Streamlit app, typically at `http://localhost:8501`.
- Show a chat interface titled **"🧠 AI Mental Health Companion"**.
- Let you type messages via `st.chat_input`.
- Under the hood, each user message sends a `POST` request to `http://localhost:8000/ask`.
- Display the assistant’s response and the name of the tool that was used.

---

## Twilio WhatsApp Integration

### 1. Expose the backend via a public URL

Twilio needs to reach your FastAPI server over the public internet. A common approach is to use [ngrok](https://ngrok.com/).

With the FastAPI server running on port 8000:

```bash
ngrok http 8000
```

Take note of the public HTTPS URL, e.g.: `https://abcd1234.ngrok.io`.

### 2. Configure Twilio Sandbox / WhatsApp number

In the Twilio Console:

1. Go to your WhatsApp Sandbox or phone number configuration.
2. Set the **Webhook URL** for incoming messages to:

   ```text
   https://abcd1234.ngrok.io/whatsapp_ask
   ```

3. Ensure the method is `POST` and the body is `application/x-www-form-urlencoded` (the default for Twilio).

Now, messages sent to your Twilio WhatsApp number should be forwarded to `/whatsapp_ask`, which will:

- Extract `Body` via `Form` parsing.
- Run the LangGraph-based agent.
- Return a TwiML `<Message>` body as the reply.

### 3. Common pitfalls & troubleshooting

- **422 Unprocessable Entity**
  - Usually means FastAPI could not validate the request body.
  - Check that `Body` is present in the form data.
  - Ensure you are using `application/x-www-form-urlencoded`, not JSON.
  - Confirm the path in Twilio (`/whatsapp_ask`) matches the backend route exactly.

- **No response or Twilio error**
  - Make sure the FastAPI server is running and the ngrok tunnel is active.
  - Check logs in your terminal for Python exceptions (e.g., misconfigured `config.py`).

- **Twilio signature validation** (optional hardening)
  - For production, you should validate `X-Twilio-Signature` headers to ensure requests are genuinely from Twilio.

---

## Emergency Call Tool

The `emergency_call_tool()` in `backend/ai_agent.py`:

- Calls `call_emergency()` from `backend/tools.py`.
- Expected behavior:
  - Initiate a Twilio voice call to a predefined emergency / helpline number.
  - Provide a script or connect the user to human support.

> **Ethical note:** Use extreme caution if you adapt this to real-world scenarios. Always comply with local regulations and best practices for crisis support.

---

## Development Notes

### Code style & structure

- Separation of concerns:
  - `backend/main.py`: HTTP layer (FastAPI routes, Twilio TwiML responses).
  - `backend/ai_agent.py`: Agent orchestration and tool definitions.
  - `backend/tools.py`: Concrete integrations (LLM, Twilio, etc.).
  - `frontend.py`: UI only – no business logic.

- Streaming agent:
  - The agent is executed via `graph.invoke({"input": query.message})`.
  - `parse_response()` walks through the streaming updates to detect:
    - Which tool (if any) was called.
    - The final agent message to return.

## Disclaimer

This project is intended as a **technical demonstration** of how to combine LLM tooling, Twilio, and location-based services for mental health support–style conversations. It **must not** be used as a replacement for licensed mental health professionals or emergency services.

If you or someone you know is in immediate danger, contact local emergency services or a crisis hotline in your region.
