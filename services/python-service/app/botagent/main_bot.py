"""
RAG Chatbot with Function Calling
Combines document search (RAG) with database function calling via MCP server
"""
import os
import time
import asyncio
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# Import existing components
from app.botagent.vectordb import PineconeManager
from app.botagent.mcp_server import StudentDataMCPServer

# LlamaIndex imports with fallback
try:
    from llama_index.core.chat_engine import CondensePlusContextChatEngine
    from llama_index.core.memory import ChatMemoryBuffer
    from llama_index.core import get_response_synthesizer
    from llama_index.core.retrievers import VectorIndexRetriever
    from llama_index.core.query_engine import RetrieverQueryEngine
    from llama_index.core.postprocessor import SimilarityPostprocessor
except ImportError as e:
    print(f"❌ LlamaIndex import error: {e}")
    print("   Install: pip install llama-index")

try:
    from llama_index.llms.openai import OpenAI
except ImportError:
    try:
        from llama_index_llms_openai import OpenAI
    except ImportError:
        print("❌ Missing OpenAI LLM. Install: pip install llama-index-llms-openai")

class RAGBot:
    """RAG Chatbot with document search and function calling"""
    
    def __init__(
        self,
        pinecone_api_key: str,
        openai_api_key: str,
        index_name: str = "attacker2",
        model: str = "gpt-4.1-mini"
    ):
        """Initialize RAG bot with Pinecone, OpenAI, and MCP server"""
        
        # Set environment variables
        os.environ["OPENAI_API_KEY"] = openai_api_key
        
        # Initialize MCP server for student data
        self.mcp_server = StudentDataMCPServer()
        self._mcp_initialized = False
        
        # Initialize Pinecone manager
        self.pinecone_manager = PineconeManager(
            api_key=pinecone_api_key,
            index_name=index_name
        )
        
        # Connect to existing index
        if not self.pinecone_manager.create_index():
            raise Exception("Failed to connect to Pinecone index")
        
        # Initialize LLM
        self.llm = OpenAI(
            model=model,
            temperature=0.7,
            max_tokens=400
        )
        
        # Load existing vector index
        if not self.pinecone_manager._load_existing_index():
            raise Exception("Failed to load existing vector index")
        
        # Create query engine
        self.query_engine = self._create_query_engine()
        
        # Chat memory
        self.memory = ChatMemoryBuffer.from_defaults(token_limit=20000)
        
        print(f"✅ RAG Bot initialized with index: {index_name}")
        
    async def _ensure_mcp_connected(self):
        """Ensure MCP server is connected to database"""
        if not self._mcp_initialized:
            try:
                await self.mcp_server.connect_database()
                self._mcp_initialized = True
                print("✅ MCP Academic Server connected")
            except Exception as e:
                print(f"❌ MCP connection failed: {e}")
                raise
    
    def _create_query_engine(self):
        """Create query engine for RAG"""
        try:
            # Create retriever
            retriever = VectorIndexRetriever(
                index=self.pinecone_manager.vector_index,
                similarity_top_k=5
            )
            
            # Create response synthesizer
            response_synthesizer = get_response_synthesizer(
                llm=self.llm,
                text_qa_template=self._get_qa_template(),
                refine_template=self._get_refine_template()
            )
            
            # Create query engine
            query_engine = RetrieverQueryEngine(
                retriever=retriever,
                response_synthesizer=response_synthesizer,
                node_postprocessors=[
                    SimilarityPostprocessor(similarity_cutoff=0.3)
                ]
            )
            
            return query_engine
            
        except Exception as e:
            print(f"❌ Error creating query engine: {e}")
            return None
    
    def _get_qa_template(self):
        """Get QA template for RAG responses"""
        from llama_index.core.prompts import PromptTemplate
        
        qa_template = PromptTemplate(
            "Bạn là trợ lý AI chuyên về tín dụng sinh viên. "
            "Dựa trên thông tin sau đây: {context_str} "
            "Hãy trả lời câu hỏi: {query_str} "
            "Quy tắc trả lời: Trả lời bằng 1 đoạn văn liền mạch, không xuống dòng, "
            "không dấu gạch đầu dòng, không markdown, chỉ văn bản thuần túy. "
            "Nếu không có thông tin thì nói tôi không biết "
            "Trả lời:"
        )
        
        return qa_template
    
    def _get_refine_template(self):
        """Get refine template for multi-document answers"""
        from llama_index.core.prompts import PromptTemplate
        
        refine_template = PromptTemplate(
            "Câu hỏi: {query_str} "
            "Thông tin bổ sung: {context_msg} "
            "Câu trả lời hiện tại: {existing_answer} "
            "Hãy cải thiện câu trả lời thành 1 đoạn văn liền mạch, không xuống dòng, không markdown:"
        )
        
        return refine_template
    
    async def chat(self, message: str, citizen_id: Optional[str] = None) -> Dict[str, Any]:
        """Smart chat method using LLM to decide response strategy with conversation memory"""
        
        start_time = time.time()
        
        try:
            # Add user message to memory
            from llama_index.core.llms import ChatMessage
            user_message = ChatMessage(role="user", content=message)
            self.memory.put(user_message)
            
            # Get conversation context for better classification
            conversation_history = self._get_recent_conversation_context()
            
            # Use LLM to classify the question and decide response strategy
            response_strategy = await self._classify_question(message, citizen_id, conversation_history)
            
            response_dict = {}
            
            if response_strategy == "direct_answer":
                # LLM can answer directly without needing documents or personal data
                response_dict = await self._handle_direct_response(message, start_time, conversation_history)
            elif response_strategy == "call_data_db":
                # Database questions - get data from MCP server
                response_dict = await self._handle_database_data(message, citizen_id, start_time, conversation_history)
            elif response_strategy == "personal":
                # Personal questions - provide general guidance since no personal data available
                response_dict = await self._handle_personal_guidance(message, start_time, conversation_history)
            elif response_strategy == "rag_search":
                # Need to search documents for specific information
                response_dict = await self._handle_rag_query(message, start_time, conversation_history)
            else:
                # Default to RAG if unsure
                response_dict = await self._handle_rag_query(message, start_time, conversation_history)
            
            # Add assistant response to memory
            assistant_message = ChatMessage(role="assistant", content=response_dict["response"])
            self.memory.put(assistant_message)
            
            # Add conversation info to response
            response_dict["conversation_id"] = id(self.memory)
            response_dict["memory_tokens"] = len(str(self.memory.get()))
            
            return response_dict
                
        except Exception as e:
            error_response = {
                "response": f"Xin lỗi, tôi gặp lỗi khi xử lý câu hỏi: {str(e)}",
                "source": "error",
                "processing_time": time.time() - start_time,
                "error": str(e)
            }
            
            # Still add to memory for debugging
            try:
                from llama_index.core.llms import ChatMessage
                error_message = ChatMessage(role="assistant", content=error_response["response"])
                self.memory.put(error_message)
            except:
                pass
                
            return error_response
    
    def _get_recent_conversation_context(self) -> str:
        """Get recent conversation context for better understanding"""
        try:
            # Get recent messages from memory
            chat_history = self.memory.get()
            
            if not chat_history:
                return "Không có lịch sử trò chuyện."
            
            # Format recent conversation (last 4 messages)
            recent_messages = chat_history[-6:] if len(chat_history) > 4 else chat_history
            context_parts = []
            
            for msg in recent_messages:
                role = "Người dùng" if msg.role == "user" else "Trợ lý"
                context_parts.append(f"{role}: {msg.content[:100]}")
            
            return "Lịch sử trò chuyện gần đây:\n" + "\n".join(context_parts)
            
        except Exception as e:
            print(f"❌ Error getting conversation context: {e}")
            return "Không thể lấy lịch sử trò chuyện."
    
    def clear_memory(self):
        """Clear conversation memory"""
        try:
            self.memory.reset()
            print("✅ Conversation memory cleared")
        except Exception as e:
            print(f"❌ Error clearing memory: {e}")
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get conversation summary and statistics"""
        try:
            chat_history = self.memory.get()
            
            if not chat_history:
                return {
                    "message_count": 0,
                    "memory_tokens": 0,
                    "status": "empty"
                }
            
            user_messages = [msg for msg in chat_history if msg.role == "user"]
            assistant_messages = [msg for msg in chat_history if msg.role == "assistant"]
            
            return {
                "message_count": len(chat_history),
                "user_messages": len(user_messages),
                "assistant_messages": len(assistant_messages),
                "memory_tokens": len(str(chat_history)),
                "recent_topics": [msg.content[:50] + "..." for msg in user_messages[-3:]],
                "status": "active"
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "status": "error"
            }
    
    async def _handle_personal_guidance(self, message: str, start_time: float, conversation_history: str = "") -> Dict[str, Any]:
        """Handle personal questions by providing general guidance"""
        
        try:
            personal_prompt = f"""
