import os
import json
import shutil
from pathlib import Path

from flask import Flask
from packaging import version
import openai
from openai import OpenAI

from api.createAssistant import create_assistant
from route import register_routes

required_version = version.parse("1.1.1")
current_version = version.parse(openai.__version__)

OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
if current_version < required_version:
    raise ValueError(
        f"Error: OpenAI version {openai.__version__} is less than the required version 1.1.1"
    )
else:
    print("OpenAI version is compatible.")

data_dir = Path('data')
if not data_dir.exists():
    data_dir.mkdir()
    print("Created data directory")

def setup_dummy_json():
    source_path = 'dummy.json'
    dest_path = 'data/dummy.json'

    if not os.path.exists(dest_path):
        try:
            shutil.copy(source_path, dest_path)
            print("Created dummy.json in data directory")
        except FileNotFoundError:
            print("Warning: Source dummy.json not found")
        except Exception as e:
            print(f"Error creating dummy.json: {e}")

# Update the initialization code
data_dir = Path('data')
if not data_dir.exists():
    data_dir.mkdir()
    print("Created data directory")

# Verify dummy.json exists
if not (data_dir / 'dummy.json').exists():
    print("Warning: dummy.json not found in data directory")

app = Flask(__name__)
client = OpenAI(api_key=OPENAI_API_KEY)

# Load assistant ID from file or create new one
try:
    assistant_id = create_assistant(client)
    if not assistant_id:
        raise Exception("Failed to get assistant ID")
    print("Assistant created/retrieved with ID:", assistant_id)
except Exception as e:
    print(f"Fatal error: {e}")
    exit(1)  # Exit if we can't create/retrieve assistant

# Register routes
register_routes(app, assistant_id)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)