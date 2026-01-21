"""
scripts/create_token.py

Run this script to trigger the Google OAuth InstalledAppFlow used by `src.utils.get_credentials()`.
It will open a browser for you to sign in and consent, and when successful `token.json` will
be written to the project root (if using InstalledAppFlow).

Usage:
    python scripts/create_token.py

Make sure `credentials.json` (OAuth client secrets) is present in the project root.
"""

import os
import traceback

# Make the project root importable so `from src import ...` works when
# running this script directly (e.g. `python scripts/create_token.py`).
# When a script is executed, Python sets sys.path[0] to the script's
# directory (here `.../scripts`) which prevents sibling packages like
# `src` from being found. Prepend the repository root to sys.path.
import sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.utils import get_credentials
from dotenv import load_dotenv

# Load environment variables from the project's .env (if present).
# Many parts of the repo (app.py, app_whatsapp.py) call `load_dotenv()` at startup,
# but running this script directly won't automatically load .env unless we do so here.
env_path = os.path.join(ROOT, '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)

# Print debug information about the service account env var to help diagnose
# issues where the path in .env isn't being picked up or is incorrect.
sa_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
print('GOOGLE_APPLICATION_CREDENTIALS (raw):', repr(sa_path))
if sa_path:
    # Resolve relative paths against project root
    if not os.path.isabs(sa_path):
        sa_path = os.path.normpath(os.path.join(ROOT, sa_path.strip('"')))
    print('Resolved service account path:', sa_path)
    print('Exists:', os.path.exists(sa_path))
else:
    print('GOOGLE_APPLICATION_CREDENTIALS is not set in environment.')


def main():
    try:
        creds = get_credentials()
        print("Credentials obtained:", type(creds))
        # token.json is created by get_credentials() when using InstalledAppFlow
        token_path = os.path.abspath("token.json")
        if os.path.exists("token.json"):
            print("token.json created at:", token_path)
        else:
            print(
                "token.json not found. You may be using service-account credentials or the flow did not write token.json."
            )
    except Exception as e:
        print("Error obtaining credentials:")
        traceback.print_exc()


if __name__ == "__main__":
    main()
