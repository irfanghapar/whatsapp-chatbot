import json
import os
from openai import OpenAI
from prompts import assistant_instructions

def create_assistant(client: OpenAI):
    # Check for existing assistant ID in file
    assistant_file = 'assistant.json'
    try:
        if os.path.exists(assistant_file):
            with open(assistant_file, 'r') as f:
                data = json.load(f)
                existing_id = data.get('assistant_id')
                if existing_id:
                    try:
                        client.beta.assistants.retrieve(existing_id)
                        print(f"Using existing assistant ID: {existing_id}")
                        return existing_id
                    except Exception as e:
                        print(f"Existing assistant not found: {e}")
    except Exception as e:
        print(f"Error reading assistant file: {e}")

    # Create a new assistant with unified product info function
    try:
        assistant = client.beta.assistants.create(
            instructions=assistant_instructions,
            model="gpt-3.5-turbo",
            tools=[{
                "type": "function",
                "function": {
                    "name": "get_product_info",
                    "description": "Get product information using either SKU or product description",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The customer's query - can contain SKU or product description"
                            }
                        },
                        "required": ["query"]
                    }
                }
            }]
        )

        # Save the assistant ID
        with open(assistant_file, 'w') as f:
            json.dump({'assistant_id': assistant.id}, f)

        print(f"Created new assistant with ID: {assistant.id}")
        return assistant.id

    except Exception as e:
        print(f"Error creating assistant: {str(e)}")
        return None