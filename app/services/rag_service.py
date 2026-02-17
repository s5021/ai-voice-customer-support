from langchain_community.document_loaders import TextLoader, DirectoryLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain_groq import ChatGroq
import os

class RAGService:
    def __init__(self, groq_api_key, docs_path="knowledge_base/docs", db_path="chroma_db"):
        self.groq_api_key = groq_api_key
        self.docs_path = docs_path
        self.db_path = db_path
        self.vectorstore = None
        self.qa_chain = None
        
        # Initialize embeddings
        print("Loading embeddings model...")
        self.embeddings = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'}
        )
        
        # Initialize LLM
        self.llm = ChatGroq(
            groq_api_key=groq_api_key,
            model_name="llama-3.3-70b-versatile",
            temperature=0.3,
            max_tokens=500
        )
        
        # Load or create vector store
        self._initialize_vectorstore()
    
    def _initialize_vectorstore(self):
        """Load existing vectorstore or create new one"""
        try:
            if os.path.exists(self.db_path) and os.listdir(self.db_path):
                print("Loading existing knowledge base...")
                self.vectorstore = Chroma(
                    persist_directory=self.db_path,
                    embedding_function=self.embeddings
                )
                print("Knowledge base loaded!")
            else:
                print("Creating new knowledge base...")
                self._create_vectorstore()
            
            # Create QA chain
            self._create_qa_chain()
            
        except Exception as e:
            print(f"Error initializing vectorstore: {e}")
    
    def _create_vectorstore(self):
        """Create vector store from documents"""
        try:
            # Load documents
            documents = []
            
            # Load text files
            if os.path.exists(self.docs_path):
                for filename in os.listdir(self.docs_path):
                    filepath = os.path.join(self.docs_path, filename)
                    
                    if filename.endswith('.txt'):
                        loader = TextLoader(filepath, encoding='utf-8')
                        documents.extend(loader.load())
                    elif filename.endswith('.pdf'):
                        loader = PyPDFLoader(filepath)
                        documents.extend(loader.load())
            
            if not documents:
                print("No documents found!")
                return
            
            print(f"Loaded {len(documents)} documents")
            
            # Split documents
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=500,
                chunk_overlap=50
            )
            chunks = text_splitter.split_documents(documents)
            print(f"Created {len(chunks)} chunks")
            
            # Create vector store
            self.vectorstore = Chroma.from_documents(
                documents=chunks,
                embedding=self.embeddings,
                persist_directory=self.db_path
            )
            self.vectorstore.persist()
            print("Knowledge base created and saved!")
            
        except Exception as e:
            print(f"Error creating vectorstore: {e}")
    
    def _create_qa_chain(self):
        """Create QA retrieval chain"""
        try:
            if self.vectorstore is None:
                return
            
            retriever = self.vectorstore.as_retriever(
                search_kwargs={"k": 3}
            )
            
            self.qa_chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=retriever,
                return_source_documents=True
            )
            print("QA chain ready!")
            
        except Exception as e:
            print(f"Error creating QA chain: {e}")
    
    def query(self, question, customer_context=""):
        """
        Query the RAG system
        
        Args:
            question: User's question
            customer_context: Optional customer data context
            
        Returns:
            dict with answer and sources
        """
        try:
            if self.qa_chain is None:
                return {
                    "answer": "Knowledge base not available.",
                    "sources": [],
                    "used_rag": False
                }
            
            # Add customer context to question if available
            full_question = question
            if customer_context:
                full_question = f"{question}\n\nCustomer Context: {customer_context}"
            
            # Query the chain
            result = self.qa_chain({"query": full_question})
            
            # Extract sources
            sources = []
            if "source_documents" in result:
                for doc in result["source_documents"]:
                    source = doc.metadata.get("source", "FAQ")
                    source = source.split("/")[-1]
                    if source not in sources:
                        sources.append(source)
            
            return {
                "answer": result["result"],
                "sources": sources,
                "used_rag": True
            }
            
        except Exception as e:
            print(f"Error in RAG query: {e}")
            return {
                "answer": None,
                "sources": [],
                "used_rag": False
            }
    
    def add_document(self, file_path):
        """Add new document to knowledge base"""
        try:
            if file_path.endswith('.txt'):
                loader = TextLoader(file_path, encoding='utf-8')
            elif file_path.endswith('.pdf'):
                loader = PyPDFLoader(file_path)
            else:
                return False
            
            documents = loader.load()
            
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=500,
                chunk_overlap=50
            )
            chunks = text_splitter.split_documents(documents)
            
            if self.vectorstore:
                self.vectorstore.add_documents(chunks)
                self.vectorstore.persist()
                return True
            
            return False
            
        except Exception as e:
            print(f"Error adding document: {e}")
            return False
    
    def reload_knowledge_base(self):
        """Reload knowledge base from scratch"""
        try:
            import shutil
            if os.path.exists(self.db_path):
                shutil.rmtree(self.db_path)
            self._create_vectorstore()
            self._create_qa_chain()
            return True
        except Exception as e:
            print(f"Error reloading knowledge base: {e}")
            return False