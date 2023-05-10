import os

# Load environment variables
BOT_TOKEN = os.environ.get('BOT_TOKEN')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
MODEL_ENGINE = os.environ.get('MODEL_ENGINE', 'text-davinci-002')
MODEL_TOKENS = int(os.environ.get('MODEL_TOKENS', '150'))
MODEL_TEMPERATURE = float(os.environ.get('MODEL_TEMPERATURE', '0.5'))
MONGO_USERNAME = os.environ.get('MONGO_USERNAME', 'root')
MONGO_PASSWORD = os.environ.get('MONGO_PASSWORD', 'root')
MONGO_DATABASE = os.environ.get('MONGO_DATABASE', 'test')
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost')
MONGO_PORT = int(os.environ.get('MONGO_PORT', '27017'))
