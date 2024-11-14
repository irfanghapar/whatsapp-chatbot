import json
import time
from flask import jsonify
from openai import OpenAI
import os
from function.productDetails import ProductDetails

OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
client = OpenAI(api_key=OPENAI_API_KEY)
product_details = ProductDetails()

def check(thread_id, run_id):
    if not thread_id or not run_id:
        print("Error: Missing thread_id or run_id in /check")
        return jsonify({"response": "error"})

    try:
        start_time = time.time()
        while time.time() - start_time < 15:
            run_status = client.beta.threads.runs.retrieve(thread_id=thread_id,
                                                         run_id=run_id)
            print("Checking run status:", run_status.status)

            if run_status.status == 'completed':
                messages = client.beta.threads.messages.list(thread_id=thread_id)
                last_message = messages.data[0].content[0].text.value
                return jsonify({"response": last_message, "status": "completed"})

            if run_status.status == 'requires_action':
                print("Action required...")
                tool_calls = run_status.required_action.submit_tool_outputs.tool_calls
                tool_outputs = []

                for tool_call in tool_calls:
                    if tool_call.function.name == "get_product_info":
                        try:
                            arguments = json.loads(tool_call.function.arguments)
                            query = arguments.get("query", "")
                            print(f"Processing product query: {query}")

                            # Refresh product data before processing query
                            if not product_details.refresh_data():
                                print("Warning: Using cached product data")

                            response = product_details.get_product_info(query)
                            response_type = "list" if "1." in response else "single product"
                            print(f"Product info response type: {response_type}")

                            tool_outputs.append({
                                "tool_call_id": tool_call.id,
                                "output": json.dumps({"response": response})
                            })
                        except Exception as e:
                            print(f"Error processing product query: {str(e)}")
                            return jsonify({"error": "Failed to process product query"}), 500

                # Submit tool outputs back to the assistant
                if tool_outputs:
                    try:
                        client.beta.threads.runs.submit_tool_outputs(
                            thread_id=thread_id,
                            run_id=run_id,
                            tool_outputs=tool_outputs
                        )
                    except Exception as e:
                        print(f"Error submitting tool outputs: {str(e)}")
                        return jsonify({"error": "Failed to process request"}), 500

            elif run_status.status == 'failed':
                return jsonify({"error": "Assistant run failed"}), 500

            time.sleep(1)

        print("Run timed out")
        return jsonify({"response": "timeout"})

    except Exception as e:
        print(f"Error in check endpoint: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500