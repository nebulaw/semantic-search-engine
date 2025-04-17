import os
import sys
from typing import List, Dict
from openai import OpenAI
from openai.pagination import SyncPage
from openai.resources.chat.completions import messages
from openai.types import VectorStoreSearchResponse
from openai.types.chat import ChatCompletionMessageParam
from openai.types.vector_stores.vector_store_file import VectorStoreFile
from .helpers import generate_name


class Client:
    SYSTEM_MESSAGE = "Produce a concise answer to the query based on the provided sources."

    def __init__(self, api_key: str, model: str = "gpt-4o") -> None:
        if not api_key or type(api_key) != str:
            raise ValueError(f"Invalid access token {api_key} provided")
        self.__model = model
        # create a openai client
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
            print(f"Successfully created vector store {self.__vector_store.name}")
        except:
            print("Could not create a vector store. Try again!")
            self.close(True)

    def close(self, sabotage: bool):
        # delete vector store
        if self.__vector_store and self.__vector_store_id:
            self.__client.vector_stores.delete(vector_store_id=self.__vector_store_id)
            print(f"Deleted vector store '{self.__vector_store.name}'")
        # and shutdown the client
        if self.__client:
            self.__client.close()
            print(f"Shut down the OpenAI client")
        print("Exiting...")
        sys.exit(1 if sabotage else 0)

    @property
    def model(self): return self.__model

    @property
    def chat(self): return self.__chat

    @property
    def files(self): return self.__uploaded_files

    # write a function for uploading file to vector store
    def upload_file(self, file):
        # file need to be provided
        if not file:
            raise ValueError("Invalid file provided")
        # check if its a path
        if type(file) == str:
            file = open(file, "rb")
        # upload to vector store
        vector_store_file = self.__client.vector_stores.files.upload_and_poll(
            vector_store_id=self.__vector_store_id,
            file=file
        )
        # obtain full path and save into uploaded files
        file_path = os.path.abspath(file.name)
        self.__uploaded_files[file_path] = vector_store_file

    def search(self, query) -> SyncPage[VectorStoreSearchResponse]:
        return self.__client.vector_stores.search(
            vector_store_id=self.__vector_store_id,
            query=query,
            max_num_results=3
        )

    def __format_search_results(self, results) -> str:
        formatted_results = ''
        for result in results.data:
            formatted_result = f"<result file_id='{result.file_id}' file_name='{result.file_name}'>"
            for part in result.content:
                formatted_result += f"<content>{part.text}</content>"
            formatted_results += formatted_result + "</result>"
        return f"<sources>{formatted_results}</sources>"

    def ask(self, query) -> str | None:
        # first search in vector store
        search_results = self.search(query)
        # format search results
        search_results = self.__format_search_results(search_results)
        # update the chat
        self.__chat.append({
            "role": "user",
            "content": f"Sources: {search_results}\n\nQuery: {query}"
        })
        # get the answer
        answer = self.__client.chat.completions.create(
            model=self.__model,
            messages=self.__chat
        ).choices[0].message.content
        # update the chat
        self.__chat.append({
            "role": "assistant",
            "content": answer
        })
        return answer




