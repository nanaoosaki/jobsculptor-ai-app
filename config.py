import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/uploads')
    ALLOWED_EXTENSIONS = {'docx'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload size
    
    # Claude API configuration
    CLAUDE_API_KEY = os.environ.get('CLAUDE_API_KEY')
    CLAUDE_API_URL = 'https://api.anthropic.com/v1/messages'
    
    # OpenAI API configuration
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    
    # Resume parsing configuration
    USE_LLM_RESUME_PARSING = os.environ.get('USE_LLM_RESUME_PARSING', 'true').lower() == 'true'
    LLM_RESUME_PARSER_PROVIDER = os.environ.get('LLM_RESUME_PARSER_PROVIDER', 'auto')  # 'auto', 'claude', 'openai'
