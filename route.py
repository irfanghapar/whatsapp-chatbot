from flask import request, jsonify
from api.lead.createLead import create_lead
from bot.start import start_conversation
from bot.chat import chat
from bot.check import check
# from api.getsku import extract_sku_with_ai, get_sku_info
from openai import OpenAI
import json
import os

client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])

def register_routes(app, assistant_id):
    @app.route('/create-lead', methods=['POST'])
    def import_data():
        # Get the JSON data from the request
        data = request.json

        # Print the received data to the console for testing
        print("Received data from ManyChat:")
        print(json.dumps(data, indent=2))

        # Extract relevant information
        full_name = data.get('name', '')
        phone = data.get('whatsapp_phone') or data.get('phone')
        email = data.get('email')
        inquiry_type = data.get('inquiry_type')
        inquiry_info = data.get('inquiry_info')
        rating = data.get('rating')
        review = data.get('review')
        assignee = data.get('assignee') or 'Eva - AI Assistant'

        # Create lead using the function from functions.py
        if full_name and phone:
            result = create_lead(full_name, phone, email, inquiry_type, inquiry_info, rating, review, assignee)
            if result:
                print(f"ManyChat lead created in Airtable for {full_name}")
                print(result)
            else:
                print(f"Failed to create ManyChat lead in Airtable for {full_name}")
        else:
            print(f"Insufficient information to create ManyChat lead. Name: '{full_name}', Phone: '{phone}'")

        # Return a response (ManyChat expects a 200 OK response)
        return jsonify({"status": "success"}), 200

    @app.route('/start', methods=['GET'])
    def start():
        return start_conversation()

    @app.route('/chat', methods=['POST'])
    def handle_chat():
        data = request.json
        if not data.get('thread_id'):
            # If no thread_id is provided, create a new thread
            thread = client.beta.threads.create()
            data['thread_id'] = thread.id
        return chat(assistant_id)

    @app.route('/check', methods=['POST'])
    def handle_check_run_status():
        data = request.json
        thread_id = data.get('thread_id')
        run_id = data.get('run_id')
        return check(thread_id, run_id)

    # @app.route('/sku-info', methods=['POST'])
    # def handle_sku_request():
    #     try:
    #         data = request.json
    #         user_message = data.get('message', '')

    #         # Extract SKU using OpenAI
    #         sku = extract_sku_with_ai(user_message)
    #         if not sku:
    #             return jsonify({
    #                 "status": "error",
    #                 "message": "No SKU number found in the message"
    #             }), 400

    #         # Get SKU information
    #         sku_info = get_sku_info(sku)
    #         if not sku_info:
    #             return jsonify({
    #                 "status": "error",
    #                 "message": "SKU not found"
    #             }), 404

    #         # Updated system prompt with strict formatting rules
    #         response = client.chat.completions.create(
    #             model="gpt-3.5-turbo",
    #             messages=[
    #                 {
    #                     "role": "system",
    #                     "content": """You must format the product information as what have been stated in prompt. Remove any bold or asterisks."""

    #                 },
    #                 {
    #                     "role": "user",
    #                     "content": f"Format this product information: {json.dumps(sku_info)}"
    #                 }
    #             ],
    #             temperature=0.8 # Changed to 0 for more consistent output
    #         )

    #         formatted_response = response.choices[0].message.content

    #         return jsonify({
    #             "status": "success",
    #             "formatted_response": formatted_response
    #         })

    #     except Exception as e:
    #         return jsonify({
    #             "status": "error",
    #             "message": f"Error processing request: {str(e)}"
    #         }), 500

    @app.route('/get-product-image', methods=['POST'])
    def handle_product_image():
        try:
            # Get the raw text input directly from the request
            ai_output = request.get_data(as_text=True)

            if not ai_output:
                return jsonify({
                    "status": "error",
                    "message": "No input provided"
                }), 400

            # Find URL starting with https://
            start_index = ai_output.find('https://')
            if start_index == -1:
                return jsonify({
                    "status": "error",
                    "message": "No image URL found in the provided data"
                }), 404

            # Extract everything after "Image: " until the end of line or string
            image_url = ai_output[start_index:].split('\n')[0].strip()

            # Remove any trailing quotes
            image_url = image_url.rstrip('"').rstrip("'")

            # Basic URL validation
            if not image_url.startswith('https://'):
                return jsonify({
                    "status": "error",
                    "message": "Invalid URL format"
                }), 400

            print(f"Successfully extracted URL: {image_url}")
            return jsonify({
                "status": "success",
                "image_url": image_url
            })

        except Exception as e:
            print(f"Error processing request: {str(e)}")
            return jsonify({
                "status": "error",
                "message": f"Error processing request: {str(e)}"
            }), 500