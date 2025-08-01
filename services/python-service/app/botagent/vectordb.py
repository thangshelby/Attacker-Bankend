"""
Simple Pinecone Vector Database Manager for RAG Bot
Handle document storage, retrieval, and management
"""
import os
import time
from typing import List, Dict, Any, Optional
from pinecone import Pinecone, ServerlessSpec
from llama_index.core import Document, VectorStoreIndex, Settings
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core.storage.storage_context import StorageContext

class PineconeManager:
    """Simple Pinecone vector database manager"""
    
    def __init__(
        self, 
        api_key: str, 
        index_name: str = "rag-knowledge-base",
        dimension: int = 1536,  # OpenAI ada-002 embedding size
        environment: str = "us-east-1-aws"
    ):
        self.api_key = api_key
        self.index_name = index_name
        self.dimension = dimension
        self.environment = environment
        
        # Initialize Pinecone
        self.pc = Pinecone(api_key=api_key)
        self.index = None
        self.vector_store = None
        self.vector_index = None
        
        # Setup embedding model
        Settings.embed_model = OpenAIEmbedding(
            model="text-embedding-ada-002",
            api_key=os.getenv("OPENAI_API_KEY")
        )
    
    def create_index(self) -> bool:
        """Create Pinecone index if not exists"""
        try:
            existing_indexes = [idx.name for idx in self.pc.list_indexes()]
            
            if self.index_name not in existing_indexes:
                print(f"🔨 Creating Pinecone index: {self.index_name}")
                
                self.pc.create_index(
                    name=self.index_name,
                    dimension=self.dimension,
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud="aws",
                        region=self.environment
                    )
                )
                
                # Wait for index to be ready
                print("⏳ Waiting for index to be ready...")
                time.sleep(10)
                
            else:
                print(f"✅ Index {self.index_name} already exists")
            
            # Connect to index
            self.index = self.pc.Index(self.index_name)
            
            # Setup vector store
            self.vector_store = PineconeVectorStore(pinecone_index=self.index)
            
            return True
            
        except Exception as e:
            print(f"❌ Error creating index: {e}")
            return False
    
    def get_index_stats(self) -> Dict[str, Any]:
        """Get index statistics"""
        try:
            if not self.index:
                return {"error": "Index not initialized"}
            
            stats = self.index.describe_index_stats()
            return {
                "total_vectors": stats.get('total_vector_count', 0),
                "dimension": stats.get('dimension', 0),
                "index_fullness": stats.get('index_fullness', 0),
                "namespaces": list(stats.get('namespaces', {}).keys())
            }
        except Exception as e:
            return {"error": str(e)}
    
    def add_documents(self, documents: List[Document], namespace: str = "default") -> bool:
        """Add documents to vector database"""
        try:
            if not self.vector_store:
                print("❌ Vector store not initialized")
                return False
            
            print(f"📤 Adding {len(documents)} documents to Pinecone...")
            
            # Create storage context
            storage_context = StorageContext.from_defaults(vector_store=self.vector_store)
            
            # Create vector index and add documents
            self.vector_index = VectorStoreIndex.from_documents(
                documents,
                storage_context=storage_context
            )
            
            print(f"✅ Successfully added {len(documents)} documents")
            return True
            
        except Exception as e:
            print(f"❌ Error adding documents: {e}")
            return False
    
    def search_documents(
        self, 
        query: str, 
        top_k: int = 5,
        namespace: str = "default"
    ) -> List[Dict[str, Any]]:
        """Search similar documents"""
        try:
            if not self.vector_index:
                # Try to load existing index
                if not self._load_existing_index():
                    return []
            
            # Create query engine
            query_engine = self.vector_index.as_query_engine(
                similarity_top_k=top_k,
                response_mode="no_text"  # Only return source nodes
            )
            
            # Execute query
            response = query_engine.query(query)
            
            # Extract results
            results = []
            for node in response.source_nodes:
                results.append({
                    "text": node.text,
                    "score": node.score,
                    "metadata": node.metadata
                })
            
            print(f"🔍 Found {len(results)} similar documents for: {query[:50]}...")
            return results
            
        except Exception as e:
            print(f"❌ Error searching documents: {e}")
            return []
    
    def delete_documents(self, doc_ids: List[str], namespace: str = "default") -> bool:
        """Delete documents by IDs"""
        try:
            if not self.index:
                return False
            
            self.index.delete(ids=doc_ids, namespace=namespace)
            print(f"🗑️ Deleted {len(doc_ids)} documents")
            return True
            
        except Exception as e:
            print(f"❌ Error deleting documents: {e}")
            return False
    
    def clear_index(self, namespace: str = "default") -> bool:
        """Clear all vectors from index"""
        try:
            if not self.index:
                return False
            
            self.index.delete(delete_all=True, namespace=namespace)
            print(f"🧹 Cleared all documents from namespace: {namespace}")
            return True
            
        except Exception as e:
            print(f"❌ Error clearing index: {e}")
            return False
    
    def _load_existing_index(self) -> bool:
        """Load existing vector index"""
        try:
            if not self.vector_store:
                self.index = self.pc.Index(self.index_name)
                self.vector_store = PineconeVectorStore(pinecone_index=self.index)
            
            # Create vector index from existing store
            self.vector_index = VectorStoreIndex.from_vector_store(self.vector_store)
            return True
            
        except Exception as e:
            print(f"❌ Error loading existing index: {e}")
            return False

# Simple usage functions
def setup_pinecone_simple(api_key: str, index_name: str = "rag-kb") -> PineconeManager:
    """Simple Pinecone setup"""
    manager = PineconeManager(api_key=api_key, index_name=index_name)
    
    if manager.create_index():
        print("✅ Pinecone setup completed")
        return manager
    else:
        print("❌ Pinecone setup failed")
        return None

def add_docs_to_pinecone(manager: PineconeManager, documents: List[Document]) -> bool:
    """Simple wrapper to add documents"""
    return manager.add_documents(documents)

def search_pinecone(manager: PineconeManager, query: str, top_k: int = 5) -> List[Dict]:
    """Simple wrapper to search"""
    return manager.search_documents(query, top_k)
