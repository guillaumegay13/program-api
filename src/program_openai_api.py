import base64
from openai import OpenAI
import json
from src.utils import extract_openai_response_content

class ProgramOpenAI():

    def __init__(self, text_model, image_model, openai_api_key):

        self.client = OpenAI()
        self.client.api_key = openai_api_key
        self.text_model = text_model
        self.image_model = image_model

    def analyse_image(self, image_binary, image_system_prompt, image_user_prompt):
        # Convert binary data to base64 encoded bytes
        image_base64_bytes = base64.b64encode(image_binary).decode('utf-8')

        response = self.client.chat.completions.create(
            model = self.image_model,
            # response_format={ "type": "json_object" },
            messages=[
                {"role": "system", "content": image_system_prompt},
                {
                "role": "user",
                "content": [
                    {"type": "text", "text": image_user_prompt},
                    {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image_base64_bytes}"
                    },
                    },
                ],
                }
            ],
            # Configurable ?
            max_tokens = 1500,
        )

        # Extract response
        json_content = extract_openai_response_content(response.json())

        # Parse the extracted JSON string
        content_data = json.loads(json_content)

        # Return content data
        return(content_data)
    
    def generate_program(self, input_system_prompt, input_user_prompt):

        response = self.client.chat.completions.create(
            model = self.text_model,
            # response_format={ "type": "json_object" },
            messages=[
                {"role": "system", "content": input_system_prompt},
                {
                "role": "user",
                "content": [
                    {"type": "text", "text": f"{input_user_prompt}"}
                ],
                }
            ],
            # Configurable ?
            max_tokens=4000,
        )

        return response.json()