Bạn là trợ lý AI chuyên về tín dụng sinh viên của Student Credit.
Người dùng hỏi một câu hỏi cá nhân: "{message}"

Lịch sử trò chuyện:
{conversation_history}

Hãy trả lời một cách hữu ích và hướng dẫn người dùng:
- Đưa ra thông tin tổng quan hữu ích về chủ đề họ hỏi
- Giải thích các yếu tố chung ảnh hưởng đến vấn đề này
- Hướng dẫn cách tự đánh giá hoặc chuẩn bị
- Tham khảo lịch sử trò chuyện để cung cấp câu trả lời phù hợp
- Trả lời thân thiện, hữu ích

Quy tắc trả lời:
- Trả lời bằng tiếng Việt tự nhiên
- Đưa ra thông tin hữu ích và thực tiễn
- Không nói "tôi không thể trả lời"
- 3-4 câu ngắn gọn

Trả lời:
"""
            
            response = await self.llm.acomplete(personal_prompt)
            response_text = str(response).strip()
            
            return {
                "response": response_text,
                "source": "personal_general",
                "processing_time": round(time.time() - start_time, 3),
                "requires_login": False,
                "suggestion": "Thông tin tổng quan về chủ đề bạn quan tâm"
            }
            
        except Exception as e:
            print(f"❌ Personal query error: {e}")
            return {
                "response": "Tôi có thể cung cấp thông tin tổng quan về vay vốn sinh viên. Để có lời khuyên cụ thể hơn, bạn có thể chia sẻ thêm về tình huống của mình. Bạn có muốn biết về điều kiện vay, quy trình, hay lãi suất không?",
                "source": "personal_fallback",
                "processing_time": round(time.time() - start_time, 3),
                "requires_login": False,
                "error": str(e)
            }
    
    async def _handle_database_data(self, message: str, citizen_id: Optional[str], start_time: float, conversation_history: str = "") -> Dict[str, Any]:
        """Handle database data questions using MCP server"""
        
        if not citizen_id:
            return {
                "response": "Để truy cập thông tin cá nhân, bạn cần đăng nhập vào hệ thống trước. Vui lòng đăng nhập để tôi có thể cung cấp thông tin chính xác về dữ liệu cá nhân của bạn.",
                "source": "database_login_required",
                "processing_time": round(time.time() - start_time, 3),
                "requires_login": True
            }
        
        try:
            # Ensure MCP server is connected
            await self._ensure_mcp_connected()
            
            # Check if this is a pure greeting message (not mixed with questions)
            greeting_keywords = ["xin chào", "hello", "chào", "hi", "hey"]
            academic_keywords = ["gpa", "điểm", "tín chỉ", "học bổng", "thành tích", "câu lạc bộ", "hoạt động", "lãnh đạo", "năm học", "học kỳ"]
            
            # Check if it's a pure greeting (no academic keywords)
            is_pure_greeting = (
                any(keyword in message.lower() for keyword in greeting_keywords) and
                not any(keyword in message.lower() for keyword in academic_keywords) and
                len(message.strip()) < 20  # Short message, likely just greeting
            )
            
            if is_pure_greeting:
                # Get user data for greeting
                user_data = await self.mcp_server.get_user_data(citizen_id)
                
                if "error" not in user_data:
                    user_name = user_data.get('name', 'bạn')
                    return {
                        "response": f"Xin chào {user_name}! Tôi là trợ lý AI của Student Credit. Tôi có thể giúp bạn tìm hiểu về thông tin học tập, hồ sơ sinh viên và các dịch vụ vay vốn. Bạn cần hỗ trợ gì hôm nay?",
                        "source": "personalized_greeting",
                        "processing_time": round(time.time() - start_time, 3),
                        "user_data": user_data,
                        "citizen_id": citizen_id
                    }
                else:
                    # Fallback if user data not found
                    return {
                        "response": "Xin chào! Tôi là trợ lý AI của Student Credit. Tôi có thể giúp bạn tìm hiểu về thông tin học tập, hồ sơ sinh viên và các dịch vụ vay vốn. Bạn cần hỗ trợ gì hôm nay?",
                        "source": "greeting_fallback",
                        "processing_time": round(time.time() - start_time, 3),
                        "citizen_id": citizen_id
                    }
            
            # Get academic data from MCP server for other questions
            academic_data = await self.mcp_server.get_academic_data(citizen_id)
            
            if "error" in academic_data:
                return {
                    "response": f"Xin lỗi, tôi không thể tìm thấy thông tin dữ liệu cho tài khoản của bạn. Vui lòng kiểm tra lại hoặc liên hệ hỗ trợ để được trợ giúp.",
                    "source": "database_not_found",
                    "processing_time": round(time.time() - start_time, 3),
                    "error": academic_data["error"]
                }
            
            # Format academic data for natural language response
            academic_context = f"""
