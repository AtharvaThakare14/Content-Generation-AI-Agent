import os

from src.logging import logging
from src.exception import CustomException
from src.constants.openai import OPENAI_API_KEY


from langchain_openai import OpenAIEmbeddings, ChatOpenAI

# os.environ["OPENAI_API_KEY"] =  ""
class OpenAIEmbedding:
    def __init__(self):
        try:
            self.api_key = OPENAI_API_KEY

            if not self.api_key:
                raise ValueError(
                    "OpenAI API key must be set as an environment variable.")

            self.embedding_model = OpenAIEmbeddings(api_key=self.api_key)
            logging.info("OpenAI Embedding Model Initialized Successfully")

        except Exception as e:
            logging.error(f"Error initializing OpenAI embeddings: {e}")
            raise CustomException(
                f"Error initializing OpenAI embeddings: {str(e)}")

    def get_embedding_model(self):
        """Returns the initialized OpenAI embedding model."""
        return self.embedding_model


class OpenAIChatModel:
    def __init__(self):
        try:
            self.api_key = os.getenv("OPENAI_API_KEY")

            if not self.api_key:
                raise ValueError("OpenAI API key must be set as an environment variable.")

            self.model = ChatOpenAI(openai_api_key=self.api_key)
            logging.info("OpenAI Chat Model Initialized Successfully")

        except Exception as e:
            logging.error(f"Error initializing OpenAI Chat Model: {e}")
            raise Exception(f"Error initializing OpenAI Chat Model: {str(e)}")

    def get_chat_model(self):
        """Returns the initialized OpenAI Chat model."""
        return self.model