import logging
import os
import sys
from dotenv import load_dotenv

def configure_logging():
    """
    Configure logging based on ENABLE_LOGGING environment variable.
    
    If ENABLE_LOGGING is set to 'false' (case-insensitive), logging is effectively disabled
    by setting the level to CRITICAL for all loggers (including third-party libraries).
    Otherwise, logging is enabled at INFO level.
    
    This allows users to disable verbose logging output by setting ENABLE_LOGGING=false
    in their environment or .env file.
    """
    load_dotenv()
    enable_logging = os.getenv("ENABLE_LOGGING", "true").lower()
    
    if enable_logging == "false":
        # Disable all logging including third-party libraries
        logging.basicConfig(
            level=logging.CRITICAL,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        )
        # Suppress specific noisy loggers
        logging.getLogger("huggingface_hub").setLevel(logging.CRITICAL)
        logging.getLogger("haystack").setLevel(logging.CRITICAL)
        logging.getLogger("qdrant_client").setLevel(logging.CRITICAL)
        logging.getLogger("httpx").setLevel(logging.CRITICAL)
        logging.getLogger("urllib3").setLevel(logging.CRITICAL)
        
        # Disable all warnings
        import warnings
        warnings.filterwarnings("ignore")
        
        # Suppress transformers library verbosity (BERT model loading reports)
        try:
            import transformers
            transformers.utils.logging.set_verbosity_error()
        except ImportError:
            pass  # transformers not installed, skip
        
        # Suppress tqdm progress bars
        os.environ["TQDM_DISABLE"] = "1"
        
        # Redirect stderr to devnull to suppress model loading messages
        sys.stderr = open(os.devnull, 'w')
    else:
        # Enable logging at INFO level
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        )
