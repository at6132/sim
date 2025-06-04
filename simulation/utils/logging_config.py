import logging
import sys
import os
from logging.handlers import RotatingFileHandler

def setup_logging(log_level=logging.INFO, log_file='simulation.log'):
    """
    Set up logging configuration for the entire simulation.
    
    Args:
        log_level: The logging level to use (default: INFO)
        log_file: The file to write logs to (default: simulation.log)
    """
    # Create logs directory if it doesn't exist
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    log_path = os.path.join(log_dir, log_file)
    
    # Set up root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Remove any existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    simple_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Console handler (simple format)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(simple_formatter)
    console_handler.setLevel(log_level)
    root_logger.addHandler(console_handler)
    
    # File handler (detailed format)
    file_handler = RotatingFileHandler(
        log_path,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setFormatter(detailed_formatter)
    file_handler.setLevel(log_level)
    root_logger.addHandler(file_handler)
    
    # Set up specific loggers for each system
    systems = [
        'SocietySystem',
        'TransportationSystem',
        'MarineSystem',
        'ClimateSystem',
        'TerrainSystem',
        'ResourceSystem',
        'PlantSystem',
        'AnimalSystem'
    ]
    
    for system in systems:
        logger = logging.getLogger(system)
        logger.setLevel(log_level)
        # Don't propagate to root logger to avoid duplicate messages
        logger.propagate = False
        
        # Add handlers
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
    
    return root_logger

def get_logger(name):
    """
    Get a logger instance for a specific component.
    
    Args:
        name: The name of the component/module
        
    Returns:
        logging.Logger: A configured logger instance
    """
    return logging.getLogger(name) 