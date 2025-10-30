# """
# Chat Long-Term Memory Service
# Business logic layer for memory operations
# """
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
import logging

from app.core.openai_client import get_ai_response
from app.core.tavily_client import fetch_realtime_data
from app.repositories.chat_long_memory_repository import (
    create_chat_long_memory,
    get_memory_by_id,
    get_recent_memories,
    get_all_memories,
    get_memories_by_type,
    get_important_memories,
    search_memories_by_content,
    update_last_used,
    update_memory_importance as repo_update_importance,
    update_memory,
    delete_memory,
    delete_old_memories as repo_delete_old,
    delete_all_user_memories,
    get_memory_count,
    get_memory_stats
)
from app.schemas.chat_long_memory_schema import (
    ChatLongMemoryCreate,
    ChatLongMemoryUpdate,
    ChatLongMemoryResponse,
    ChatMemoryQueryResponse,
    MemoryStatsResponse,
    MemoryCleanupResponse
)

logger = logging.getLogger(__name__)

class ChatLongMemoryService:
    """Service layer for managing long-term chat memories"""

    @staticmethod
    def create_memory(
        db: Session,
        user_id: UUID,
        content: str,
        role: str = "system",
        memory_type: str = "summary",
        importance_score: float = 0.5,
        meta_data: Optional[dict] = None
    ) -> ChatLongMemoryResponse:
        """
        Create a new long-term memory entry
        Args:
            db: Database session
            user_id: User's UUID
            content: Memory content (summary/fact/reflection)
            role: Message role (system/human/ai)
            memory_type: Type of memory (summary/fact/reflection/note)
            importance_score: Importance rating (0.0 to 1.0)
            meta_data: Additional metadata
        Returns:
            ChatLongMemoryResponse object
        """
        try:
            print(f"💾 [SERVICE] Creating memory for user {user_id}")
            print(f"📝 [SERVICE] Type: {memory_type}, Role: {role}, Importance: {importance_score}")
            memory_data = ChatLongMemoryCreate(
                user_id=user_id,
                role=role,
                content=content,
                memory_type=memory_type,
                importance_score=importance_score,
                meta_data=meta_data or {}
            )
            new_memory = create_chat_long_memory(db, memory_data)
            print(f"✅ [SERVICE] Memory created with ID: {new_memory.id}")
            return ChatLongMemoryResponse.from_orm(new_memory)
        except Exception as e:
            logger.error(f"Error creating memory: {e}")
            print(f"❌ [SERVICE ERROR] {e}")
            raise

    @staticmethod
    def get_memory(db: Session, memory_id: UUID) -> Optional[ChatLongMemoryResponse]:
        """
        Get a single memory by ID
        Args:
            db: Database session
            memory_id: Memory UUID
        Returns:
            ChatLongMemoryResponse or None
        """
        try:
            memory = get_memory_by_id(db, memory_id)
            if memory:
                update_last_used(db, memory_id)
                return ChatLongMemoryResponse.from_orm(memory)
            return None
        except Exception as e:
            logger.error(f"Error fetching memory: {e}")
            raise

    @staticmethod
    def get_user_recent_memories(
        db: Session,
        user_id: UUID,
        limit: int = 10
    ) -> ChatMemoryQueryResponse:
        """
        Get recent memories for a user
        Args:
            db: Database session
            user_id: User's UUID
            limit: Number of recent memories to fetch
        Returns:
            ChatMemoryQueryResponse with list of memories
        """
        try:
            print(f"🔍 [SERVICE] Fetching {limit} recent memories for user {user_id}")
            memories = get_recent_memories(db, user_id, limit)
            print(f"✅ [SERVICE] Found {len(memories)} memories")
            # Update last_used_at for fetched memories
            for memory in memories:
                update_last_used(db, memory.id)
            return ChatMemoryQueryResponse(memories=memories)
        except Exception as e:
            logger.error(f"Error fetching recent memories: {e}")
            print(f"❌ [SERVICE ERROR] {e}")
            raise

    @staticmethod
    def get_all_user_memories(
        db: Session,
        user_id: UUID
    ) -> ChatMemoryQueryResponse:
        """
        Get all memories for a user
        
        Args:
            db: Database session
            user_id: User's UUID
        
        Returns:
            ChatMemoryQueryResponse with all memories
        """
        try:
            print(f"🔍 [SERVICE] Fetching all memories for user {user_id}")
            
            memories = get_all_memories(db, user_id)
            print(f"✅ [SERVICE] Found {len(memories)} total memories")
            
            response = ChatMemoryQueryResponse(
                memories=[ChatLongMemoryResponse.from_orm(m) for m in memories],
                total_count=len(memories)
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error fetching all memories: {e}")
            print(f"❌ [SERVICE ERROR] {e}")
            raise

    @staticmethod
    def get_memories_by_type(
        db: Session,
        user_id: UUID,
        memory_type: str,
        limit: Optional[int] = None
    ) -> ChatMemoryQueryResponse:
        """
        Get memories filtered by type
        
        Args:
            db: Database session
            user_id: User's UUID
            memory_type: Type to filter (summary/fact/reflection/note)
            limit: Optional limit on results
        
        Returns:
            ChatMemoryQueryResponse with filtered memories
        """
        try:
            print(f"🔍 [SERVICE] Fetching {memory_type} memories for user {user_id}")
            
            memories = get_memories_by_type(db, user_id, memory_type, limit)
            print(f"✅ [SERVICE] Found {len(memories)} {memory_type} memories")
            
            response = ChatMemoryQueryResponse(
                memories=[ChatLongMemoryResponse.from_orm(m) for m in memories],
                total_count=len(memories)
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error fetching memories by type: {e}")
            print(f"❌ [SERVICE ERROR] {e}")
            raise

    @staticmethod
    def get_important_memories(
        db: Session,
        user_id: UUID,
        min_importance: float = 0.7,
        limit: int = 20
    ) -> ChatMemoryQueryResponse:
        """
        Get memories above a certain importance threshold
        
        Args:
            db: Database session
            user_id: User's UUID
            min_importance: Minimum importance score (0.0 to 1.0)
            limit: Maximum number of results
        
        Returns:
            ChatMemoryQueryResponse with important memories
        """
        try:
            print(f"🔍 [SERVICE] Fetching important memories (>= {min_importance}) for user {user_id}")
            
            memories = get_important_memories(db, user_id, min_importance, limit)
            print(f"✅ [SERVICE] Found {len(memories)} important memories")
            
            response = ChatMemoryQueryResponse(
                memories=[ChatLongMemoryResponse.from_orm(m) for m in memories],
                total_count=len(memories)
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error fetching important memories: {e}")
            print(f"❌ [SERVICE ERROR] {e}")
            raise

    @staticmethod
    def search_memories(
        db: Session,
        user_id: UUID,
        search_term: str,
        limit: int = 20
    ) -> ChatMemoryQueryResponse:
        """
        Search memories by content
        
        Args:
            db: Database session
            user_id: User's UUID
            search_term: Text to search for
            limit: Maximum results
        
        Returns:
            ChatMemoryQueryResponse with matching memories
        """
        try:
            print(f"🔍 [SERVICE] Searching memories for '{search_term}' (user {user_id})")
            
            memories = search_memories_by_content(db, user_id, search_term, limit)
            print(f"✅ [SERVICE] Found {len(memories)} matching memories")
            
            response = ChatMemoryQueryResponse(
                memories=[ChatLongMemoryResponse.from_orm(m) for m in memories],
                total_count=len(memories)
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error searching memories: {e}")
            print(f"❌ [SERVICE ERROR] {e}")
            raise

    @staticmethod
    def update_memory_importance(
        db: Session,
        memory_id: UUID,
        new_importance: float
    ) -> Optional[ChatLongMemoryResponse]:
        """
        Update the importance score of a memory
        
        Args:
            db: Database session
            memory_id: Memory UUID
            new_importance: New importance score (0.0 to 1.0)
        
        Returns:
            Updated ChatLongMemoryResponse or None
        """
        try:
            print(f"🔄 [SERVICE] Updating importance for memory {memory_id} to {new_importance}")
            
            memory = repo_update_importance(db, memory_id, new_importance)
            
            if not memory:
                print(f"⚠️ [SERVICE] Memory {memory_id} not found")
                return None
            
            print(f"✅ [SERVICE] Importance updated to {memory.importance_score}")
            return ChatLongMemoryResponse.from_orm(memory)
            
        except Exception as e:
            logger.error(f"Error updating memory importance: {e}")
            print(f"❌ [SERVICE ERROR] {e}")
            raise

    @staticmethod
    def update_memory_content(
        db: Session,
        memory_id: UUID,
        update_data: ChatLongMemoryUpdate
    ) -> Optional[ChatLongMemoryResponse]:
        """
        Update memory content and metadata
        
        Args:
            db: Database session
            memory_id: Memory UUID
            update_data: ChatLongMemoryUpdate schema
        
        Returns:
            Updated ChatLongMemoryResponse or None
        """
        try:
            print(f"🔄 [SERVICE] Updating memory {memory_id}")
            
            memory = update_memory(db, memory_id, update_data)
            
            if not memory:
                print(f"⚠️ [SERVICE] Memory {memory_id} not found")
                return None
            
            print(f"✅ [SERVICE] Memory updated successfully")
            return ChatLongMemoryResponse.from_orm(memory)
            
        except Exception as e:
            logger.error(f"Error updating memory: {e}")
            print(f"❌ [SERVICE ERROR] {e}")
            raise

    @staticmethod
    def delete_memory(db: Session, memory_id: UUID) -> bool:
        """
        Delete a single memory
        
        Args:
            db: Database session
            memory_id: Memory UUID
        
        Returns:
            True if deleted, False if not found
        """
        try:
            print(f"🗑️ [SERVICE] Deleting memory {memory_id}")
            
            deleted = delete_memory(db, memory_id)
            
            if deleted:
                print(f"✅ [SERVICE] Memory deleted successfully")
            else:
                print(f"⚠️ [SERVICE] Memory {memory_id} not found")
            
            return deleted
            
        except Exception as e:
            logger.error(f"Error deleting memory: {e}")
            print(f"❌ [SERVICE ERROR] {e}")
            raise

    @staticmethod
    def delete_old_memories(
        db: Session,
        user_id: UUID,
        days_old: int = 90,
        min_importance: float = 0.3
    ) -> MemoryCleanupResponse:
        """
        Delete old, low-importance memories (memory cleanup)
        
        Args:
            db: Database session
            user_id: User's UUID
            days_old: Delete memories older than this many days
            min_importance: Only delete if importance is below this
        
        Returns:
            MemoryCleanupResponse with deletion count
        """
        try:
            print(f"🗑️ [SERVICE] Cleaning up old memories for user {user_id}")
            print(f"📅 [SERVICE] Days old: {days_old}, Min importance: {min_importance}")
            
            deleted_count = repo_delete_old(db, user_id, days_old, min_importance)
            print(f"✅ [SERVICE] Deleted {deleted_count} old memories")
            
            return MemoryCleanupResponse(
                message=f"Successfully deleted {deleted_count} old memories",
                deleted_count=deleted_count
            )
            
        except Exception as e:
            logger.error(f"Error deleting old memories: {e}")
            print(f"❌ [SERVICE ERROR] {e}")
            raise

    @staticmethod
    def delete_all_memories(db: Session, user_id: UUID) -> MemoryCleanupResponse:
        """
        Delete ALL memories for a user (use with caution!)
        
        Args:
            db: Database session
            user_id: User's UUID
        
        Returns:
            MemoryCleanupResponse with deletion count
        """
        try:
            print(f"🗑️ [SERVICE] Deleting ALL memories for user {user_id}")
            
            deleted_count = delete_all_user_memories(db, user_id)
            print(f"✅ [SERVICE] Deleted {deleted_count} memories")
            
            return MemoryCleanupResponse(
                message=f"Successfully deleted all {deleted_count} memories",
                deleted_count=deleted_count
            )
            
        except Exception as e:
            logger.error(f"Error deleting all memories: {e}")
            print(f"❌ [SERVICE ERROR] {e}")
            raise

    @staticmethod
    def get_memory_statistics(db: Session, user_id: UUID) -> MemoryStatsResponse:
        """
        Get comprehensive memory statistics
        
        Args:
            db: Database session
            user_id: User's UUID
        
        Returns:
            MemoryStatsResponse with statistics
        """
        try:
            print(f"📊 [SERVICE] Fetching memory stats for user {user_id}")
            
            stats = get_memory_stats(db, user_id)
            print(f"✅ [SERVICE] Stats retrieved successfully")
            
            return MemoryStatsResponse(**stats)
            
        except Exception as e:
            logger.error(f"Error fetching memory stats: {e}")
            print(f"❌ [SERVICE ERROR] {e}")
            raise


# Singleton instance
chat_long_memory_service = ChatLongMemoryService()


from langchain_core.tools import Tool
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
from langchain_community.tools import DuckDuckGoSearchRun
import traceback
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# 🧠 Initialize LLM and Vector DB
try:
    embeddings = OpenAIEmbeddings(api_key=settings.OPENAI_API_KEY)
    CHROMA_PATH = "app/db/chroma_storage"
    vectorstore = Chroma(persist_directory=CHROMA_PATH, embedding_function=embeddings)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    llm = ChatOpenAI(model=settings.OPENAI_MODEL, temperature=0.3, api_key=settings.OPENAI_API_KEY)
    search_tool = DuckDuckGoSearchRun()
    logger.info("✅ All tools initialized successfully")
except Exception as init_error:
    logger.error(f"❌ Initialization error: {init_error}")
    logger.debug(traceback.format_exc())

# 💬 System Prompt
prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        f"""
        Tum {settings.BOT_NAME} ho — ek intelligent, polite aur thoda witty AI assistant 
        jise {settings.CREATOR_NAME} ne banaya hai 😎.

        Kuch khaas baatein mere baare mein:
        • Mujhe {settings.CREATOR_NAME} ne banaya hai.
        • Main Hindi-English dono me baat karta hoon.
        • Main coding, AI, aur daily life ke sawalon ka jawab deta hoon.
        • Thoda witty hoon, par respect ke saath.
        • Mere paas updated knowledge hai (jitna mujhe diya gaya hai).

        Agar koi pooche "tum kaun ho" ya "apne baare me batao", 
        to apne style me confidently ye sab batao.

        🧠 Personality Rules:
        - Hamesha apne aap ko "{settings.BOT_NAME}" kehkar refer karo.
        - Agar koi pooche "tum kaun ho", "tumhara naam kya hai", "kisne banaya tumhe",
          ya "apne baare me batao", to naturally aur friendly tone me jawab do:
          "Mera naam {settings.BOT_NAME} hai. Mujhe {settings.CREATOR_NAME} ne banaya hai.
          Main ek AI assistant hoon jo tumhe har problem me help karta hai — coding se leke
          life ke sawalon tak. 😊"
        - Tone: mix Hindi + English (Indian conversational style).
        - Friendly, concise aur helpful raho — unnecessarily lamba explanation mat do.
        - Thoda witty ban sakte ho, par kabhi rude nahi hona.
        - Hamesha apna character maintain karo, kabhi break mat karo.
        - Agar user technical sawal pooche to professional aur clear tone me jawab do.
        """
    ),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "Question: {input}\n\nContext:\n{context}")
])

