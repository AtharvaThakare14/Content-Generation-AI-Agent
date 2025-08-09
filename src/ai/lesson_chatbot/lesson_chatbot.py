import logging
import sys
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from src.exception import CustomException
from src.configurations.openai import OpenAIChatModel


class ContextBoundQABot:
    """Chatbot that answers only questions related to a provided context."""

    def __init__(self):
        try:
            self.chat_open_ai = OpenAIChatModel()
            self.model = self.chat_open_ai.get_chat_model()
            # self.context = context

            self.prompt = ChatPromptTemplate.from_template("""
            You are a helpful assistant that answers questions based on the provided context. You can also greet the user if they say hello. 

            ---

            Context:
            \"\"\"
            {context}
            \"\"\"

            ---

            Instructions:

            1. If the user says "hi", "hello", or "hey", respond in a friendly way and guide them to ask about the topic.

            2. If the question is clearly about the same subject as the context (even if not word-for-word), answer it using what you know from the context.

            3. If the question is **completely unrelated**, respond with: **"Sorry, I can’t answer that."**

            4. Do not guess answers from outside the topic. Stay close to the subject provided.

            ---

            Examples:

            Q: What are lists in Python?  
            A: Lists are used to store and manipulate collections of items like names, numbers, or objects.

            Q: What is Python?  
            A: Python is a programming language. In this lesson, we focus on Python data structures like lists and tuples.

            Q: What is the capital of France?  
            A: Sorry, I can’t answer that

            Q: Hi  
            A: Hi there! How can I help you with this topic?

            ---

            Now respond to the user's question:

            Question: {question}  
            Answer:
            """)

            self.chain = self.prompt | self.model | StrOutputParser()

        except Exception as e:
            raise CustomException(e, sys)

    def answer_question(self, data):
        try:
            response = self.chain.invoke({
                "context": data.context,
                "question": data.question
            })
            return {"response": str(response)}
        except Exception as e:
            raise CustomException(e, sys)
