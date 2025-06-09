import logging
from functools import wraps
from flask import jsonify
from typing import Callable, Any

logger = logging.getLogger(__name__)

def handle_api_error(func: Callable) -> Callable:
    """Decorator to handle API errors gracefully"""
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            logger.error(f"ValueError in {func.__name__}: {e}")
            return jsonify({
                "status": "error",
                "error": {
                    "message": str(e),
                    "type": "validation_error"
                }
            }), 400
        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {e}")
            return jsonify({
                "status": "error",
                "error": {
                    "message": "Internal server error",
                    "type": "server_error"
                }
            }), 500
    
    return wrapper

class APIError(Exception):
    """Custom API exception"""
    def __init__(self, message: str, status_code: int = 400, error_type: str = "api_error"):
        self.message = message
        self.status_code = status_code
        self.error_type = error_type
        super().__init__(self.message)