# 🔍 Search Prompt Template with Current Date Context
search_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        f"""
        Tum {settings.BOT_NAME} ho — ek intelligent AI assistant.
        
        IMPORTANT: Aaj ki date hai {{current_date}} (DD Month YYYY format mein).
        
        User ne tumse real-time information maangi hai. 
        Neeche search results diye gaye hain internet se.
        
        CRITICAL INSTRUCTIONS:
        1. Agar user date ya time poocha hai, to HAMESHA current date {{current_date}} use karo
        2. Search results purane ho sakte hain - unhe ignore karo agar wo outdated hain
        3. Current date ko priority do over search results
        4. Apne style me jawab do - Hindi-English mix, friendly aur thoda witty
        5. Agar search results current date ke baare mein nahi hain, to directly current date bata do
        """
    ),
    ("human", "Question: {question}\n\nSearch Results:\n{search_results}\n\nAnswer in your style:")
])


def get_current_datetime_info():
    """Get current date and time information"""
    now = datetime.now()
    return {
        "date": now.strftime("%d %B %Y"),  # 29 October 2025
        "time": now.strftime("%I:%M %p"),  # 02:30 PM
        "day": now.strftime("%A"),  # Monday
        "iso": now.isoformat()
    }


def chat_with_memory_db(db: Session, user_id: UUID, question: str):
    """
    Sharma Ji bot with memory + retrieval + real-time search capability.
    """
    try:
        logger.info(f"📝 Processing question for user {user_id}: {question}")
        
        # Get current datetime
        current_info = get_current_datetime_info()
        logger.info(f"📅 Current date: {current_info['date']}")
        
        # 🧠 Load previous messages from DB
        try:
            db_history = get_user_chat_memory(db, user_id)
            messages = []
            for item in db_history:
                messages.append(HumanMessage(content=item.question))
                messages.append(AIMessage(content=item.answer))
            logger.info(f"✅ Loaded {len(messages)} previous messages")
        except Exception as history_error:
            logger.error(f"❌ Error loading chat history: {history_error}")
            messages = []

        # 🗓️ Direct date/time questions - don't even search
        date_time_keywords = ["aaj ki date", "today date", "aaj ka din", "current date", "kya tarikh", 
                              "aaj kya date", "date kya hai", "time kya hai", "aaj ka time"]
        
        if any(keyword in question.lower() for keyword in date_time_keywords):
            logger.info("📅 Direct date/time question - using system time")
            
            # Generate response directly with current date
            direct_answer = f"Aaj ki date hai {current_info['date']} ({current_info['day']}). " \
                          f"Aur time hai {current_info['time']}. Kuch aur jaanna hai? 😊"
            
            # Save to DB
            try:
                chat_data = ChatMemoryCreate(
                    user_id=user_id,
                    question=question,
                    answer=direct_answer
                )
                save_chat_memory(db, chat_data)
                logger.info("✅ Chat saved to database")
            except Exception as db_error:
                logger.error(f"❌ Database save error: {db_error}")
            
            return {
                "answer": direct_answer,
                "context": [],
                "source_type": "system_time"
            }

        # 🌍 Detect if question needs real-time info (other than date/time)
        realtime_keywords = [
            "latest", "current", "now", "news", "weather",
            "score", "who is", "what is", "recent", "update", "2024", "2025"
        ]
        needs_search = any(keyword in question.lower() for keyword in realtime_keywords)

        # 🔎 Perform real-time search if needed
        if needs_search:
            logger.info(f"🔍 Real-time search triggered for: {question}")
            try:
                # Enhance search query with current date for better results
                enhanced_query = f"{question} {current_info['date']}"
                search_results = search_tool.run(enhanced_query)
                logger.info(f"✅ Search results retrieved: {len(search_results)} chars")

                # Create answer using search results with current date context
                search_chain = search_prompt | llm | StrOutputParser()
                search_answer = search_chain.invoke({
                    "question": question,
                    "search_results": search_results,
                    "current_date": current_info['date']
                })
                logger.info("✅ Search answer generated")

                # Save chat to DB
                try:
                    chat_data = ChatMemoryCreate(
                        user_id=user_id,
                        question=question,
                        answer=search_answer
                    )
                    save_chat_memory(db, chat_data)
                    logger.info("✅ Chat saved to database")
                except Exception as db_error:
                    logger.error(f"❌ Database save error: {db_error}")
                    logger.debug(traceback.format_exc())

                return {
                    "answer": search_answer,
                    "context": [],
                    "source_type": "search"
                }

            except Exception as search_error:
                logger.error(f"❌ Search failed: {search_error}")
                logger.debug(traceback.format_exc())
                # Continue to regular flow if search fails

        # 📚 Retrieve related docs from vector DB (for non-search queries or search fallback)
        try:
            docs = retriever.invoke(question)
            context = "\n\n".join([doc.page_content for doc in docs]) if docs else "No relevant context found."
            logger.info(f"✅ Retrieved {len(docs)} documents from vector DB")
        except Exception as retriever_error:
            logger.error(f"❌ Retriever error: {retriever_error}")
            logger.debug(traceback.format_exc())
            docs = []
            context = "No context available."

        # 🧩 Run through prompt chain
        try:
            chain = prompt | llm | StrOutputParser()
            answer = chain.invoke({
                "input": question,
                "chat_history": messages,
                "context": context
            })
            logger.info("✅ Answer generated successfully")
        except Exception as chain_error:
            logger.error(f"❌ Chain execution error: {chain_error}")
            logger.debug(traceback.format_exc())
            raise

        # 💾 Save chat to DB
        try:
            chat_data = ChatMemoryCreate(
                user_id=user_id,
                question=question,
                answer=answer
            )
            save_chat_memory(db, chat_data)
            logger.info("✅ Chat saved to database")
        except Exception as db_error:
            logger.error(f"❌ Database save error: {db_error}")
            logger.debug(traceback.format_exc())

        return {
            "answer": answer,
            "context": docs,
            "source_type": "vectorstore"
        }

    except Exception as e:
        logger.error(f"❌ Critical error in chat_with_memory_db: {e}")
        logger.error(f"Error type: {type(e).__name__}")
        logger.error(traceback.format_exc())
        
        return {
            "answer": f"Sorry, maine ek technical error encounter kiya: {str(e)}. Please try again!",
            "context": [],
            "source_type": "error",
            "error": str(e)
        }





