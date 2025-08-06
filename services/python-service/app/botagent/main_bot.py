"""
RAG Chatbot with Function Calling
Combines document search (RAG) with database function calling
"""
import os
import time
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# Import existing components
from app.botagent.vectordb import PineconeManager

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
        """Initialize RAG bot with Pinecone and OpenAI"""
        
        # Set environment variables
        os.environ["OPENAI_API_KEY"] = openai_api_key
        
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
        """Smart chat method using LLM to decide response strategy"""
        
        start_time = time.time()
        
        try:
            # Use LLM to classify the question and decide response strategy
            response_strategy = await self._classify_question(message, citizen_id)
            
            if response_strategy == "direct_answer":
                # LLM can answer directly without needing documents or personal data
                return await self._handle_direct_response(message, start_time)
            elif response_strategy == "personal":
                # Personal questions - provide general guidance since no personal data available
                return await self._handle_personal_guidance(message, start_time)
            elif response_strategy == "rag_search":
                # Need to search documents for specific information
                return await self._handle_rag_query(message, start_time)
            else:
                # Default to RAG if unsure
                return await self._handle_rag_query(message, start_time)
                
        except Exception as e:
            return {
                "response": f"Xin lỗi, tôi gặp lỗi khi xử lý câu hỏi: {str(e)}",
                "source": "error",
                "processing_time": time.time() - start_time,
                "error": str(e)
            }
    
    async def _handle_personal_guidance(self, message: str, start_time: float) -> Dict[str, Any]:
        """Handle personal questions by providing general guidance"""
        
        try:
            personal_prompt = f"""
Bạn là trợ lý AI chuyên về tín dụng sinh viên của Student Credit.
Người dùng hỏi một câu hỏi cá nhân: "{message}"

Hãy trả lời một cách hữu ích và hướng dẫn người dùng:
- Đưa ra thông tin tổng quan hữu ích về chủ đề họ hỏi
- Giải thích các yếu tố chung ảnh hưởng đến vấn đề này
- Hướng dẫn cách tự đánh giá hoặc chuẩn bị
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
    
    async def _classify_question(self, message: str, citizen_id: Optional[str] = None) -> str:
        """Use LLM to classify question and decide response strategy"""
        
        context_info = f"Người dùng {'có' if citizen_id else 'không có'} thông tin định danh (citizen_id)."
        
        classification_prompt = f"""
Bạn là một AI classifier cho hệ thống chatbot tư vấn vay vốn sinh viên.
Hãy phân loại câu hỏi sau và quyết định chiến lược trả lời tốt nhất.

Câu hỏi: "{message}"
Thông tin ngữ cảnh: {context_info}

Các loại câu hỏi và chiến lược:
1. "direct_answer" - Câu hỏi chào hỏi, cảm ơn, hoặc câu hỏi chung không cần thông tin cá nhân
2. "personal" - Câu hỏi về thông tin cá nhân của người dùng
3. "rag_search" - Câu hỏi cần thông tin từ tài liệu, quy định chung về vay vốn

Ví dụ phân loại:

DIRECT_ANSWER:
- "Xin chào" → direct_answer
- "Cảm ơn bạn" → direct_answer  
- "Vay vốn sinh viên là gì?" → direct_answer
- "Bạn có thể giúp gì?" → direct_answer

PERSONAL:
- "Tôi có thể vay bao nhiều tiền?" → personal
- "Hồ sơ của tôi như thế nào?" → personal
- "Tình trạng đơn vay của tôi?" → personal
- "Điểm GPA của tôi có đủ không?" → personal
- "Lịch sử vay của tôi ra sao?" → personal
- "Thông tin sinh viên của tôi" → personal

RAG_SEARCH (thông tin chung từ tài liệu):
- "Quy trình vay vốn như thế nào?" → rag_search
- "Lãi suất vay sinh viên hiện tại?" → rag_search
- "Điều kiện vay vốn là gì?" → rag_search
- "Thời hạn vay tối đa bao lâu?" → rag_search
- "Giấy tờ cần thiết để vay?" → rag_search
- "System ứng dụng những công nghệ gì?" → rag_search
Chỉ trả lời một từ: direct_answer, personal, hoặc rag_search
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
            elif "personal" in result:
                return "personal"
            elif "rag_search" in result:
                return "rag_search"
            else:
                # Smart fallback logic
                personal_keywords = ["tôi", "của tôi", "hồ sơ", "đơn vay", "gpa", "lịch sử"]
                if any(keyword in message.lower() for keyword in personal_keywords):
                    return "personal"
                else:
                    return "rag_search"  # Default to RAG for general info
                
        except Exception as e:
            print(f"❌ Classification error: {e}")
            # Fallback classification based on keywords
            personal_keywords = ["tôi", "của tôi", "hồ sơ", "đơn vay", "thông tin cá nhân"]
            greeting_keywords = ["xin chào", "hello", "chào", "cảm ơn", "thank"]
            
            message_lower = message.lower()
            
            if any(keyword in message_lower for keyword in greeting_keywords):
                return "direct_answer"
            elif any(keyword in message_lower for keyword in personal_keywords):
                return "personal"
            else:
                return "rag_search"
    
    async def _handle_direct_response(self, message: str, start_time: float) -> Dict[str, Any]:
        """Handle direct LLM responses for general questions"""
        
        try:
            direct_prompt = f"""
Bạn là trợ lý AI chuyên về tín dụng sinh viên của Student Credit.
Hãy trả lời câu hỏi sau một cách tự nhiên, thân thiện và hữu ích.

Câu hỏi: {message}

Quy tắc trả lời:
- Trả lời bằng tiếng Việt tự nhiên, thân thiện
- Nếu là chào hỏi, hãy giới thiệu bản thân và dịch vụ
- Nếu là câu hỏi chung về vay vốn, đưa ra thông tin tổng quan hữu ích
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
    
    async def _handle_rag_query(self, message: str, start_time: float) -> Dict[str, Any]:
        """Handle RAG document search queries"""
        
        if not self.query_engine:
            return {
                "response": "Hệ thống tìm kiếm tài liệu chưa sẵn sàng. Vui lòng thử lại sau.",
                "source": "error",
                "processing_time": time.time() - start_time
            }
        
        try:
            # Query the knowledge base
            response = self.query_engine.query(message)
            
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
                    "has_answer": len(str(response)) > 50
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
        """Get RAG bot statistics"""
        
        try:
            pinecone_stats = self.pinecone_manager.get_index_stats()
            
            return {
                "status": "ready",
                "pinecone_stats": pinecone_stats,
                "features": {
                    "document_search": True,
                    "function_calling": False,  # No function calling
                    "personal_context": False,  # No personal data from database
                    "conversation_memory": True,
                    "smart_routing": True  # Auto-route to RAG/Direct based on question
                },
                "model": "gpt-4.1-mini",
                "embedding_model": "text-embedding-3-large",
                "response_strategies": ["direct_answer", "personal_general", "rag_search"]
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