Thông tin học tập của sinh viên (ID: {academic_data['student_id']}):

📊 THÀNH TÍCH HỌC TẬP:
• GPA tổng: {academic_data['academic_performance']['gpa']}/4.0
• GPA học kỳ hiện tại: {academic_data['academic_performance']['current_gpa']}/4.0
• Tổng tín chỉ đã hoàn thành: {academic_data['academic_performance']['total_credits_earned']}
• Số môn thi rớt: {academic_data['academic_performance']['failed_course_count']}

🏆 THÀNH TỰU & HỌC BỔNG:
• Số giải thưởng/thành tích: {academic_data['achievements']['achievement_award_count']}
• Có học bổng: {'Có' if academic_data['achievements']['has_scholarship'] else 'Không'}
• Số lượng học bổng: {academic_data['achievements']['scholarship_count']}

🎯 HOẠT ĐỘNG & LÃNH ĐẠO:
• Câu lạc bộ: {academic_data['activities']['club']}
• Số hoạt động ngoại khóa: {academic_data['activities']['extracurricular_activity_count']}
• Có vai trò lãnh đạo: {'Có' if academic_data['activities']['has_leadership_role'] else 'Không'}

📚 TÌNH TRẠNG HIỆN TẠI:
• Năm học: {academic_data['current_status']['study_year']}
• Học kỳ: {academic_data['current_status']['term']}
• Trạng thái xác thực: {'Đã xác thực' if academic_data['current_status']['verified'] else 'Chưa xác thực'}
"""

            # Generate natural language response based on question and data
            academic_prompt = f"""
