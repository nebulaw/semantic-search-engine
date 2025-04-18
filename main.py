from dotenv import load_dotenv
import os

from app.client import Client
from app.chat import Chat

load_dotenv()


def main():
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_AI_MODEL = os.getenv("OPENAI_AI_MODEL", "gpt-4o")

    client = Client(api_key=OPENAI_API_KEY, model=OPENAI_AI_MODEL)
    try: Chat(client).run()
    except KeyboardInterrupt: client.close(False)

if __name__ == "__main__":
    main()

