import os
import sys
from typing import List, Dict
from openai import OpenAI
from openai.pagination import SyncPage
from openai.types import VectorStoreSearchResponse
from openai.types.chat import ChatCompletionMessageParam
from openai.types.vector_stores.vector_store_file import VectorStoreFile
from .helpers import generate_name, format_search_results


class Client:
    SYSTEM_MESSAGE = """You are a document-based assistant for a semantic search engine. Your goal is to answer user queries using only the content from the provided source documents.

    Instructions:
    - If sources are provided:
      * Summarize or answer based strictly on the content.
      * Prioritize clarity and conciseness.
    - If no sources are provided:
      * Politely respond that no sources were given and you cannot answer the question.
    - If the sources do not contain relevant information:
      * Clearly state that the answer is not present in the documents.
      * Do not infer or assume based on general knowledge.

    Additional Notes:
    - Do not hallucinate or fabricate details not found in the sources.
    - Do not respond as if you are a generic assistant.
    - Keep responses professional and focused on the content.
    """

    def __init__(self, api_key: str | None, model: str = "gpt-4o") -> None:
        if not api_key or type(api_key) != str:
            raise ValueError(f"Invalid access token {api_key} provided")
        # create a openai client
        self.__model = model
        try:
            self.__client = OpenAI(api_key=api_key)
            print("Successfully created an OpenAI client")
        except:
            print("Could not create a client. Try again!")
            self.close(False)
        # now create a vector store
        self.__chat: List[ChatCompletionMessageParam] = [{ "role": "system", "content": self.SYSTEM_MESSAGE }]
        # save newly created store
        try:
            self.__vector_store = self.__client.vector_stores.create(name=f"VecStore-{generate_name()}")
            self.__vector_store_id = self.__vector_store.id
            # track uploaded files
            self.__uploaded_files: Dict[str, VectorStoreFile] = dict()
            print(f"Successfully created vector store '{self.__vector_store.name}'")
        except:
            print("Could not create a vector store. Try again!")
            self.close(True)

    def close(self, panick: bool):
        print("Please wait while we clean up...")
        # delete vector store
        if self.__vector_store and self.__vector_store_id:
            self.__client.vector_stores.delete(vector_store_id=self.__vector_store_id)
            print(f"Deleted vector store '{self.__vector_store.name}'")
        # and shutdown the client
        if self.__client:
            self.__client.close()
            print(f"Shut down the OpenAI client")
        print("Exiting...")
        if panick: sys.exit(1)

    @property
    def model(self): return self.__model

    @property
    def chat(self): return self.__chat

    @property
    def files(self): return self.__uploaded_files

    # write a function for uploading file to vector store
    def upload_file(self, file_path: str | None):
        # file need to be provided
        if not file_path or type(file_path) != str:
            raise ValueError(f"Invalid file path {file_path} provided")
        # upload to vector store
        with open(file_path, "rb") as file:
            print(f"Uploading file {file.name} to vector store...")
            vector_store_file = self.__client.vector_stores.files.upload_and_poll(
                vector_store_id=self.__vector_store_id,
                file=file
            )
        # obtain full path and save into uploaded files
        file_path = os.path.abspath(file.name)
        self.__uploaded_files[file_path] = vector_store_file
        print(f"Successfully uploaded file {file.name} to vector store")

    def search(self, query) -> SyncPage[VectorStoreSearchResponse]:
        return self.__client.vector_stores.search(
            vector_store_id=self.__vector_store_id,
            query=query,
            max_num_results=3
        )

    def ask(self, query) -> str | None:
        # first search in vector store
        search_results = self.search(query)
        # format search results
        search_results = format_search_results(search_results)
        # update the chat
        self.__chat.append({
            "role": "user",
            "content": f"Sources: {search_results}\n\nQuery: {query}"
        })
        print("Asking the model...")
        # get the answer
        answer = self.__client.chat.completions.create(
            model=self.__model if self.__model else "gpt-4o",
            messages=self.__chat
        ).choices[0].message.content
        # update the chat
        self.__chat.append({
            "role": "assistant",
            "content": answer
        })
        return answer