# tavily with real time data
from langchain_core.tools import Tool
from sqlalchemy.orm import Session
from app.repositories.chat_memory_repository import get_user_chat_memory, save_chat_memory
from app.schemas.chat_memory_schema import ChatMemoryCreate
from langchain_core.messages import HumanMessage, AIMessage
from app.core.config import settings
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from tavily import TavilyClient
from uuid import UUID
import traceback
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# Initialize LLM, Vectorstore, and Tavily Search
try:
    print("🔧 [INIT] Starting initialization...")
    embeddings = OpenAIEmbeddings(api_key=settings.OPENAI_API_KEY)
    CHROMA_PATH = "app/db/chroma_storage_new"
    print(f"📁 [INIT] Chroma path: {CHROMA_PATH}")

    vectorstore = Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=embeddings
    )
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    print("✅ [INIT] Vectorstore initialized")

    llm = ChatOpenAI(
        model=settings.OPENAI_MODEL,
        temperature=0.3,
        api_key=settings.OPENAI_API_KEY
    )
    print(f"✅ [INIT] LLM initialized: {settings.OPENAI_MODEL}")

    tavily_client = TavilyClient(api_key=settings.TAVILY_API_KEY)
    print("✅ [INIT] Tavily Search initialized successfully")
    logger.info("Tavily Search initialized successfully")

