"""
Simple Text Chunking for RAG Bot
Split documents into optimal chunks for embedding
"""
import re
from typing import List, Dict, Any
from llama_index.core import Document
from llama_index.core.node_parser import SimpleNodeParser, SentenceSplitter

class DocumentChunker:
    """Split documents into chunks for better RAG performance"""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # Initialize LlamaIndex splitter
        self.splitter = SentenceSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            paragraph_separator="\n\n",
            secondary_chunking_regex="[^,.;。]+[,.;。]?"
        )
    
    def chunk_documents(self, documents: List[Document]) -> List[Document]:
        """Main method to chunk all documents"""
        all_chunks = []
        
        for doc in documents:
            chunks = self._chunk_single_document(doc)
            all_chunks.extend(chunks)
        
        print(f"📝 Split {len(documents)} documents into {len(all_chunks)} chunks")
        return all_chunks
    
    def _chunk_single_document(self, document: Document) -> List[Document]:
        """Chunk a single document"""
        chunks = []
        
        try:
            # Use LlamaIndex splitter
            nodes = self.splitter.get_nodes_from_documents([document])
            
            for i, node in enumerate(nodes):
                # Create new document for each chunk
                chunk_doc = Document(
                    text=node.text,
                    metadata={
                        **document.metadata,  # Keep original metadata
                        "chunk_id": i,
                        "total_chunks": len(nodes),
                        "chunk_size": len(node.text)
                    }
                )
                chunks.append(chunk_doc)
        
        except Exception as e:
            print(f"❌ Error chunking document: {e}")
            # Fallback: return original document
            chunks = [document]
        
        return chunks
    
    def smart_chunk_by_content_type(self, document: Document) -> List[Document]:
        """Content-aware chunking based on document type"""
        doc_type = document.metadata.get("type", "text")
        
        if doc_type == "pdf":
            return self._chunk_pdf_document(document)
        elif doc_type == "web":
            return self._chunk_web_document(document)
        else:
            return self._chunk_single_document(document)
    
    def _chunk_pdf_document(self, document: Document) -> List[Document]:
        """Special chunking for PDF documents"""
        text = document.text
        chunks = []
        
        # Split by pages first if page markers exist
        if "--- Page" in text:
            pages = re.split(r'\n--- Page \d+ ---\n', text)
            
            for i, page_content in enumerate(pages):
                if page_content.strip():
                    # Further split large pages
                    page_chunks = self._split_text_smart(page_content)
                    
                    for j, chunk in enumerate(page_chunks):
                        chunk_doc = Document(
                            text=chunk,
                            metadata={
                                **document.metadata,
                                "page_number": i,
                                "chunk_id": f"{i}_{j}",
                                "chunk_type": "pdf_page"
                            }
                        )
                        chunks.append(chunk_doc)
        else:
            # No page markers, use regular chunking
            chunks = self._chunk_single_document(document)
        
        return chunks
    
    def _chunk_web_document(self, document: Document) -> List[Document]:
        """Special chunking for web documents"""
        text = document.text
        
        # Try to split by sections/headings
        sections = re.split(r'\n(?=[A-Z][^a-z]*(?:\n|$))', text)
        
        chunks = []
        for i, section in enumerate(sections):
            if len(section.strip()) > 50:  # Skip very short sections
                # Split large sections further
                section_chunks = self._split_text_smart(section)
                
                for j, chunk in enumerate(section_chunks):
                    chunk_doc = Document(
                        text=chunk,
                        metadata={
                            **document.metadata,
                            "section_id": i,
                            "chunk_id": f"web_{i}_{j}",
                            "chunk_type": "web_section"
                        }
                    )
                    chunks.append(chunk_doc)
        
        return chunks if chunks else self._chunk_single_document(document)
    
    def _split_text_smart(self, text: str) -> List[str]:
        """Smart text splitting with sentence awareness"""
        if len(text) <= self.chunk_size:
            return [text]
        
        # Split by sentences first
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            # If adding this sentence would exceed chunk size
            if len(current_chunk) + len(sentence) > self.chunk_size:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                    # Start new chunk with overlap
                    current_chunk = self._get_overlap_text(current_chunk) + sentence
                else:
                    # Single sentence too long, split it
                    chunks.append(sentence[:self.chunk_size])
                    current_chunk = sentence[self.chunk_size:]
            else:
                current_chunk += (" " if current_chunk else "") + sentence
        
        # Add final chunk
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def _get_overlap_text(self, text: str) -> str:
        """Get overlap text from end of current chunk"""
        if len(text) <= self.chunk_overlap:
            return text
        
        # Get last chunk_overlap characters, but try to end at sentence boundary
        overlap_text = text[-self.chunk_overlap:]
        
        # Find last sentence boundary
        last_sentence = re.search(r'[.!?]\s+', overlap_text[::-1])
        if last_sentence:
            # Cut at sentence boundary
            cut_point = len(overlap_text) - last_sentence.start()
            overlap_text = overlap_text[cut_point:]
        
        return overlap_text + " "

# Simple usage
def chunk_documents_simple(documents: List[Document], chunk_size: int = 1000) -> List[Document]:
    """Simple wrapper for chunking"""
    chunker = DocumentChunker(chunk_size=chunk_size)
    return chunker.chunk_documents(documents)
