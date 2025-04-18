from base64 import b64encode
from os import urandom

from openai.pagination import SyncPage
from openai.types import VectorStoreSearchResponse

def generate_name() -> str: return b64encode(urandom(8)).decode("utf-8")[:-1]
def format_search_results(results: SyncPage[VectorStoreSearchResponse]) -> str:
    formatted_results = ''
    for result in results.data:
        formatted_result = f"<result file_id='{result.file_id}' file_name='{result.filename}'>"
        for part in result.content:
            formatted_result += f"<content>{part.text}</content>"
        formatted_results += formatted_result + "</result>"
    return f"<sources>{formatted_results}</sources>"