Bạn là trợ lý AI của Student Credit, chuyên tư vấn về tín dụng sinh viên.
Người dùng hỏi: "{message}"

Lịch sử trò chuyện:
{conversation_history}

Dựa vào thông tin học tập sau của sinh viên:
{academic_context}

Hãy trả lời câu hỏi một cách tự nhiên, thân thiện và hữu ích:
- Trả lời trực tiếp câu hỏi được hỏi
- Sử dụng thông tin cụ thể từ hồ sơ học tập
- Tham khảo lịch sử trò chuyện để tránh lặp lại thông tin
- Có thể đưa ra nhận xét hoặc lời khuyên phù hợp
- Trả lời bằng tiếng Việt tự nhiên
- Ngắn gọn, 2-3 câu

Trả lời:
"""
            
            response = await self.llm.acomplete(academic_prompt)
            response_text = str(response).strip()
            
            return {
                "response": response_text,
                "source": "database_data",
                "processing_time": round(time.time() - start_time, 3),
                "data": academic_data,
                "citizen_id": citizen_id
            }
            
        except Exception as e:
            print(f"❌ Database data error: {e}")
            return {
                "response": "Xin lỗi, tôi gặp lỗi khi truy cập thông tin dữ liệu của bạn. Vui lòng thử lại sau hoặc liên hệ hỗ trợ.",
                "source": "database_error",
                "processing_time": round(time.time() - start_time, 3),
                "error": str(e)
            }

    async def _classify_question(self, message: str, citizen_id: Optional[str] = None, conversation_history: str = "") -> str:
        """Use LLM to classify question and decide response strategy with conversation context"""
        
        context_info = f"Người dùng {'có' if citizen_id else 'không có'} thông tin định danh (citizen_id)."
        
        classification_prompt = f"""
Bạn là một AI classifier cho hệ thống chatbot tư vấn vay vốn sinh viên.
Hãy phân loại câu hỏi sau và quyết định chiến lược trả lời tốt nhất.

Câu hỏi hiện tại: "{message}"
Thông tin ngữ cảnh: {context_info}

Lịch sử trò chuyện:
{conversation_history}

QUY TẮC PHÂN LOẠI QUAN TRỌNG (dựa trên context và lịch sử):
- Nếu câu hỏi CHỈ là chào hỏi thuần túy (không có từ khóa học tập) + user đã đăng nhập → call_data_db
- Nếu câu hỏi có từ khóa học tập (gpa, điểm, tín chỉ, etc.) → call_data_db
- Nếu câu hỏi chào hỏi + user chưa đăng nhập → direct_answer
- Nếu câu hỏi chung về vay vốn hoặc follow-up từ conversation trước → rag_search
- Nếu câu hỏi tiếp theo liên quan đến chủ đề đã thảo luận → giữ nguyên strategy từ context

