import yaml
import json

def read_config(file_path):
    with open(file_path, 'r') as stream:
        try:
            config = yaml.safe_load(stream)
            return config
        except yaml.YAMLError as exc:
            print(exc)

def extract_openai_response_content(data):
    return json.loads(data)["choices"][0]["message"]["content"].strip("```json\n").rstrip("```").replace("\\n", "\n").replace('\\"', '"')

def load_template(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)