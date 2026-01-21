import os 
from datetime import datetime
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2 import service_account

SCOPES = [
    "https://www.googleapis.com/auth/calendar.events",
    "https://www.googleapis.com/auth/contacts.readonly",
    'https://www.googleapis.com/auth/gmail.readonly'
]

def get_current_date_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M")
        
def get_credentials():
    """
    Get and refresh Google Contacts API credentials
    """
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Prefer OAuth client secrets file if present
            client_secrets_path = 'credentials.json'
            service_account_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')

            if os.path.exists(client_secrets_path):
                flow = InstalledAppFlow.from_client_secrets_file(
                    client_secrets_path, SCOPES
                )
                creds = flow.run_local_server(port=0)
            # If a service account JSON is provided via env var, use it (useful for servers)
            elif service_account_path and os.path.exists(service_account_path):
                creds = service_account.Credentials.from_service_account_file(
                    service_account_path, scopes=SCOPES
                )
            else:
                raise FileNotFoundError(
                    "No Google credentials found. Provide an OAuth client secrets file named 'credentials.json' "
                    "in the project root or set the environment variable 'GOOGLE_APPLICATION_CREDENTIALS' pointing to a "
                    "service account JSON file. See https://developers.google.com/identity/protocols/oauth2 for details."
                )
        with open('token.json', 'w') as token:
            # Only write token.json for user credentials returned by InstalledAppFlow
            try:
                token.write(creds.to_json())
            except Exception:
                # Service account credentials do not support `to_json()`; skip saving
                pass
    return creds

def extract_provider_and_model(model_string: str):
    return model_string.split("/", 1)

def get_llm_by_provider(model_string, temperature=0.1):
    llm_provider, model = extract_provider_and_model(model_string)
    # Else find provider
    # Map Gemini alias to Google's implementation and allow GEMINI_API_KEY mapping
    if llm_provider in ("google", "gemini"):
        # If user provided GEMINI_API_KEY, map it to the environment variable expected by
        # the Google generative API client (`GOOGLE_API_KEY`). This lets users set
        # GEMINI_API_KEY in their .env without changing library expectations.
        gemini_key = os.environ.get("GEMINI_API_KEY")
        if gemini_key and not os.environ.get("GOOGLE_API_KEY"):
            os.environ["GOOGLE_API_KEY"] = gemini_key
        from langchain_google_genai import ChatGoogleGenerativeAI
        llm = ChatGoogleGenerativeAI(model=model, temperature=temperature)  # Correct model name
    elif llm_provider == "openai":
        from langchain_openai import ChatOpenAI
        llm = ChatOpenAI(model=model, temperature=temperature)
    elif llm_provider == "groq":
        from langchain_groq import ChatGroq
        llm = ChatGroq(model=model, temperature=temperature)
    elif llm_provider == "groq":
        from langchain_groq import ChatGroq
        llm = ChatGroq(model=model, temperature=temperature)
    # ... add elif blocks for other providers ...
    else:
        raise ValueError(f"Unsupported LLM provider: {llm_provider}")
    return llm