PHÂN LOẠI:
1. "direct_answer" - Chào hỏi khi chưa đăng nhập, cảm ơn, câu hỏi chung không cần thông tin cá nhân
2. "call_data_db" - Chào hỏi khi đã đăng nhập hoặc câu hỏi về dữ liệu cá nhân (academic, profile, etc.)
3. "personal" - Câu hỏi về thông tin cá nhân khác không có trong database
4. "rag_search" - Câu hỏi cần thông tin từ tài liệu, quy định chung về vay vốn

VÍ DỤ CỤ THỂ:

DIRECT_ANSWER (chưa đăng nhập):
- "Xin chào" (không có citizen_id) → direct_answer
- "Cảm ơn bạn" → direct_answer
- "Bạn có thể giúp gì?" → direct_answer

CALL_DATA_DB (cần dữ liệu từ database):
- "Xin chào" (có citizen_id) → call_data_db (lấy tên để chào)
- "Hello" (có citizen_id) → call_data_db (lấy tên để chào)
- "GPA của tôi là bao nhiều?" → call_data_db
- "điểm số của tôi" → call_data_db
- "tín chỉ tôi đã học" → call_data_db
- "học bổng của tôi" → call_data_db
- "thành tích học tập" → call_data_db
- "câu lạc bộ tôi tham gia" → call_data_db

RAG_SEARCH (tài liệu chung):
- "Quy trình vay vốn như thế nào?" → rag_search
- "Lãi suất vay sinh viên" → rag_search
- "Điều kiện vay vốn" → rag_search
- "Giấy tờ cần thiết" → rag_search
- Follow-up questions về vay vốn → rag_search

PERSONAL (thông tin cá nhân khác):
- "Tôi có thể vay bao nhiều tiền?" → personal
- "Hồ sơ vay của tôi" → personal

CHỈ TRẢ LỜI MỘT TỪ: direct_answer, call_data_db, personal, hoặc rag_search
"""
        
        try:
            # Use a fast, lightweight call to classify
            try:
                from llama_index.llms.openai import OpenAI
            except ImportError:
                from llama_index_llms_openai import OpenAI
                
            classifier_llm = OpenAI(model="gpt-4.1-mini", temperature=0, max_tokens=50)
            
            response = await classifier_llm.acomplete(classification_prompt)
            result = str(response).strip().lower()
            
            if "direct_answer" in result:
                return "direct_answer"
            elif "call_data_db" in result:
                return "call_data_db"
            elif "personal" in result:
                return "personal"
            elif "rag_search" in result:
                return "rag_search"
            else:
                # If LLM response is unclear, ask it again with simpler prompt
                simple_prompt = f"""
Classify this question into one category: direct_answer, call_data_db, personal, or rag_search

Question: "{message}"
Context: User {'has' if citizen_id else 'does not have'} login info.

Rules:
- Greetings with login → call_data_db
- Academic questions → call_data_db  
- General questions → direct_answer
- Document questions → rag_search

Answer with one word only:"""
                
                fallback_response = await classifier_llm.acomplete(simple_prompt)
                fallback_result = str(fallback_response).strip().lower()
                
                if "call_data_db" in fallback_result:
                    return "call_data_db"
                elif "direct_answer" in fallback_result:
                    return "direct_answer"
                elif "personal" in fallback_result:
                    return "personal"
                else:
                    return "rag_search"
                
        except Exception as e:
            print(f"❌ Classification error: {e}")
            # Only use rule-based as absolute last resort when LLM fails
            database_keywords = ["gpa", "điểm", "tín chỉ", "học bổng", "thành tích", "câu lạc bộ", "hoạt động", "lãnh đạo", "năm học", "học kỳ"]
            
            if any(keyword in message.lower() for keyword in database_keywords):
                return "call_data_db"
            else:
                return "direct_answer"  # Safe fallback
    
    async def _handle_direct_response(self, message: str, start_time: float, conversation_history: str = "") -> Dict[str, Any]:
        """Handle direct LLM responses for general questions"""
        
        try:
            direct_prompt = f"""
Bạn là trợ lý AI chuyên về tín dụng sinh viên của Student Credit.
Hãy trả lời câu hỏi sau một cách tự nhiên, thân thiện và hữu ích.

Câu hỏi: {message}

Lịch sử trò chuyện:
{conversation_history}