except Exception as init_error:
    print(f"❌ [INIT ERROR] {init_error}")
    logger.error(f"Initialization error: {init_error}")
    logger.debug(traceback.format_exc())
    raise

# System Prompt (Hinglish + Personality)
prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        f"""
        Tum {settings.BOT_NAME} ho — ek intelligent, polite aur thoda witty AI assistant 
        jise {settings.CREATOR_NAME} ne banaya hai.

        Rules:
        - Mix Hindi + English
        - Professional yet friendly
        - Apna character hamesha maintain karo
        - Agar user pooche "tum kaun ho", to confidently intro do
        """
    ),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "Question: {input}\n\nContext:\n{context}")
])

# Tavily Search Prompt
search_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        f"""
        Tum {settings.BOT_NAME} ho — ek smart AI assistant.
        Tumhe Tavily search se realtime data milta hai.

        Current date: {{current_date}}.
        Jo data mila hai, use concise aur apne tone me explain karo.
        Agar data outdated ho to user ko warn kar dena.
        """
    ),
    ("human", "Question: {question}\n\nTavily Results:\n{search_results}\n\nAnswer naturally:")
])


def get_current_datetime_info():
    """Get current date/time details"""
    now = datetime.now()
    info = {
        "date": now.strftime("%d %B %Y"),
        "time": now.strftime("%I:%M %p"),
        "day": now.strftime("%A"),
    }
    print(f"📅 [TIME] Current info: {info}")
    return info


