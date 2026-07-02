#!/usr/bin/env python3
##############################################################################
###
### This file is part of the BBS software (Bioconductor Build System).
###

import sys
import logging


# BBS-style format (matching existing output style)
BBS_LOG_FORMAT = "BBS> [%(asctime)s] %(message)s"
BBS_LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logger(level=logging.INFO, use_bbs_format=True):
    """
    Configure logging for BBS scripts.
    
    Args:
        level: Logging level (default: INFO)
        use_bbs_format: If True, use BBS-style format. If False, use standard format.
    
    Returns:
        logger: Configured logger instance
    
    Example:
        logger = setup_logger()
        logger.info('Starting STAGE2')
        logger.debug('Detailed debug info')
    """
    if use_bbs_format:
        log_format = BBS_LOG_FORMAT
        date_format = BBS_LOG_DATE_FORMAT
    
    logger = logging.getLogger('BBS')
    logger.setLevel(level)
    
    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(log_format, datefmt=date_format)
    
    # Console handler (stdout for BBS output)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger


def get_logger(name='BBS'):
    """Get the BBS logger instance."""
    return logging.getLogger(name)


if __name__ == "__main__":
    # Test the logging module
    logger = setup_logger()
    
    logger.info("This is an info message")
    logger.debug("This is a debug message")
    
    print("\nLogging module working correctly!")
