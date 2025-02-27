import logging
import sys
from logging.handlers import RotatingFileHandler
from datetime import datetime
import colorama
from colorama import Fore, Style

# Initialize colorama for cross-platform color support
colorama.init()

class ColoredFormatter(logging.Formatter):
    COLORS = {
        'DEBUG': Fore.BLUE,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.RED + Style.BRIGHT,
    }

    def format(self, record):
        # Color the entire format string for console output
        color = self.COLORS.get(record.levelname, '')
        formatted_message = super().format(record)
        
        # Add color to the entire message for console output
        if color:
            formatted_message = f"{color}{formatted_message}{Style.RESET_ALL}"
            
        return formatted_message

def setup_logger():
    # Configure root logger to handle external library logs
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Create console handler for root logger
    root_console_handler = logging.StreamHandler(sys.stdout)
    root_console_handler.setFormatter(ColoredFormatter(
        '%(asctime)s │ %(levelname)-8s │ %(name)s │ %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    ))
    root_logger.addHandler(root_console_handler)

    # Setup application logger
    logger = logging.getLogger('journal_app')
    logger.setLevel(logging.INFO)
    
    # Prevent propagation to avoid duplicate logs
    logger.propagate = False

    # Console handler with colors
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_format = ColoredFormatter(
        '%(asctime)s │ %(levelname)-8s │ %(name)s │ %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_format)

    # File handler (without colors)
    file_handler = RotatingFileHandler(
        'logs/journal_app.log',
        maxBytes=1024 * 1024,  # 1MB
        backupCount=5
    )
    file_handler.setLevel(logging.INFO)
    file_format = logging.Formatter(
        '[%(asctime)s] %(levelname)-8s [%(name)s:%(lineno)d] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_format)

    # Add handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger

logger = setup_logger()