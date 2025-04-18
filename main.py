from dotenv import load_dotenv
import os

from app.client import Client

load_dotenv()


def main():
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_AI_MODEL = os.getenv("OPENAI_AI_MODEL", "gpt-4o")

    client = Client(api_key=OPENAI_API_KEY, model=OPENAI_AI_MODEL)

    def run():
        # upload file
        client.upload_file("/home/nebula/Workspace/projects/semantic-search-engine/symp.txt")
        while True:
            try:
                print("Enter your query (or press 'ctrl+c' to quit):")
                user_input = input().strip()
                if user_input.lower() == "exit": break
                response = client.ask(user_input)
                print(f"Response: {response}")
            except KeyboardInterrupt:
                client.close(False)
                break
    run()


if __name__ == "__main__":
    main()