def extract_content_from_doc(doc):
    """
    Safely extract content from various document formats.
    Handles Document objects, dicts, and strings.
    """
    try:
        print(f"📄 [DOC] Extracting content from type: {type(doc)}")
        
        # Case 1: Document object with page_content attribute
        if hasattr(doc, "page_content"):
            content = str(doc.page_content).strip()
            print(f"✅ [DOC] Extracted from page_content attribute: {content[:50]}...")
            return content
        
        # Case 2: Dictionary with page_content key
        elif isinstance(doc, dict):
            print(f"🔑 [DOC] Dict keys: {list(doc.keys())}")
            if "page_content" in doc:
                content = str(doc["page_content"]).strip()
                print(f"✅ [DOC] Extracted from page_content key: {content[:50]}...")
                return content
            elif "content" in doc:
                content = str(doc["content"]).strip()
                print(f"✅ [DOC] Extracted from content key: {content[:50]}...")
                return content
            else:
                content = str(doc).strip()
                print(f"⚠️ [DOC] No content key, using string repr: {content[:50]}...")
                return content
        
        # Case 3: Plain string
        elif isinstance(doc, str):
            print(f"✅ [DOC] Already a string: {doc[:50]}...")
            return doc.strip()
        
        # Case 4: Unknown type, convert to string
        else:
            content = str(doc).strip()
            print(f"⚠️ [DOC] Unknown type, converting to string: {content[:50]}...")
            logger.warning(f"Unknown document type: {type(doc)}")
            return content
            
    except Exception as e:
        print(f"❌ [DOC ERROR] {e}")
        logger.error(f"Error extracting content from doc: {e}")
        return ""


