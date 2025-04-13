import os
import json
import time
import datetime
from pathlib import Path

class ClaudeAPILogger:
    """Simple logger for Claude API requests and responses"""
    
    def __init__(self, log_dir="logs"):
        """Initialize the logger with a directory for log files"""
        self.log_dir = log_dir
        
        # Create logs directory if it doesn't exist
        Path(log_dir).mkdir(exist_ok=True)
        
        # Log file path - use date in filename
        self.log_file = os.path.join(
            log_dir, 
            f"claude_api_log_{datetime.datetime.now().strftime('%Y-%m-%d')}.json"
        )
        
        # Initialize log file if it doesn't exist
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w', encoding='utf-8') as f:
                f.write("[]")
    
    def log_api_call(self, request_data, response_data, resume_id, section, token_usage=None):
        """
        Log an API call to the log file - simplified to avoid serialization issues
        
        Args:
            request_data: Summary of the request to Claude API
            response_data: Summary of the response from Claude API
            resume_id: ID of the resume being processed
            section: Section of the resume being tailored
            token_usage: Token usage information if available
        """
        try:
            # Simplify to basic types to avoid serialization issues
            timestamp = datetime.datetime.now().isoformat()
            
            # Create a simplified log entry with only string/number values
            log_entry = {
                "timestamp": timestamp,
                "resume_id": str(resume_id),
                "section": str(section),
                "request": self._simplify_for_json(request_data),
                "response": self._simplify_for_json(response_data),
                "token_usage": self._simplify_for_json(token_usage or {})
            }
            
            # Load existing logs (simple approach)
            try:
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content and content != "[]":
                        logs = json.loads(content)
                    else:
                        logs = []
            except Exception as e:
                print(f"Error reading log file, starting fresh: {e}")
                logs = []
            
            # Add new log entry
            logs.append(log_entry)
            
            # Write updated logs back to file
            with open(self.log_file, 'w', encoding='utf-8') as f:
                json.dump(logs, f, ensure_ascii=False)
            
            print(f"API call logged to {self.log_file}")
            return True
        except Exception as e:
            print(f"Error logging API call: {str(e)}")
            return False
    
    def _simplify_for_json(self, data):
        """Convert complex data to simple JSON-serializable values"""
        if isinstance(data, (str, int, float, bool)) or data is None:
            return data
        elif isinstance(data, dict):
            return {k: self._simplify_for_json(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._simplify_for_json(item) for item in data]
        else:
            # For any other type, convert to string
            return str(data)
    
    def get_logs(self):
        """Get all logged API calls"""
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if content:
                    return json.loads(content)
                return []
        except Exception as e:
            print(f"Error reading logs: {e}")
            return []

# Global logger instance
api_logger = ClaudeAPILogger() 