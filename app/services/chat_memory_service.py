# from langchain_core.tools import Tool
# from sqlalchemy.orm import Session
# from app.repositories.chat_memory_repository import get_user_chat_memory, save_chat_memory
# from app.schemas.chat_memory_schema import ChatMemoryCreate
# from langchain_core.messages import HumanMessage, AIMessage
# from app.core.config import settings
# from langchain_openai import ChatOpenAI, OpenAIEmbeddings
# from langchain_community.vectorstores import Chroma
# from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
# from langchain_core.output_parsers import StrOutputParser
# from uuid import UUID
# from langchain_community.tools import DuckDuckGoSearchRun
# import traceback
# import logging
# from datetime import datetime

# logger = logging.getLogger(__name__)

# # 🧠 Initialize LLM and Vector DB
# try:
#     embeddings = OpenAIEmbeddings(api_key=settings.OPENAI_API_KEY)
#     CHROMA_PATH = "app/db/chroma_storage"
#     vectorstore = Chroma(persist_directory=CHROMA_PATH, embedding_function=embeddings)
#     retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
#     llm = ChatOpenAI(model=settings.OPENAI_MODEL, temperature=0.3, api_key=settings.OPENAI_API_KEY)
#     search_tool = DuckDuckGoSearchRun()
#     logger.info("✅ All tools initialized successfully")
# except Exception as init_error:
#     logger.error(f"❌ Initialization error: {init_error}")
#     logger.debug(traceback.format_exc())

# # 💬 System Prompt
# prompt = ChatPromptTemplate.from_messages([
#     (
#         "system",
#         f"""
#         Tum {settings.BOT_NAME} ho — ek intelligent, polite aur thoda witty AI assistant 
#         jise {settings.CREATOR_NAME} ne banaya hai 😎.

#         Kuch khaas baatein mere baare mein:
#         • Mujhe {settings.CREATOR_NAME} ne banaya hai.
#         • Main Hindi-English dono me baat karta hoon.
#         • Main coding, AI, aur daily life ke sawalon ka jawab deta hoon.
#         • Thoda witty hoon, par respect ke saath.
#         • Mere paas updated knowledge hai (jitna mujhe diya gaya hai).

#         Agar koi pooche "tum kaun ho" ya "apne baare me batao", 
#         to apne style me confidently ye sab batao.

#         🧠 Personality Rules:
#         - Hamesha apne aap ko "{settings.BOT_NAME}" kehkar refer karo.
#         - Agar koi pooche "tum kaun ho", "tumhara naam kya hai", "kisne banaya tumhe",
#           ya "apne baare me batao", to naturally aur friendly tone me jawab do:
#           "Mera naam {settings.BOT_NAME} hai. Mujhe {settings.CREATOR_NAME} ne banaya hai.
#           Main ek AI assistant hoon jo tumhe har problem me help karta hai — coding se leke
#           life ke sawalon tak. 😊"
#         - Tone: mix Hindi + English (Indian conversational style).
#         - Friendly, concise aur helpful raho — unnecessarily lamba explanation mat do.
#         - Thoda witty ban sakte ho, par kabhi rude nahi hona.
#         - Hamesha apna character maintain karo, kabhi break mat karo.
#         - Agar user technical sawal pooche to professional aur clear tone me jawab do.
#         """
#     ),
#     MessagesPlaceholder(variable_name="chat_history"),
#     ("human", "Question: {input}\n\nContext:\n{context}")
# ])

# # 🔍 Search Prompt Template with Current Date Context
# search_prompt = ChatPromptTemplate.from_messages([
#     (
#         "system",
#         f"""
#         Tum {settings.BOT_NAME} ho — ek intelligent AI assistant.
        
#         IMPORTANT: Aaj ki date hai {{current_date}} (DD Month YYYY format mein).
        
#         User ne tumse real-time information maangi hai. 
#         Neeche search results diye gaye hain internet se.
        
#         CRITICAL INSTRUCTIONS:
#         1. Agar user date ya time poocha hai, to HAMESHA current date {{current_date}} use karo
#         2. Search results purane ho sakte hain - unhe ignore karo agar wo outdated hain
#         3. Current date ko priority do over search results
#         4. Apne style me jawab do - Hindi-English mix, friendly aur thoda witty
#         5. Agar search results current date ke baare mein nahi hain, to directly current date bata do
#         """
#     ),
#     ("human", "Question: {question}\n\nSearch Results:\n{search_results}\n\nAnswer in your style:")
# ])


# def get_current_datetime_info():
#     """Get current date and time information"""
#     now = datetime.now()
#     return {
#         "date": now.strftime("%d %B %Y"),  # 29 October 2025
#         "time": now.strftime("%I:%M %p"),  # 02:30 PM
#         "day": now.strftime("%A"),  # Monday
#         "iso": now.isoformat()
#     }


