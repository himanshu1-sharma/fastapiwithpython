from dotenv import load_dotenv
from app.core.config import settings
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
import os

load_dotenv()

# Initialize embeddings
embeddings = OpenAIEmbeddings(api_key=settings.OPENAI_API_KEY)

# Set up Chroma vector database
CHROMA_PATH = "app/db/chroma_storage"
vectorstore = Chroma(
    persist_directory=CHROMA_PATH,
    embedding_function=embeddings
)

# Create LLM
llm = ChatOpenAI(
    model=settings.OPENAI_MODEL,
    temperature=0.3,
    api_key=settings.OPENAI_API_KEY
)

# Retriever
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

# Create prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant. Use the provided context to answer the question."),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "Question: {input}\n\nContext: {context}")
])

def chat_with_memory(question: str, chat_history: list):
    """
    Handles chat memory by combining previous Human/AI messages with the new question.
    """
    messages = []
    for item in chat_history:
        if isinstance(item, tuple) and len(item) == 2:
            user_text, assistant_text = item
            messages.append(HumanMessage(content=user_text))
            messages.append(AIMessage(content=assistant_text))
        elif isinstance(item, (HumanMessage, AIMessage)):
            messages.append(item)
    
    # Retrieve relevant documents using invoke (newer method)
    docs = retriever.invoke(question)
    context = "\n\n".join([doc.page_content for doc in docs])
    
    # Create chain
    chain = prompt | llm | StrOutputParser()
    
    # Get response
    answer = chain.invoke({
        "input": question,
        "chat_history": messages,
        "context": context
    })
    
    return {"answer": answer, "context": docs}