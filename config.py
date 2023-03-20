import os
from dotenv import load_dotenv, find_dotenv


load_dotenv(find_dotenv())

API_TOKEN = os.getenv('API_TOKEN')
