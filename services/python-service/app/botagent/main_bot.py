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
        index_name: str = "attacker2025",
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
            temperature=0.1,
            max_tokens=1000
        )
        
        # Load existing vector index
        if not self.pinecone_manager._load_existing_index():
            raise Exception("Failed to load existing vector index")
        
        # Create query engine
        self.query_engine = self._create_query_engine()
        
        # Chat memory
        self.memory = ChatMemoryBuffer.from_defaults(token_limit=2000)
        
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
            "Nếu không có thông tin thì nói không có thông tin trong tài liệu. "
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
    
    async def chat(self, message: str, conversation_id: Optional[str] = None) -> Dict[str, Any]:
        """Main chat method combining RAG and function calling"""
        
        start_time = time.time()
        
        try:
            # Check if question needs function calling (database queries)
            if self._needs_function_calling(message):
                return await self._handle_function_calling(message, conversation_id)
            
            # Use RAG for document-based questions
            else:
                return await self._handle_rag_query(message, conversation_id, start_time)
                
        except Exception as e:
            return {
                "response": f"Xin lỗi, tôi gặp lỗi khi xử lý câu hỏi: {str(e)}",
                "source": "error",
                "conversation_id": conversation_id,
                "processing_time": time.time() - start_time,
                "error": str(e)
            }
    
    def _needs_function_calling(self, message: str) -> bool:
        """Determine if message needs function calling vs RAG"""
        
        # Keywords that suggest database queries
        function_keywords = [
            "thống kê", "số liệu", "bao nhiêu", "danh sách", 
            "hồ sơ gần đây", "ứng viên", "tìm kiếm", "lọc",
            "so sánh", "báo cáo", "phân tích dữ liệu"
        ]
        
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in function_keywords)
    
    async def _handle_function_calling(self, message: str, conversation_id: Optional[str]) -> Dict[str, Any]:
        """Handle database function calling"""
        
        # TODO: Implement database function calling
        # For now, return a placeholder response
        
        return {
            "response": "Tính năng truy vấn cơ sở dữ liệu đang được phát triển. Vui lòng hỏi về nội dung tài liệu thay vì dữ liệu thống kê.",
            "source": "function_calling",
            "conversation_id": conversation_id,
            "functions_used": [],
            "processing_time": 0.1
        }
    
    async def _handle_rag_query(self, message: str, conversation_id: Optional[str], start_time: float) -> Dict[str, Any]:
        """Handle RAG document search queries"""
        
        if not self.query_engine:
            return {
                "response": "Hệ thống tìm kiếm tài liệu chưa sẵn sàng. Vui lòng thử lại sau.",
                "source": "error",
                "conversation_id": conversation_id,
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
                "conversation_id": conversation_id,
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
                "conversation_id": conversation_id,
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
                    "function_calling": False,  # TODO: Implement
                    "conversation_memory": True
                },
                "model": "gpt-4.1-mini",
                "embedding_model": "text-embedding-3-small"
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
