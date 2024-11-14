from flask import jsonify
from openai import OpenAI
import os

OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
client = OpenAI(api_key=OPENAI_API_KEY)

def start_conversation():
    thread = client.beta.threads.create()
    print("New conversation started with thread ID:", thread.id)
    return jsonify({"thread_id": thread.id})