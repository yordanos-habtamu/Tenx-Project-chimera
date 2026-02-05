
import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logging():
    """
    Configure logging with both StreamHandler and RotatingFileHandler.
    Ensures logs directory exists.
    """
    # Ensure logs directory exists
    os.makedirs("logs", exist_ok=True)
    
    # Ensure logs directory exists
    os.makedirs("logs", exist_ok=True)
    
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Define formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # 1. Add StreamHandler if none exists
    has_stream = any(isinstance(h, logging.StreamHandler) for h in root_logger.handlers)
    if not has_stream:
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        root_logger.addHandler(stream_handler)
        
    # 2. Always add FileHandler (idempotent check)
    log_file = "logs/chimera.log"
    has_file = any(isinstance(h, RotatingFileHandler) and h.baseFilename.endswith("chimera.log") for h in root_logger.handlers)
    
    if not has_file:
        file_handler = RotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=5)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # Reduce noise from libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
