import uvicorn
import asyncio
import sqlite3
from pathlib import Path
from fastapi import FastAPI, Form, Response, status
from dotenv import load_dotenv
from src.channels.whatsapp import WhatsAppChannel
from src.agents.personal_assistant import PersonalAssistant
from src.utils import get_current_date_time


def extract_text_from_response(resp) -> str | None:
    """
    Try to extract a plain text reply from common LLM/agent response shapes.
    Returns None when no text found.
    """
    # Simple string
    if isinstance(resp, str):
        return resp

    # List like [{'type':'text','text':'...'}]
    if isinstance(resp, list) and resp:
        first = resp[0]
        if isinstance(first, dict):
            if "text" in first and isinstance(first["text"], str):
                return first["text"]
            if "content" in first and isinstance(first["content"], str):
                return first["content"]

    # Dict-like
    if isinstance(resp, dict):
        # Typical agent state
        if "messages" in resp and isinstance(resp["messages"], list) and resp["messages"]:
            last = resp["messages"][-1]
            if hasattr(last, "content"):
                return getattr(last, "content")
            if isinstance(last, dict):
                for k in ("content", "text", "message"):
                    if k in last and isinstance(last[k], str):
                        return last[k]
        if "text" in resp and isinstance(resp["text"], str):
            return resp["text"]
        if "content" in resp and isinstance(resp["content"], str):
            return resp["content"]

    # Objects with .content
    if hasattr(resp, "content") and isinstance(getattr(resp, "content"), str):
        return getattr(resp, "content")

    return None

# Load .env variables from the environment file
load_dotenv()

# Initiate FastAPI app
app = FastAPI()

# Initialize sqlite3 DB for saving agent memory
BASE_DIR = Path(__file__).resolve().parent
DB_DIR = BASE_DIR / "db"
DB_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DB_DIR / "checkpoints.sqlite"

try:
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
except sqlite3.OperationalError as e:
    raise sqlite3.OperationalError(f"Failed to open database at {DB_PATH}: {e}")

# Initiate personal assistant instance (pass DB connection)
personal_assistant = PersonalAssistant(conn)

# Configuration for the Langgraph agent, specifying thread ID
config = {"configurable": {"thread_id": "1"}}

async def process_message_async(to_whatsapp_number, incoming_message):
    """
    Processes the incoming message asynchronously:
    1. Formats the message with the current date and time.
    2. Invokes the personal assistant to get a response.
    3. Sends the response to the provided WhatsApp number.
    """
    try:
        # Format the message with current date/time
        message = (
            f"Message: {incoming_message}\n"
            f"Current Date/time: {get_current_date_time()}"
        )

        # Invoke the personal assistant to generate a response
        answer = personal_assistant.invoke(message, config=config)
        #print("DEBUG: raw agent output:", repr(answer))

        # Extract plain text to send to WhatsApp
        content = extract_text_from_response(answer)
        if not content:
            # If no plain text, provide a graceful fallback
            content = "Sorry — I couldn't generate a reply right now."

        # Ensure to_whatsapp_number is in Twilio WhatsApp format
        if not str(to_whatsapp_number).startswith("whatsapp:"):
            to_whatsapp = f"whatsapp:{to_whatsapp_number}"
        else:
            to_whatsapp = to_whatsapp_number

        whatsapp = WhatsAppChannel()
        send_result = await asyncio.to_thread(whatsapp.send_message, to_number=to_whatsapp, body=content)
        print("Send result:", send_result)
    except Exception as e:
        # Catch exceptions inside the background task to avoid unhandled Task exceptions
        import traceback
        print(f"Error processing incoming message from {to_whatsapp_number}: {e}")
        traceback.print_exc()

@app.post("/whatsapp/webhook")
async def whatsapp_webhook(Body: str = Form(...), From: str = Form(...)):
    """
    Webhook endpoint that handles incoming messages from WhatsApp.
    Receives the message and triggers an asynchronous task to process it.
    """
    incoming_message = Body
    from_number = From
    print(f"Message received from {from_number}: {incoming_message}")

    # Create an asynchronous task to process the message without blocking
    asyncio.create_task(process_message_async(from_number, incoming_message))

    # Respond with a status indicating that the message was received
    return Response(content="Message received", status_code=status.HTTP_200_OK)


@app.get("/")
async def root():
    """Simple root endpoint to confirm the server is running."""
    return {"status": "ok", "service": "personal-ai-assistant"}

if __name__ == "__main__":
    # Start the FastAPI application on the specified host and port
    uvicorn.run(app, host="0.0.0.0", port=5000)