# def chat_with_memory_db(db: Session, user_id: UUID, question: str):
#     """
#     Sharma Ji bot with memory + retrieval + real-time search capability.
#     """
#     try:
#         logger.info(f"📝 Processing question for user {user_id}: {question}")
        
#         # Get current datetime
#         current_info = get_current_datetime_info()
#         logger.info(f"📅 Current date: {current_info['date']}")
        
#         # 🧠 Load previous messages from DB
#         try:
#             db_history = get_user_chat_memory(db, user_id)
#             messages = []
#             for item in db_history:
#                 messages.append(HumanMessage(content=item.question))
#                 messages.append(AIMessage(content=item.answer))
#             logger.info(f"✅ Loaded {len(messages)} previous messages")
#         except Exception as history_error:
#             logger.error(f"❌ Error loading chat history: {history_error}")
#             messages = []

#         # 🗓️ Direct date/time questions - don't even search
#         date_time_keywords = ["aaj ki date", "today date", "aaj ka din", "current date", "kya tarikh", 
#                               "aaj kya date", "date kya hai", "time kya hai", "aaj ka time"]
        
#         if any(keyword in question.lower() for keyword in date_time_keywords):
#             logger.info("📅 Direct date/time question - using system time")
            
#             # Generate response directly with current date
#             direct_answer = f"Aaj ki date hai {current_info['date']} ({current_info['day']}). " \
#                           f"Aur time hai {current_info['time']}. Kuch aur jaanna hai? 😊"
            
#             # Save to DB
#             try:
#                 chat_data = ChatMemoryCreate(
#                     user_id=user_id,
#                     question=question,
#                     answer=direct_answer
#                 )
#                 save_chat_memory(db, chat_data)
#                 logger.info("✅ Chat saved to database")
#             except Exception as db_error:
#                 logger.error(f"❌ Database save error: {db_error}")
            
#             return {
#                 "answer": direct_answer,
#                 "context": [],
#                 "source_type": "system_time"
#             }

#         # 🌍 Detect if question needs real-time info (other than date/time)
#         realtime_keywords = [
#             "latest", "current", "now", "news", "weather",
#             "score", "who is", "what is", "recent", "update", "2024", "2025"
#         ]
#         needs_search = any(keyword in question.lower() for keyword in realtime_keywords)

#         # 🔎 Perform real-time search if needed
#         if needs_search:
#             logger.info(f"🔍 Real-time search triggered for: {question}")
#             try:
#                 # Enhance search query with current date for better results
#                 enhanced_query = f"{question} {current_info['date']}"
#                 search_results = search_tool.run(enhanced_query)
#                 logger.info(f"✅ Search results retrieved: {len(search_results)} chars")

#                 # Create answer using search results with current date context
#                 search_chain = search_prompt | llm | StrOutputParser()
#                 search_answer = search_chain.invoke({
#                     "question": question,
#                     "search_results": search_results,
#                     "current_date": current_info['date']
#                 })
#                 logger.info("✅ Search answer generated")

#                 # Save chat to DB
#                 try:
#                     chat_data = ChatMemoryCreate(
#                         user_id=user_id,
#                         question=question,
#                         answer=search_answer
#                     )
#                     save_chat_memory(db, chat_data)
#                     logger.info("✅ Chat saved to database")
#                 except Exception as db_error:
#                     logger.error(f"❌ Database save error: {db_error}")
#                     logger.debug(traceback.format_exc())

#                 return {
#                     "answer": search_answer,
#                     "context": [],
#                     "source_type": "search"
#                 }

#             except Exception as search_error:
#                 logger.error(f"❌ Search failed: {search_error}")
#                 logger.debug(traceback.format_exc())
#                 # Continue to regular flow if search fails

#         # 📚 Retrieve related docs from vector DB (for non-search queries or search fallback)
#         try:
#             docs = retriever.invoke(question)
#             context = "\n\n".join([doc.page_content for doc in docs]) if docs else "No relevant context found."
#             logger.info(f"✅ Retrieved {len(docs)} documents from vector DB")
#         except Exception as retriever_error:
#             logger.error(f"❌ Retriever error: {retriever_error}")
#             logger.debug(traceback.format_exc())
#             docs = []
#             context = "No context available."

#         # 🧩 Run through prompt chain
#         try:
#             chain = prompt | llm | StrOutputParser()
#             answer = chain.invoke({
#                 "input": question,
#                 "chat_history": messages,
#                 "context": context
#             })
#             logger.info("✅ Answer generated successfully")
#         except Exception as chain_error:
#             logger.error(f"❌ Chain execution error: {chain_error}")
#             logger.debug(traceback.format_exc())
#             raise

