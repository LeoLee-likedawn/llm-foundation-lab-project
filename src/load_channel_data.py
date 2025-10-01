from common import f_print_log

from glob import glob
import warnings
warnings.filterwarnings("ignore")

# LangChain 핵심
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from langchain.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever
from langchain_chroma import Chroma

# 데이터 처리
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
# ollama 임베딩 모델 사용
from langchain_ollama import OllamaEmbeddings

import matplotlib
# 한글 폰트 인식 - Mac
matplotlib.rc('font', family='AppleGothic')
# 마이너스 부호 인식
matplotlib.rc("axes", unicode_minus = False)

#ollma 임베딩 사용 여부
embedding_type = "ollama" 

file_patterns = [
    'data/PRJ_CHN_ERR_LISTS.md',
]

def load_text_files(file_patterns):

    documents = []
    
    for pattern in file_patterns:
        files = glob(pattern)
        for file_path in files:
            try:
                loader = TextLoader(file_path, encoding='utf-8')
                docs = loader.load()
                documents.extend(docs)
                if f_print_log:
                    print(f"- load file complete...FILE[{file_path}]")
            except Exception as e:
                if f_print_log:
                    print(f"- !!! load file failed...FILE[{file_path}] ERROR[{e}]")    
    return documents

if f_print_log:
    print("Load file start...")  
raw_documents = load_text_files(file_patterns)
if f_print_log:
    print("-"*80)   

def preprocess_documents(documents):
    """
    문서 전처리 및 메타데이터 추가
    
    Args:
        documents (list): 원본 문서 리스트
    
    Returns:
        list: 전처리된 Document 객체 리스트
    """
    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        encoding_name="cl100k_base",
        separators=['\n\n\n'],
        chunk_size=180,
        chunk_overlap=50,
        is_separator_regex=True,
        keep_separator=True,
    )
    chunks = text_splitter.split_documents(documents)
    
    processed_docs = []
    for chunk in chunks:
        # Document 객체 생성
        doc = Document(
            page_content=f"<Document>\n{chunk.page_content}\n</Document>",
            metadata={
                **chunk.metadata,
                'language': 'ko',
                'chunk_length': len(chunk.page_content)
            }
        )
        processed_docs.append(doc)
    
    return processed_docs

processed_docs = preprocess_documents(raw_documents)
if f_print_log:
    print(f"Create chunk complete...CNT[{len(processed_docs)}]")    
    for i, doc in enumerate(processed_docs):
        print(f"\n- C#{i+1} : CHK[{doc.page_content}]")
    print("-"*80)

def load_vector_store(documents, embedding_type: str):
    """
    기존 벡터 저장소를 로드하거나 새로 생성
    
    Returns:
        Chroma: 벡터 저장소 객체
    """

    # 임베딩 선택
    if embedding_type == "ollama":
        embeddings = OllamaEmbeddings(model="bge-m3")
        collection_name="CHN_ERROR_LISTS_OLLAMA"
    else:
        embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        collection_name="CHN_ERROR_LISTS"

    persist_directory="./chroma_db_tuniverse"
    
    try:
        vector_store = Chroma(
            collection_name=collection_name,
            embedding_function=embeddings,
            persist_directory=persist_directory,
        )
        
        doc_count = vector_store._collection.count()
        if doc_count > 0:
            if f_print_log:
                print(f"Load vector store...CNT[{doc_count}]")
            return vector_store
        else:
            if f_print_log:
                print("!!! Empty vector store...Please add data.")
            
            vector_store = Chroma.from_documents(
                documents=documents,
                embedding=embeddings,
                collection_name=collection_name,
                persist_directory=persist_directory
            )
            
            if f_print_log:
                print(f"Vector store created...CNT[{vector_store._collection.count()}]")
            return vector_store
            
    except Exception as e:
        if f_print_log:
            print(f"!!! Vector store load failed...ERROR[{e}]")
        return None

def initialize_vector_store(embedding_type: str):
    """
    기존 벡터 저장소를 로드하거나 새로 생성
    
    Returns:
        Chroma: 벡터 저장소 객체
    """

    # 임베딩 선택
    if embedding_type == "ollama":
        embeddings = OllamaEmbeddings(model="bge-m3")
        collection_name="CHN_ERROR_LISTS_OLLAMA"
    else:
        embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        collection_name="CHN_ERROR_LISTS"

    persist_directory="./chroma_db_tuniverse"
    
    try:
        vector_store = Chroma(
            collection_name=collection_name,
            embedding_function=embeddings,
            persist_directory=persist_directory,
        )
        
        doc_count = vector_store._collection.count()
        if doc_count > 0:
            if f_print_log:
                print(f"Load vector store...CNT[{doc_count}]")
            return vector_store
        else:
            if f_print_log:
                print("!!! Empty vector store...Please add data.")            
            return vector_store
            
    except Exception as e:
        if f_print_log:
            print(f"!!! Vector store load failed...ERROR[{e}]")
        return None


# 벡터 저장소 초기화
chroma_db = load_vector_store(processed_docs, embedding_type)