def serialize_docs(docs):
    """
    Convert documents to JSON-serializable format.
    Returns a list of dicts with content and metadata.
    """
    print(f"🔄 [SERIALIZE] Starting serialization of {len(docs)} docs")
    serialized = []
    
    for i, doc in enumerate(docs):
        try:
            print(f"🔄 [SERIALIZE] Doc {i}: type={type(doc)}")
            
            # Extract content
            content = extract_content_from_doc(doc)
            
            # Extract metadata if available
            metadata = {}
            if hasattr(doc, "metadata"):
                metadata = doc.metadata
                print(f"📋 [SERIALIZE] Doc {i}: Found metadata attribute")
            elif isinstance(doc, dict) and "metadata" in doc:
                metadata = doc["metadata"]
                print(f"📋 [SERIALIZE] Doc {i}: Found metadata key")
            
            result = {
                "content": content,
                "metadata": metadata
            }
            serialized.append(result)
            print(f"✅ [SERIALIZE] Doc {i}: Successfully serialized")
            
        except Exception as e:
            print(f"❌ [SERIALIZE ERROR] Doc {i}: {e}")
            logger.error(f"Error serializing doc: {e}")
            continue
    
    print(f"✅ [SERIALIZE] Completed: {len(serialized)} docs serialized")
    return serialized


