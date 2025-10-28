from sqlalchemy.orm import Session
from app.repositories.chat_memory_repository import get_user_chat_memory, save_chat_memory
from app.schemas.chat_memory_schema import ChatMemoryCreate
from langchain_core.messages import HumanMessage, AIMessage
from app.core.config import settings
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from uuid import UUID

# Initialize LLM and Vector DB
embeddings = OpenAIEmbeddings(api_key=settings.OPENAI_API_KEY)
CHROMA_PATH = "app/db/chroma_storage"
vectorstore = Chroma(persist_directory=CHROMA_PATH, embedding_function=embeddings)
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

llm = ChatOpenAI(model=settings.OPENAI_MODEL, temperature=0.3, api_key=settings.OPENAI_API_KEY)

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant. Use the context below to answer clearly."),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "Question: {input}\n\nContext:\n{context}")
])

def chat_with_memory_db(db: Session, user_id: UUID, question: str):
    # 🧠 Load previous messages from DB
    db_history = get_user_chat_memory(db, user_id)
    messages = []
    for item in db_history:
        messages.append(HumanMessage(content=item.question))
        messages.append(AIMessage(content=item.answer))

    # Retrieve related docs
    docs = retriever.invoke(question)
    context = "\n\n".join([doc.page_content for doc in docs])

    # Chain
    chain = prompt | llm | StrOutputParser()
    answer = chain.invoke({
        "input": question,
        "chat_history": messages,
        "context": context
    })

    # Save chat to DB - Create ChatMemoryCreate object
    chat_data = ChatMemoryCreate(
        user_id=user_id,
        question=question,
        answer=answer
    )
    save_chat_memory(db, chat_data)

    return {"answer": answer, "context": docs}