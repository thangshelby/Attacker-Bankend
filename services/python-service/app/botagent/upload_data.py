"""
Cross-Platform Document Upload to Pinecone
Supports: TXT, PDF, DOCX, MD (Windows/Linux/Mac compatible)
Run: python -m app.botagent.upload_data

Make sure you have .env file with:
OPENAI_API_KEY=sk-proj-...
PINECONE_API_KEY=pc-...
"""
import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from llama_index.core import Document

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

# ✅ REUSE existing components + cross-platform loader
from app.botagent.chunking import chunk_documents_by_sections
from app.botagent.vectordb import PineconeManager

# Cross-platform imports (optional)
try:
    import PyPDF2
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False

try:
    import docx2txt
    DOCX_SUPPORT = True
except ImportError:
    DOCX_SUPPORT = False

def load_cross_platform_document(file_path: str):
    """Cross-platform document loader - works on Windows/Linux/Mac"""
    file_path = Path(file_path)
    
    if not file_path.exists():
        return None
    
    print(f"📄 Loading: {file_path.name}")
    
    try:
        file_type = file_path.suffix.lower()
        
        # 1. TXT and MD files (universal)
        if file_type in ['.txt', '.md']:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                return Document(
                    text=content,
                    metadata={
                        "source": str(file_path),
                        "type": file_type[1:],
                        "filename": file_path.name,
                        "size": len(content)
                    }
                )
        
        # 2. PDF files (cross-platform)
        elif file_type == '.pdf' and PDF_SUPPORT:
            with open(file_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                text = ""
                for i, page in enumerate(pdf_reader.pages):
                    text += f"\n--- Page {i+1} ---\n"
                    text += page.extract_text()
                
                return Document(
                    text=text,
                    metadata={
                        "source": str(file_path),
                        "type": "pdf",
                        "filename": file_path.name,
                        "pages": len(pdf_reader.pages)
                    }
                )
        
        # 3. DOCX files (cross-platform, no pywin32 needed)
        elif file_type == '.docx' and DOCX_SUPPORT:
            text = docx2txt.process(str(file_path))
            return Document(
                text=text,
                metadata={
                    "source": str(file_path),
                    "type": "docx",
                    "filename": file_path.name,
                    "word_count": len(text.split())
                }
            )
        
        # 4. Unsupported or missing dependencies
        else:
            missing_deps = []
            if file_type == '.pdf' and not PDF_SUPPORT:
                missing_deps.append("PyPDF2")
            elif file_type == '.docx' and not DOCX_SUPPORT:
                missing_deps.append("docx2txt")
            
            if missing_deps:
                print(f"❌ Missing dependency for {file_type}: pip install {' '.join(missing_deps)}")
            else:
                print(f"❌ Unsupported file type: {file_type}")
                print("   Supported: .txt (best), .pdf, .docx, .md")
            return None
            
    except Exception as e:
        print(f"❌ Error loading {file_path}: {e}")
        return None

async def upload_to_pinecone():
    """Upload documents using existing components"""
    
    print("🚀 RAG Document Upload Tool")
    print("Using existing components + environment variables")
    print("=" * 50)
    
    # ✅ Load from .env file
    load_dotenv()
    
    # Get API keys from environment
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
    
    # Validate keys
    if not OPENAI_API_KEY:
        print("❌ OPENAI_API_KEY not found in environment")
        print("   Create .env file with: OPENAI_API_KEY=sk-proj-...")
        return False
        
    if not PINECONE_API_KEY:
        print("❌ PINECONE_API_KEY not found in environment") 
        print("   Add to .env file: PINECONE_API_KEY=pc-...")
        return False
    
    print("✅ API keys loaded from environment")
    
    # Cross-platform file paths (priority: TXT > PDF > DOCX > MD)
    file_paths = [
        "../knowledge_base/document.txt",    # ✅ Best for RAG - universal
        "../knowledge_base/document.pdf",    # ✅ Common format
        "../knowledge_base/document.docx",   # ✅ Office format (no pywin32)
        "../knowledge_base/document.md",     # ✅ Markdown
        "../document.txt",                   # Fallback locations
        "document.txt",
        "./document.docx",
        "./README.md"                       # Test file
    ]
    
    # Show available dependencies
    deps_status = []
    if PDF_SUPPORT:
        deps_status.append("PDF ✅")
    else:
        deps_status.append("PDF ❌")
    if DOCX_SUPPORT:
        deps_status.append("DOCX ✅")
    else:
        deps_status.append("DOCX ❌")
    
    print(f"📋 Support status: TXT ✅, MD ✅, {', '.join(deps_status)}")
    
    # 1. ✅ Use cross-platform loader  
    print("📄 Looking for documents...")
    document = None
    found_path = None
    
    for path in file_paths:
        if os.path.exists(path):
            print(f"   Found: {path}")
            document = load_cross_platform_document(path)  # ✅ CROSS-PLATFORM
            if document:
                found_path = path
                break
    
    if not document:
        print("❌ No supported document found. Please put your file in:")
        print("   ./knowledge_base/document.txt  (TXT - best for RAG)")
        if PDF_SUPPORT:
            print("   ./knowledge_base/document.pdf  (PDF)")
        if DOCX_SUPPORT:
            print("   ./knowledge_base/document.docx (DOCX)")
        print("   ./knowledge_base/document.md   (Markdown)")
        print(f"\n💡 Missing dependencies? Install: pip install PyPDF2 docx2txt")
        return False
    
    documents = [document]  # Convert to list for compatibility
    print(f"✅ Loaded: {found_path}")
    print(f"   Characters: {len(document.text):,}")
    print(f"   Words: {len(document.text.split()):,}")
    print(f"   Type: {document.metadata.get('type', 'unknown')}")
    
    # 2. ✅ Use chunking.py component  
    print("\n✂️ Chunking document...")
    chunks = chunk_documents_by_sections(documents, max_section_length=1000)  # ✅ SECTION-BASED CHUNKING
    print(f"✅ Created {len(chunks)} chunks")
    print(f"   Average chunk size: {sum(len(c.text) for c in chunks) // len(chunks)} chars")
    
    # Show sample
    print(f"📝 Sample chunk: {chunks[0].text[:100]}...")
    
    # 3. ✅ Use vectordb.py component
    print("\n🔧 Setting up Pinecone...")
    manager = PineconeManager(  # ✅ EXISTING CLASS
        api_key=PINECONE_API_KEY,
        index_name="attacker2",
        dimension=1024,
        environment="us-east-1"
    )
    
    # ✅ EXISTING METHOD
    if not manager.create_index():
        print("❌ Pinecone setup failed")
        return False
    
    print("✅ Pinecone ready")
    
    # 4. ✅ Use existing upload method
    print("\n📤 Uploading to vector database...")
    print("⏳ This may take 30-60 seconds...")
    
    success = manager.add_documents(chunks)  # ✅ EXISTING METHOD
    
    if success:
        print("🎉 Upload successful!")
        
        # 5. ✅ Test search with document content preview
        print("\n🔍 Testing search...")
        
        # First, show what's actually in the document
        print(f"📄 Document preview (first 200 chars):")
        print(f"   {document.text[:200]}...")
        
        # Extract some actual words from document for testing
        words = document.text.split()[:10]  # First 10 words
        print(f"📝 First 10 words in document: {words}")
        
        # Test with both Vietnamese and actual document words
        test_queries = [
            "quy trình", "vay vốn", "sinh viên", "điều kiện",  # Vietnamese
            words[0] if words else "document",  # First word from doc
            words[1] if len(words) > 1 else "text",  # Second word
            " ".join(words[:3]) if len(words) >= 3 else "content"  # First 3 words
        ]
        
        for query in test_queries:
            results = manager.search_documents(query, top_k=2)  # ✅ EXISTING METHOD
            if results:
                print(f"✅ '{query}' → {len(results)} results")
                print(f"   Match: {results[0]['text'][:80]}...")
                print(f"   Score: {results[0].get('score', 'N/A')}")
            else:
                print(f"❌ '{query}' → No results")
        
        # 6. ✅ Debug and show stats
        print("\n🔍 Debugging index status...")
        
        # Wait a bit for Pinecone to update
        import time
        time.sleep(3)
        
        # Check direct Pinecone stats
        try:
            direct_stats = manager.index.describe_index_stats()
            print(f"📊 Direct Pinecone Stats:")
            print(f"   Total vectors: {direct_stats.get('total_vector_count', 0):,}")
            print(f"   Namespaces: {list(direct_stats.get('namespaces', {}).keys())}")
            
            # Check each namespace
            for ns_name, ns_stats in direct_stats.get('namespaces', {}).items():
                print(f"   Namespace '{ns_name}': {ns_stats.get('vector_count', 0)} vectors")
        except Exception as e:
            print(f"❌ Error getting direct stats: {e}")
        
        # Try search with different method
        print("\n🔍 Testing direct search...")
        try:
            # Direct Pinecone query
            query_response = manager.index.query(
                vector=[0.1] * 1024,  # dummy vector
                top_k=3,
                include_metadata=True
            )
            print(f"Direct query found: {len(query_response.matches)} matches")
            
        except Exception as e:
            print(f"❌ Direct query error: {e}")
        
        stats = manager.get_index_stats()  # ✅ EXISTING METHOD
        print(f"\n📊 LlamaIndex Stats:")
        print(f"   Total vectors: {stats.get('total_vectors', 0):,}")
        print(f"   Dimension: {stats.get('dimension', 0)}")
        print(f"   Index fullness: {stats.get('index_fullness', 0):.1%}")
        
        print("\n✅ RAG Knowledge Base Ready!")
        print("Next: Implement main_bot.py for chat interface")
        return True
        
    else:
        print("❌ Upload failed")
        return False

if __name__ == "__main__":
    try:
        result = asyncio.run(upload_to_pinecone())
        if result:
            print("\n🎯 Success! Your document is now in Pinecone vector database")
        else:
            print("\n💡 Fix the issues above and try again")
            
    except KeyboardInterrupt:
        print("\n⏹️  Upload cancelled")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n🔧 Common fixes:")
        print("1. Update API keys (lines 19-20)")
        print("2. Put document in ./knowledge_base/")
        print("3. Install: pip install -r requirements.txt")