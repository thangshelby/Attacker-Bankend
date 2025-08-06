"""
Section-based Text Chunking for RAG Bot
Split documents into chunks based on logical sections (PHẦN X:)
"""
import re
from typing import List, Dict, Any
from llama_index.core import Document

class DocumentChunker:
    """Split documents into chunks based on sections for better RAG performance"""
    
    def __init__(self, max_section_length: int = 3000, fallback_chunk_size: int = 1000):
        """
        Initialize chunker with section-based approach
        
        Args:
            max_section_length: Maximum length for a single section before splitting
            fallback_chunk_size: Fallback chunk size for non-sectioned content
        """
        self.max_section_length = max_section_length
        self.fallback_chunk_size = fallback_chunk_size
    
    def chunk_documents(self, documents: List[Document]) -> List[Document]:
        """Main method to chunk all documents based on sections"""
        all_chunks = []
        
        for doc in documents:
            chunks = self.chunk_by_sections(doc)
            all_chunks.extend(chunks)
        
        print(f"📝 Split {len(documents)} documents into {len(all_chunks)} section-based chunks")
        return all_chunks
    
    def chunk_by_sections(self, document: Document) -> List[Document]:
        """
        Chunk document by sections (PHẦN X:, SECTION, CHAPTER, etc.)
        """
        text = document.text.strip()
        chunks = []
        
        # Try different section patterns
        sections = self._extract_sections(text)
        
        if len(sections) > 1:
            print(f"🔍 Found {len(sections)} sections in document")
            
            for i, section in enumerate(sections):
                section_title = section.get('title', f'Section {i+1}')
                section_content = section.get('content', '')
                
                # If section is too long, split it further
                if len(section_content) > self.max_section_length:
                    subsections = self._split_long_section(section_content)
                    
                    for j, subsection in enumerate(subsections):
                        chunk_doc = Document(
                            text=subsection,
                            metadata={
                                **document.metadata,
                                "section_title": section_title,
                                "section_number": i + 1,
                                "subsection_number": j + 1,
                                "chunk_id": f"section_{i+1}_{j+1}",
                                "chunk_type": "section_based",
                                "is_subsection": True
                            }
                        )
                        chunks.append(chunk_doc)
                else:
                    # Section fits in one chunk
                    chunk_doc = Document(
                        text=section_content,
                        metadata={
                            **document.metadata,
                            "section_title": section_title,
                            "section_number": i + 1,
                            "chunk_id": f"section_{i+1}",
                            "chunk_type": "section_based",
                            "is_subsection": False
                        }
                    )
                    chunks.append(chunk_doc)
        else:
            print(f"⚠️ No clear sections found, using fallback chunking")
            chunks = self._fallback_chunking(document)
        
        return chunks
    
    def _extract_sections(self, text: str) -> List[Dict[str, str]]:
        """
        Extract sections from text using various patterns
        """
        sections = []
        
        # Pattern 1: PHẦN X: (Vietnamese sections)
        section_pattern = r'(?:^|\n\n)(PHẦN\s+\d+[:\.].*?)(?=\n\n(?:PHẦN\s+\d+[:\.]|\Z))'
        matches = re.findall(section_pattern, text, re.MULTILINE | re.DOTALL)
        
        if matches:
            for match in matches:
                lines = match.strip().split('\n', 1)
                title = lines[0].strip()
                content = lines[1].strip() if len(lines) > 1 else ""
                
                if content:  # Only add if there's actual content
                    sections.append({
                        'title': title,
                        'content': f"{title}\n{content}"
                    })
        
        # Pattern 2: CHAPTER/SECTION (English)
        if not sections:
            chapter_pattern = r'(?:^|\n\n)((?:CHAPTER|SECTION)\s+\d+.*?)(?=\n\n(?:CHAPTER|SECTION)\s+\d+|\Z)'
            matches = re.findall(chapter_pattern, text, re.MULTILINE | re.DOTALL | re.IGNORECASE)
            
            for match in matches:
                lines = match.strip().split('\n', 1)
                title = lines[0].strip()
                content = lines[1].strip() if len(lines) > 1 else ""
                
                if content:
                    sections.append({
                        'title': title,
                        'content': f"{title}\n{content}"
                    })
        
        # Pattern 3: Numbered headings (1. 2. 3.)
        if not sections:
            numbered_pattern = r'(?:^|\n\n)(\d+\.\s+.*?)(?=\n\n\d+\.\s+|\Z)'
            matches = re.findall(numbered_pattern, text, re.MULTILINE | re.DOTALL)
            
            for match in matches:
                lines = match.strip().split('\n', 1)
                title = lines[0].strip()
                content = lines[1].strip() if len(lines) > 1 else ""
                
                if content:
                    sections.append({
                        'title': title,
                        'content': f"{title}\n{content}"
                    })
        
        # Pattern 4: Double line breaks as simple section separator
        if not sections:
            simple_sections = [s.strip() for s in text.split('\n\n') if s.strip()]
            
            # Only use this if we have reasonable sections (not too many small ones)
            if len(simple_sections) <= 20 and all(len(s) > 100 for s in simple_sections):
                for i, section in enumerate(simple_sections):
                    # Try to extract title from first line
                    lines = section.split('\n', 1)
                    if len(lines) > 1 and len(lines[0]) < 100:
                        title = lines[0].strip()
                        content = section
                    else:
                        title = f"Section {i+1}"
                        content = section
                    
                    sections.append({
                        'title': title,
                        'content': content
                    })
        
        return sections
    
    def _split_long_section(self, content: str) -> List[str]:
        """
        Split a long section into smaller chunks while preserving meaning
        """
        chunks = []
        
        # Try to split by paragraphs first
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        
        current_chunk = ""
        
        for paragraph in paragraphs:
            # If adding this paragraph would exceed max length
            if len(current_chunk) + len(paragraph) + 2 > self.max_section_length:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                    current_chunk = paragraph
                else:
                    # Single paragraph too long, split by sentences
                    sentence_chunks = self._split_by_sentences(paragraph)
                    chunks.extend(sentence_chunks)
            else:
                if current_chunk:
                    current_chunk += "\n\n" + paragraph
                else:
                    current_chunk = paragraph
        
        # Add final chunk
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def _split_by_sentences(self, text: str) -> List[str]:
        """
        Split text by sentences when paragraph is too long
        """
        # Split by Vietnamese and English sentence endings
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) > self.max_section_length:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                    current_chunk = sentence
                else:
                    # Single sentence too long, just split it
                    chunks.append(sentence[:self.max_section_length])
                    current_chunk = sentence[self.max_section_length:]
            else:
                current_chunk += (" " if current_chunk else "") + sentence
        
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def _fallback_chunking(self, document: Document) -> List[Document]:
        """
        Fallback to simple chunking when no sections are detected
        """
        text = document.text
        chunks = []
        
        # Simple chunking by character count
        start = 0
        chunk_id = 0
        
        while start < len(text):
            end = start + self.fallback_chunk_size
            
            # Try to end at sentence boundary
            if end < len(text):
                # Look for sentence ending within next 200 chars
                sentence_end = text.rfind('.', end, end + 200)
                if sentence_end == -1:
                    sentence_end = text.rfind('!', end, end + 200)
                if sentence_end == -1:
                    sentence_end = text.rfind('?', end, end + 200)
                
                if sentence_end != -1:
                    end = sentence_end + 1
            
            chunk_text = text[start:end].strip()
            
            if chunk_text:
                chunk_doc = Document(
                    text=chunk_text,
                    metadata={
                        **document.metadata,
                        "chunk_id": f"fallback_{chunk_id}",
                        "chunk_type": "fallback",
                        "start_pos": start,
                        "end_pos": end
                    }
                )
                chunks.append(chunk_doc)
                chunk_id += 1
            
            start = end
        
        return chunks

# Simple usage functions
def chunk_documents_by_sections(documents: List[Document], max_section_length: int = 3000) -> List[Document]:
    """Simple wrapper for section-based chunking"""
    chunker = DocumentChunker(max_section_length=max_section_length)
    return chunker.chunk_documents(documents)

def analyze_document_structure(document: Document) -> Dict[str, Any]:
    """Analyze document structure to see how it would be chunked"""
    chunker = DocumentChunker()
    sections = chunker._extract_sections(document.text)
    
    return {
        "total_length": len(document.text),
        "sections_found": len(sections),
        "sections": [
            {
                "title": s["title"],
                "length": len(s["content"]),
                "preview": s["content"][:100] + "..." if len(s["content"]) > 100 else s["content"]
            }
            for s in sections
        ]
    }