def detect_realtime_intent(question: str) -> bool:
    """Smart detection for realtime or dynamic queries."""
    q = question.lower().strip()

    realtime_keywords = [
        "latest", "current", "today", "now", "live", "update", "trending", "recent", "breaking", "abhi",
        "aaj", "abhi ka", "kal ka", "score", "match", "price", "rate", "value", "weather", "temperature",
        "winner", "ipl", "news", "gold", "silver", "bitcoin", "stock", "sensex", "bazar", "market"
    ]

    finance_words = ["price", "rate", "value", "gold", "silver", "usd", "bitcoin", "crypto", "share", "stock"]
    event_words = ["ipl", "match", "score", "winner", "tournament", "game"]
    news_words = ["news", "update", "today", "breaking", "headline"]
    weather_words = ["weather", "temperature", "climate", "rain", "humidity"]

    if any(word in q for word in ["aaj", "abhi", "today", "current", "latest", "now"]) and \
       any(w in q for w in (finance_words + event_words + news_words + weather_words)):
        return True

    if any(str(y) in q for y in range(2023, 2031)):
        return True

    if any(k in q for k in realtime_keywords):
        return True

    return False




def sharmaji_chat(db: Session, user_id: str, user_message: str):
    """
    Main chat logic that uses long-term memory + realtime data + OpenAI.
    Each step includes console logs for debugging and understanding flow.
    """
    print("\n🧠 [SharmaJi Chat Started]")
    print(f"👤 User ID: {user_id}")
    print(f"💬 User Message: {user_message}")

    # 1️⃣ Get recent memories
    print("\n[STEP 1] Fetching recent memories...")
    recent_memories = chat_long_memory_service.get_user_recent_memories(db, user_id, limit=10)
    print(f"✅ Recent memories fetched: {len(recent_memories.memories)} entries found.")

    # 2️⃣ Combine memories into context
    print("\n[STEP 2] Building context for AI prompt...")
    context_messages = [
        {
            "role": "system",
            "content": "You are Sharma Ji, a friendly AI assistant who remembers previous chats and answers like ChatGPT or Grok."
        }
    ]

    for i, mem in enumerate(recent_memories.memories, start=1):
        print(f"   ↳ Memory {i}: ({mem.role}) {mem.content[:60]}...")
        context_messages.append({"role": mem.role, "content": mem.content})

    context_messages.append({"role": "user", "content": user_message})
    print(f"✅ Context built with {len(context_messages)} total messages.")

    # 3️⃣ Check if message needs realtime data
    print("\n[STEP 3] Checking if realtime data is required...")
    realtime_data = ""
    if any(keyword in user_message.lower() for keyword in ["today", "latest", "current", "news", "update"]):
        print("🌐 Realtime keywords detected → fetching data from Tavily...")
        try:
            data = fetch_realtime_data(user_message)
            if data:
                realtime_data = f"\n[Realtime Info from Tavily]: {data[0].get('content', '')}"
                context_messages.append({"role": "system", "content": realtime_data})
                print("✅ Realtime data successfully added to context.")
            else:
                print("⚠️ No realtime data returned from Tavily.")
        except Exception as e:
            print(f"❌ Error fetching realtime data: {e}")
    else:
        print("ℹ️ No realtime data needed for this query.")

    # 4️⃣ Get AI reply
    print("\n[STEP 4] Sending context to AI model (OpenAI/Groq)...")
    try:
        ai_reply = get_ai_response(context_messages)
        print(f"🤖 AI Reply Received: {ai_reply[:120]}...")
    except Exception as e:
        print(f"❌ Error while getting AI response: {e}")
        ai_reply = "Sorry, something went wrong while generating my response."

    # 5️⃣ Store both user and AI messages in memory
    print("\n[STEP 5] Saving messages to long-term memory...")
    try:
        chat_long_memory_service.create_memory(
            db, user_id=user_id, role="user", content=user_message, memory_type="fact"
        )
        chat_long_memory_service.create_memory(
            db, user_id=user_id, role="assistant", content=ai_reply, memory_type="response"
        )
        print("✅ Both user and AI messages saved successfully.")
    except Exception as e:
        print(f"❌ Error saving chat memory: {e}")

    # 6️⃣ Return the bot's response
    print("\n[STEP 6] Preparing final response for frontend...")
    response = {
        "reply": ai_reply,
        "realtime_info": realtime_data if realtime_data else None
    }

    print("🎯 Final Response Ready → Returning to user.\n")
    return response