Quy tắc trả lời:
- Trả lời bằng tiếng Việt tự nhiên, thân thiện
- Nếu là chào hỏi, hãy giới thiệu bản thân và dịch vụ
- Nếu là câu hỏi chung về vay vốn, đưa ra thông tin tổng quan hữu ích
- Tham khảo lịch sử trò chuyện để tránh lặp lại thông tin
- Không cần tìm kiếm tài liệu cụ thể, dựa vào kiến thức chung
- Khuyến khích người dùng hỏi thêm nếu cần thông tin chi tiết
- Trả lời ngắn gọn, súc tích (2-3 câu)

Trả lời:
"""
            
            # Use the main LLM for direct response
            response = await self.llm.acomplete(direct_prompt)
            response_text = str(response).strip()
            
            return {
                "response": response_text,
                "source": "direct_llm",
                "processing_time": round(time.time() - start_time, 3)
            }
            
        except Exception as e:
            print(f"❌ Direct response error: {e}")
            return {
                "response": "Xin chào! Tôi là trợ lý AI của Student Credit. Tôi có thể giúp bạn về các thông tin vay vốn sinh viên. Bạn có câu hỏi gì không?",
                "source": "fallback",
                "processing_time": round(time.time() - start_time, 3),
                "error": str(e)
            }
    
    async def _handle_rag_query(self, message: str, start_time: float, conversation_history: str = "") -> Dict[str, Any]:
        """Handle RAG document search queries"""
        
        if not self.query_engine:
            return {
                "response": "Hệ thống tìm kiếm tài liệu chưa sẵn sàng. Vui lòng thử lại sau.",
                "source": "error",
                "processing_time": time.time() - start_time
            }
        
        try:
            # Enhance query with conversation context
            enhanced_query = message
            if conversation_history and "Lịch sử trò chuyện gần đây:" in conversation_history:
                enhanced_query = f"{message} (Ngữ cảnh: {conversation_history[-200:]})"
            
            # Query the knowledge base
            response = self.query_engine.query(enhanced_query)
            
            # Extract source information
            sources = []
            if hasattr(response, 'source_nodes'):
                for node in response.source_nodes[:3]:  # Top 3 sources
                    sources.append({
                        "text_preview": node.text[:100] + "...",
                        "score": getattr(node, 'score', 0),
                        "metadata": node.metadata
                    })
            
            return {
                "response": str(response),
                "source": "knowledge_base",
                "sources": sources,
                "processing_time": time.time() - start_time,
                "query_stats": {
                    "retrieved_documents": len(sources),
                    "has_answer": len(str(response)) > 50,
                    "enhanced_with_context": len(conversation_history) > 0
                }
            }
            
        except Exception as e:
            return {
                "response": f"Không thể tìm kiếm trong tài liệu: {str(e)}",
                "source": "error",
                "processing_time": time.time() - start_time,
                "error": str(e)
            }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get RAG bot statistics with memory info"""
        
        try:
            pinecone_stats = self.pinecone_manager.get_index_stats()
            conversation_stats = self.get_conversation_summary()
            
            return {
                "status": "ready",
                "pinecone_stats": pinecone_stats,
                "conversation_memory": conversation_stats,
                "features": {
                    "document_search": True,
                    "function_calling": True,  # MCP server integration
                    "personal_context": True,  # Database integration with memory
                    "conversation_memory": True,
                    "smart_routing": True  # LLM-based classification with context
                },
                "model": "gpt-4.1-mini",
                "embedding_model": "text-embedding-3-large",
                "response_strategies": ["direct_answer", "call_data_db", "personal", "rag_search"],
                "memory_system": "ChatMemoryBuffer with conversation context"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

# Helper functions for API
def create_rag_bot() -> RAGBot:
    """Create RAG bot instance with environment variables"""
    
    load_dotenv()
    
    openai_key = os.getenv("OPENAI_API_KEY")
    pinecone_key = os.getenv("PINECONE_API_KEY")
    
    if not openai_key or not pinecone_key:
        raise Exception("Missing OPENAI_API_KEY or PINECONE_API_KEY in environment")
    
    return RAGBot(
        pinecone_api_key=pinecone_key,
        openai_api_key=openai_key
    )

# Global bot instance (singleton)
_bot_instance = None

def get_rag_bot() -> RAGBot:
    """Get or create global RAG bot instance"""
    global _bot_instance
    
    if _bot_instance is None:
        _bot_instance = create_rag_bot()
    
    return _bot_instance