#         # 💾 Save chat to DB
#         try:
#             chat_data = ChatMemoryCreate(
#                 user_id=user_id,
#                 question=question,
#                 answer=answer
#             )
#             save_chat_memory(db, chat_data)
#             logger.info("✅ Chat saved to database")
#         except Exception as db_error:
#             logger.error(f"❌ Database save error: {db_error}")
#             logger.debug(traceback.format_exc())

#         return {
#             "answer": answer,
#             "context": docs,
#             "source_type": "vectorstore"
#         }

#     except Exception as e:
#         logger.error(f"❌ Critical error in chat_with_memory_db: {e}")
#         logger.error(f"Error type: {type(e).__name__}")
#         logger.error(traceback.format_exc())
        
#         return {
#             "answer": f"Sorry, maine ek technical error encounter kiya: {str(e)}. Please try again!",
#             "context": [],
#             "source_type": "error",
#             "error": str(e)
#         }






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


def chat_with_memory_db(db: Session, user_id: UUID, question: str):
    """Main Sharma Ji Bot Function (Tavily + Memory + Vector + LLM)"""
    try:
        print(f"\n{'='*60}")
        print(f"🚀 [START] New request")
        print(f"👤 [USER] ID: {user_id}")
        print(f"❓ [QUESTION] {question}")
        print(f"{'='*60}\n")
        
        logger.info(f"Processing question: {question}")
        current_info = get_current_datetime_info()

        # Load chat memory
        print("💾 [MEMORY] Loading chat history...")
        db_history = get_user_chat_memory(db, user_id)
        print(f"💾 [MEMORY] Found {len(db_history)} previous messages")
        
        messages = []
        for item in db_history:
            messages.append(HumanMessage(content=item.question))
            messages.append(AIMessage(content=item.answer))
        print(f"💾 [MEMORY] Built {len(messages)} message objects")

        # Handle direct date/time queries
        date_time_keywords = [
            "aaj ki date", "today date", "aaj ka din", "current date",
            "kya tarikh", "aaj kya date", "date kya hai", "time kya hai"
        ]
        print(f"🔍 [CHECK] Checking for date/time keywords...")
        if any(k in question.lower() for k in date_time_keywords):
            print("✅ [CHECK] Date/time keyword detected!")
            answer = f"Aaj {current_info['day']} hai, date {current_info['date']} aur time {current_info['time']} hai."
            save_chat_memory(db, ChatMemoryCreate(user_id=user_id, question=question, answer=answer))
            print(f"💬 [ANSWER] {answer}")
            return {"answer": answer, "context": [], "source_type": "system_time"}

        # Tavily Search (for real-time info)
        realtime_keywords = ["latest", "current", "news", "weather", "today", "2025", "score", "update", "ipl", "match", "win", "winner"]
        print(f"🔍 [CHECK] Checking for realtime keywords...")
        needs_search = any(k in question.lower() for k in realtime_keywords)
        print(f"🔍 [CHECK] Needs search: {needs_search}")

        if needs_search:
            try:
                print(f"🌐 [TAVILY] Search triggered for: {question}")
                logger.info(f"Tavily Search triggered for: {question}")
                
                tavily_results = tavily_client.search(query=question, max_results=5)
                print(f"🌐 [TAVILY] Received {len(tavily_results.get('results', []))} results")

                formatted_results = "\n\n".join(
                    [f"- {r.get('title', 'No Title')}: {r.get('url', 'No URL')}\n{r.get('content', 'No content')}" 
                     for r in tavily_results.get("results", [])]
                )
                print(f"🌐 [TAVILY] Formatted results length: {len(formatted_results)} chars")

                print("🤖 [LLM] Generating answer from Tavily results...")
                chain = search_prompt | llm | StrOutputParser()
                search_answer = chain.invoke({
                    "question": question,
                    "search_results": formatted_results,
                    "current_date": current_info['date']
                })
                print(f"✅ [LLM] Answer generated: {search_answer[:100]}...")

                print("💾 [MEMORY] Saving to database...")
                save_chat_memory(db, ChatMemoryCreate(user_id=user_id, question=question, answer=search_answer))
                print("✅ [MEMORY] Saved successfully")
                
                # Serialize Tavily results to ensure JSON compatibility
                print("🔄 [TAVILY] Serializing Tavily results...")
                serialized_tavily = []
                for r in tavily_results.get("results", []):
                    try:
                        serialized_tavily.append({
                            "title": str(r.get("title", "")),
                            "url": str(r.get("url", "")),
                            "content": str(r.get("content", "")),
                            "score": float(r.get("score", 0.0)) if r.get("score") else 0.0
                        })
                    except Exception as ser_err:
                        print(f"⚠️ [TAVILY] Failed to serialize result: {ser_err}")
                        continue
                
                print(f"✅ [TAVILY] Serialized {len(serialized_tavily)} results")
                
                result = {
                    "answer": search_answer,
                    "context": serialized_tavily,
                    "source_type": "tavily_search"
                }
                print(f"✅ [RETURN] Returning Tavily result with {len(serialized_tavily)} context items")
                return result

            except Exception as tavily_error:
                print(f"❌ [TAVILY ERROR] {tavily_error}")
                print(f"❌ [TAVILY TRACE] {traceback.format_exc()}")
                logger.error(f"Tavily Search Error: {tavily_error}")
                logger.debug(traceback.format_exc())
                print("⚠️ [FALLBACK] Continuing to vector fallback...")

        # Vector DB Retrieval (fallback)
        print("🔍 [VECTOR] Starting vector retrieval...")
        context = "No relevant context found."
        docs = []
        serialized_context = []

        try:
            print(f"🔍 [VECTOR] Invoking retriever with question: {question}")
            docs = retriever.invoke(question)
            print(f"✅ [VECTOR] Retriever returned {len(docs)} items")
            
            if docs:
                print(f"🔍 [VECTOR] First doc type: {type(docs[0])}")
                print(f"🔍 [VECTOR] First doc content: {docs[0]}")
                
                # Check if it's a dict with direct access
                if isinstance(docs[0], dict):
                    print(f"🔍 [VECTOR] First doc keys: {list(docs[0].keys())}")
            else:
                print("⚠️ [VECTOR] No docs returned!")

            context_parts = []
            for i, doc in enumerate(docs):
                try:
                    print(f"🔍 [VECTOR] Processing doc {i}... Type: {type(doc)}")
                    content = extract_content_from_doc(doc)
                    
                    if content:
                        context_parts.append(content)
                        print(f"✅ [VECTOR] Doc {i} added: {content[:100]}...")
                    else:
                        print(f"⚠️ [VECTOR] Doc {i} returned empty content")
                        
                except Exception as doc_error:
                    print(f"❌ [VECTOR] Error processing doc {i}: {doc_error}")
                    print(f"❌ [VECTOR] Doc {i} trace: {traceback.format_exc()}")
                    continue

            context = "\n\n".join(context_parts) if context_parts else "No relevant context found."
            print(f"🧩 [VECTOR] Built context from {len(context_parts)} chunks")
            print(f"🧩 [VECTOR] Total context length: {len(context)} chars")
            
            # Serialize docs for JSON response
            print("🔄 [VECTOR] Starting serialization...")
            try:
                serialized_context = serialize_docs(docs)
                print(f"✅ [VECTOR] Serialization complete: {len(serialized_context)} items")
            except Exception as serialize_error:
                print(f"❌ [VECTOR] Serialization failed: {serialize_error}")
                print(f"❌ [VECTOR] Serialize trace: {traceback.format_exc()}")
                serialized_context = []

        except Exception as retriever_error:
            print(f"❌ [VECTOR ERROR] {retriever_error}")
            print(f"❌ [VECTOR TRACE] {traceback.format_exc()}")
            logger.error(f"❌ Retriever Error: {retriever_error}")
            logger.debug(traceback.format_exc())
            context = "Context retrieval failed."
            serialized_context = []

        # Generate final answer
        try:
            print("🤖 [LLM] Generating final answer...")
            print(f"🤖 [LLM] Context length: {len(context)}")
            print(f"🤖 [LLM] Chat history length: {len(messages)}")
            
            chain = prompt | llm | StrOutputParser()
            answer = chain.invoke({
                "input": question,
                "chat_history": messages,
                "context": context
            })
            print(f"✅ [LLM] Answer generated: {answer[:100]}...")

            print("💾 [MEMORY] Saving to database...")
            save_chat_memory(db, ChatMemoryCreate(user_id=user_id, question=question, answer=answer))
            print("✅ [MEMORY] Saved successfully")
            
            result = {
                "answer": answer,
                "context": serialized_context,
                "source_type": "vectorstore"
            }
            print(f"✅ [RETURN] Returning vectorstore result")
            print(f"✅ [RETURN] Context items: {len(serialized_context)}")
            return result

        except Exception as llm_error:
            print(f"❌ [LLM ERROR] {llm_error}")
            print(f"❌ [LLM TRACE] {traceback.format_exc()}")
            logger.error(f"LLM generation error: {llm_error}")
            answer = "Sorry, answer generate nahi kar paya abhi. Thodi der baad try karo."
            save_chat_memory(db, ChatMemoryCreate(user_id=user_id, question=question, answer=answer))
            return {
                "answer": answer,
                "context": [],
                "source_type": "error"
            }

    except Exception as e:
        print(f"❌ [CRITICAL ERROR] {e}")
        print(f"❌ [CRITICAL TRACE] {traceback.format_exc()}")
        logger.error(f"Critical Error: {e}")
        logger.debug(traceback.format_exc())
        return {
            "answer": f"Sorry, ek technical issue hua: {e}",
            "context": [],
            "source_type": "error"
        }