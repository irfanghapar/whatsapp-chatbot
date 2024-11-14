from flask import request, jsonify
from openai import OpenAI
import os

client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])

def chat(assistant_id):
    try:
        data = request.json
        thread_id = data.get('thread_id')
        message = data.get('message')

        # Validate inputs
        if not thread_id or not message:
            return jsonify({"error": "Missing thread_id or message"}), 400

        # Create message in thread
        message = client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=message
        )

        # Create run
        run = client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=assistant_id
        )

        return jsonify({
            "thread_id": thread_id,
            "run_id": run.id
        })

    except Exception as e:
        print(f"Error in chat: {str(e)}")
        return jsonify({"error": str(e)}), 500