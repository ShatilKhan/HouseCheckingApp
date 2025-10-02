"""
Logging utilities for industrial inspection system.

This module provides logging configuration and utilities for tracking
inspection operations, errors, and system events.
"""

import logging
import os
from datetime import datetime
from typing import Optional


def setup_logger(
    log_dir: str, 
    log_level: int = logging.INFO,
    max_log_size: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5
) -> logging.Logger:
    """
    Set up logging configuration for the inspection system.
    
    Args:
        log_dir: Directory to store log files
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        max_log_size: Maximum log file size in bytes before rotation
        backup_count: Number of backup log files to keep
        
    Returns:
        Configured logger instance
    """
    # Create log directory if it doesn't exist
    os.makedirs(log_dir, exist_ok=True)
    
    # Generate log filename with date
    date_str = datetime.now().strftime("%Y%m%d")
    log_filename = os.path.join(log_dir, f"inspection_{date_str}.log")
    
    # Create logger
    logger = logging.getLogger('InspectionSystem')
    logger.setLevel(log_level)
    
    # Remove existing handlers to avoid duplication
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    simple_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    
    # File handler with rotation
    from logging.handlers import RotatingFileHandler
    file_handler = RotatingFileHandler(
        log_filename,
        maxBytes=max_log_size,
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)
    logger.addHandler(file_handler)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    logger.addHandler(console_handler)
    
    return logger


def log_inspection_start(logger: logging.Logger, order_number: str, user: str) -> None:
    """
    Log the start of an inspection session.
    
    Args:
        logger: Logger instance
        order_number: Production order number
        user: User name
    """
    logger.info(f"=== INSPECTION SESSION STARTED ===")
    logger.info(f"Order Number: {order_number}")
    logger.info(f"User: {user}")
    logger.info(f"Timestamp: {datetime.now().isoformat()}")


def log_inspection_result(
    logger: logging.Logger, 
    part_number: str, 
    status: str, 
    measurements: list,
    defects: Optional[list] = None
) -> None:
    """
    Log inspection result for a part.
    
    Args:
        logger: Logger instance
        part_number: Part identification number
        status: Inspection status ("OK" or "NOK")
        measurements: List of measurement values
        defects: List of detected defects (if any)
    """
    logger.info(f"Part {part_number} inspection completed: {status}")
    logger.debug(f"Measurements: {measurements}")
    
    if defects:
        logger.warning(f"Defects detected in part {part_number}: {', '.join(defects)}")


def log_system_event(logger: logging.Logger, event_type: str, message: str) -> None:
    """
    Log system events like camera connection, file operations, etc.
    
    Args:
        logger: Logger instance
        event_type: Type of event (CAMERA, FILE, CONFIG, etc.)
        message: Event description
    """
    logger.info(f"[{event_type}] {message}")


def log_error(logger: logging.Logger, error_type: str, error_message: str, 
              exception: Optional[Exception] = None) -> None:
    """
    Log error events with optional exception details.
    
    Args:
        logger: Logger instance
        error_type: Type of error (CAMERA_ERROR, FILE_ERROR, etc.)
        error_message: Error description
        exception: Exception object (if available)
    """
    logger.error(f"[{error_type}] {error_message}")
    
    if exception:
        logger.exception(f"Exception details: {str(exception)}")


def log_performance_metric(
    logger: logging.Logger, 
    metric_name: str, 
    value: float, 
    unit: str = ""
) -> None:
    """
    Log performance metrics for monitoring.
    
    Args:
        logger: Logger instance
        metric_name: Name of the metric
        value: Metric value
        unit: Unit of measurement
    """
    unit_str = f" {unit}" if unit else ""
    logger.info(f"METRIC [{metric_name}]: {value}{unit_str}")


class InspectionLogger:
    """
    Specialized logger class for inspection operations.
    """
    
    def __init__(self, log_dir: str, order_number: str):
        """
        Initialize inspection logger.
        
        Args:
            log_dir: Directory for log files
            order_number: Production order number
        """
        self.order_number = order_number
        self.logger = setup_logger(log_dir)
        self.part_count = 0
        self.session_start_time = datetime.now()
    
    def start_session(self, user: str) -> None:
        """Start logging session."""
        log_inspection_start(self.logger, self.order_number, user)
    
    def log_part_processed(self, part_number: str, status: str, 
                          processing_time: float, defects: Optional[list] = None) -> None:
        """Log part processing result."""
        self.part_count += 1
        
        self.logger.info(
            f"Part {self.part_count}: {part_number} -> {status} "
            f"(processed in {processing_time:.2f}s)"
        )
        
        if defects:
            self.logger.warning(f"Defects in {part_number}: {', '.join(defects)}")
    
    def log_statistics(self, ok_count: int, nok_count: int) -> None:
        """Log session statistics."""
        total = ok_count + nok_count
        ok_rate = (ok_count / total * 100) if total > 0 else 0
        
        session_duration = datetime.now() - self.session_start_time
        
        self.logger.info(f"=== SESSION STATISTICS ===")
        self.logger.info(f"Duration: {session_duration}")
        self.logger.info(f"Total parts: {total}")
        self.logger.info(f"OK parts: {ok_count} ({ok_rate:.1f}%)")
        self.logger.info(f"NOK parts: {nok_count} ({100-ok_rate:.1f}%)")
    
    def get_logger(self) -> logging.Logger:
        """Get underlying logger instance."""
        return self.logger