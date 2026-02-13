import os
import logging
from app.ingestion.ingest import ingest
from app.retriever.qdrant_retriever import QdrantRetriever
from app.generation.generate_response import GenerateResponse
from app.logging_config import configure_logging

from cli_ans import *

# Configure logging based on ENABLE_LOGGING environment variable
configure_logging()

logger = logging.getLogger(__name__)

def build_vector_store(force_rebuild: bool):
    """Load FAISS index from disk if present, otherwise build it (ingest).
    Uses VECTOR_STORE_DIR env var; defaults to ./vector_store if unset.
    """
    vs_dir = os.getenv("VECTOR_STORE_DIR")
    if not vs_dir:
        vs_dir = "vector_store"
        os.environ["VECTOR_STORE_DIR"] = vs_dir  # keep ingest() consistent

    if (force_rebuild) and os.path.isdir(vs_dir) :
        ingest()




def run_rag(query: str, force_rebuild: bool = False, stream: bool = False):
    """
    Execute the RAG pipeline with optional streaming support.
    
    Args:
        query: User's question
        force_rebuild: Whether to rebuild the vector store
        stream: If True and provider is Ollama or Portkey, stream the response token by token
        
    Returns:
        dict: Contains 'answer' and 'sources', or None if streaming is enabled
        
    Note:
        When streaming is enabled, the answer is printed directly to console
        and the function returns None.
    """
    try :
        # 1) build vector store or not
        build_vector_store(force_rebuild=force_rebuild)

        # 2) Retrieve with similarity or HyDE based on mode
        logger.info("Retrieving documents...")
        retrieved = QdrantRetriever().retrieve(query=query)
        logger.info("Generating answer...")
        
        # Check if we should use streaming
        from app.load_secrets import LoadSecrets
        provider = LoadSecrets().get_provider()
        
        if stream and provider in ["ollama", "portkey"]:
            # Use streaming mode
            generator = GenerateResponse(retrieved, query)
            print("\n", end="", flush=True)  # Start on new line
            full_response = ""
            
            for chunk in generator.generate_stream():
                print(chunk, end="", flush=True)
                full_response += chunk
            
            print()  # New line after streaming completes
            
            try:
                used_sources = extracts_sources(full_response, retrieved)
                return {"answer": full_response, "sources": used_sources}
            except Exception:
                return {"answer": full_response, "sources": None}
        else:
            # Use non-streaming mode (original behavior)
            result_gen = GenerateResponse(retrieved, query).generate()
            
            try :
                used_sources = extracts_sources(result_gen, retrieved)
                return {"answer": result_gen, "sources": used_sources}
            except Exception :
                return {"answer" : result_gen, "sources": None}
    except Exception as e:
        logger.exception("An error occurred during RAG execution.")
        #import traceback
        #traceback.print_exc()
    


if __name__ == "__main__":
    logger.info("Type 'exit' to quit the console.")
    
    # Check if we're using Ollama or Portkey for streaming
    from app.load_secrets import LoadSecrets
    provider = LoadSecrets().get_provider()
    use_streaming = (provider in ["ollama", "portkey"])
    
    if use_streaming:
        logger.info(f"Streaming mode enabled for {provider}")
    
    query =""
    while(query != "exit"):
        query = input("Question : ")
        if query == "exit":
            break
        result = run_rag(query, force_rebuild=False, stream=use_streaming)

        if result:
            # If not streaming, print the answer (streaming already printed it)
            if not use_streaming:
                from rich.console import Console
                from rich.markdown import Markdown

                console = Console()

                def display_response(text):
                    md = Markdown(text)
                    console.print(md)
                
                print("\n\n\n")
                display_response(result["answer"])
                #print("\n", result["answer"])
    
            if result["sources"]:
                print("\nSources utilisées:")
                for s in result["sources"]:
                    print("- ", s)

        print("\n\n")
    print("Thank you for testing the RAG :)")
