from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI
import os 
from dotenv import load_dotenv
load_dotenv()

urls=["https://docs.python.org/3/tutorial/introduction.html",
       "https://docs.python.org/3/tutorial/controlflow.html",
       "https://docs.python.org/3/tutorial/datastructures.html"]
Loader=WebBaseLoader(urls)
docs=Loader.load()

text_splitter=RecursiveCharacterTextSplitter(chunk_size=1000,chunk_overlap=200)
texts=text_splitter.split_documents(docs)

embeddings=HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

vector_store=Chroma(
    collection_name="python-docs",
    embedding_function=embeddings,
    persist_directory="./chroma_db"
)

# Fix 3: use the recommended keyword argument so Chroma receives Documents explicitly.
vector_store.add_documents(documents=texts)

# Fix 1: Chroma.get() returns a dictionary, so read from the "documents" list safely.
sample_text = vector_store.get(limit=1)
stored_documents = sample_text.get("documents", [])
if stored_documents:
    print(stored_documents[0])
else:
    print("No documents found in the vector store.")


def retrieve_context(query):
    # Fix 2 and 5: call similarity_search correctly and retrieve the top 3 documents.
    retrieved_docs=vector_store.similarity_search(query, k=3)

    # Fix 8: handle empty retrieval results before building the prompt context.
    if not retrieved_docs:
        return "", []

    # Fix 5: concatenate retrieved document content into one context string.
    context="\n\n".join(doc.page_content for doc in retrieved_docs)
    
    # Fix 7: return the retrieved source documents alongside the context.
    return context, retrieved_docs

api_key=os.getenv("GOOGLE_API_KEY")

# Fix 8: fail early with a clear message when the Gemini API key is unavailable.
if not api_key:
    raise ValueError("Missing GOOGLE_API_KEY environment variable.")

llm=ChatGoogleGenerativeAI(model="gemini-2.0-flash",api_key=api_key)

def answer_question(question):
    # Fix 6: accept both the context string and source documents from retrieval.
    context, source_documents=retrieve_context(question)

    # Fix 8: return a useful fallback when no relevant chunks are found.
    if not context:
        return {
            "answer": "I don't know.",
            "source_documents": source_documents
        }

    # Fix 6: use a clear multiline system message with role, context, rules, and fallback.
    system_message=f"""
You are a helpful assistant.

Context:
{context}

Instructions:
- Answer the user's question only from the context above.
- If the context does not contain the answer, say "I don't know."
"""
    messages=[
        {"role":"system","content":system_message},
        {"role":"user","content":question}
    ]

    try:
        response=llm.invoke(messages)
    except Exception as exc:
        # Fix 8: handle failed model invocation without crashing the whole pipeline.
        return {
            "answer": f"Model invocation failed: {exc}",
            "source_documents": source_documents
        }

    # Fix 4 and 7: return generated text plus source documents, not the raw response object.
    return {
        "answer": response.content,
        "source_documents": source_documents
    }

queries = [
    "What are Python lists?",
    "Explain list comprehensions.",
    "What is a for loop?",
    "What is the break statement?"
]

for query in queries:
    result=answer_question(query)
    print(f"Question: {query}\nAnswer: {result['answer']}\n")

    for index, source_doc in enumerate(result["source_documents"], start=1):
        print(f"Source {index}: {source_doc.metadata.get('source', 'unknown')}")
    print()
    
