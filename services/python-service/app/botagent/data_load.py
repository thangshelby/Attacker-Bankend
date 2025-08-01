"""
Simple Document Loader for RAG Bot
Supports: PDF, TXT, MD, Web pages
"""
import os
import aiofiles
from pathlib import Path
from typing import List, Dict, Any
import requests
from bs4 import BeautifulSoup
import PyPDF2
from llama_index.core import Document

# For .doc/.docx files
try:
    import docx2txt  # pip install docx2txt
    import win32com.client  # for .doc files on Windows
    DOC_SUPPORT = True
except ImportError:
    DOC_SUPPORT = False
    print("⚠️  Install docx2txt for .doc/.docx support: pip install docx2txt")

class DocumentLoader:
    """Load documents from various sources"""
    
    def __init__(self):
        self.supported_formats = ['.pdf', '.md', '.txt', '.html', '.doc', '.docx']
    
    async def load_text_file(self, file_path: str) -> List[Document]:
        """Load plain text or markdown files"""
        documents = []
        try:
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as file:
                content = await file.read()
                
                documents.append(Document(
                    text=content,
                    metadata={
                        "source": file_path,
                        "type": Path(file_path).suffix[1:],
                        "filename": Path(file_path).name
                    }
                ))
                
        except Exception as e:
            print(f"❌ Error loading text file {file_path}: {e}")
        
        return documents
    
    def load_pdf(self, file_path: str) -> List[Document]:
        """Load PDF documents"""
        documents = []
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                # Extract all text
                full_text = ""
                for page_num, page in enumerate(pdf_reader.pages):
                    page_text = page.extract_text()
                    full_text += f"\n--- Page {page_num + 1} ---\n{page_text}\n"
                
                documents.append(Document(
                    text=full_text,
                    metadata={
                        "source": file_path,
                        "type": "pdf",
                        "filename": Path(file_path).name,
                        "pages": len(pdf_reader.pages)
                    }
                ))
                
        except Exception as e:
            print(f"❌ Error loading PDF {file_path}: {e}")
        
        return documents
    
    def load_doc_file(self, file_path: str) -> List[Document]:
        """Load .doc/.docx files"""
        documents = []
        if not DOC_SUPPORT:
            print("❌ docx2txt not installed. Cannot load .doc/.docx files")
            return documents
        
        try:
            file_path = Path(file_path)
            
            if file_path.suffix.lower() == '.docx':
                # Load .docx file
                text = docx2txt.process(str(file_path))
            elif file_path.suffix.lower() == '.doc':
                # Load .doc file (requires Windows + Office)
                try:
                    word = win32com.client.Dispatch("Word.Application")
                    word.Visible = False
                    doc = word.Documents.Open(str(file_path.absolute()))
                    text = doc.Content.Text
                    doc.Close()
                    word.Quit()
                except Exception as e:
                    print(f"❌ Error loading .doc file (needs MS Word): {e}")
                    return documents
            else:
                return documents
            
            if text.strip():
                documents.append(Document(
                    text=text,
                    metadata={
                        "source": str(file_path),
                        "type": file_path.suffix[1:],
                        "filename": file_path.name,
                        "word_count": len(text.split())
                    }
                ))
                print(f"✅ Loaded {file_path.name} ({len(text)} characters)")
            
        except Exception as e:
            print(f"❌ Error loading doc file {file_path}: {e}")
        
        return documents
    
    def load_web_page(self, url: str) -> List[Document]:
        """Scrape web page content"""
        documents = []
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove unwanted elements
            for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
                tag.decompose()
            
            # Extract title and content
            title = soup.title.string if soup.title else "Untitled"
            content = soup.get_text()
            
            # Clean up text
            lines = [line.strip() for line in content.splitlines() if line.strip()]
            clean_content = '\n'.join(lines)
            
            documents.append(Document(
                text=clean_content,
                metadata={
                    "source": url,
                    "type": "web",
                    "title": title,
                    "url": url
                }
            ))
            
        except Exception as e:
            print(f"❌ Error loading web page {url}: {e}")
        
        return documents
    
    async def load_directory(self, directory_path: str) -> List[Document]:
        """Load all supported documents from directory"""
        all_documents = []
        directory = Path(directory_path)
        
        if not directory.exists():
            print(f"❌ Directory not found: {directory_path}")
            return all_documents
        
        print(f"📁 Loading documents from: {directory_path}")
        
        for file_path in directory.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in self.supported_formats:
                print(f"📄 Processing: {file_path.name}")
                
                if file_path.suffix.lower() == '.pdf':
                    docs = self.load_pdf(str(file_path))
                elif file_path.suffix.lower() in ['.doc', '.docx']:
                    docs = self.load_doc_file(str(file_path))
                else:  # .txt, .md, .html
                    docs = await self.load_text_file(str(file_path))
                
                all_documents.extend(docs)
        
        print(f"✅ Loaded {len(all_documents)} documents from {directory_path}")
        return all_documents

# Simple usage for single file
async def load_single_document(file_path: str) -> List[Document]:
    """Load a single document file - perfect for your case!"""
    loader = DocumentLoader()
    
    file_path = Path(file_path)
    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        return []
    
    print(f"📄 Loading single file: {file_path.name}")
    
    # Determine file type and load accordingly
    if file_path.suffix.lower() == '.pdf':
        docs = loader.load_pdf(str(file_path))
    elif file_path.suffix.lower() in ['.doc', '.docx']:
        docs = loader.load_doc_file(str(file_path))
    else:  # .txt, .md, .html
        docs = await loader.load_text_file(str(file_path))
    
    print(f"✅ Loaded 1 file → {len(docs)} document(s)")
    return docs

# Usage example for directory (if you add more files later)
async def load_sample_docs():
    """Example usage for multiple documents"""
    loader = DocumentLoader()
    
    # Load from directory
    docs = await loader.load_directory("./knowledge_base")
    
    return docs
