from langchain_community.chat_models import ChatOpenAI
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
import uvicorn
import time
import requests
import logging
from src.utils import read_config, load_template, generate_html, insert_complete_program
from src.openai_client import OpenAIClient
import firebase_admin
from firebase_admin import credentials, firestore
from firebase_service import FirebaseService

# Firebase
cred = credentials.Certificate("config/train-3328b-firebase-adminsdk-sz3ho-6f187f09df.json")
firebase_admin.initialize_app(cred)
db = firestore.client()
firebase_service = FirebaseService(db)

config_file = 'config/config.yaml'
config_data = read_config(config_file)

TRIGGER_URL = config_data['zapier']['trigger_url']
OPENAI_API_KEY = config_data['openai']['key']
GPT_MODEL = config_data['openai']['text_model']
config_file = 'config/config.yaml'
config_data = read_config(config_file)

IMAGE_MODEL = config_data['openai']['image_model']
TEXT_MODEL = config_data['openai']['text_model']
TYPEFORM_TOKEN = config_data['typeform']['token']

DEFAULT_WEEK_NUMBER = "one"

OPENAI_API_CLIENT = OpenAIClient(TEXT_MODEL, IMAGE_MODEL, OPENAI_API_KEY)

# Load the JSON prompt template
template = load_template('config/prompts.json')

image_system_prompt = template["analyse_image"][0]["system_template"]
image_user_prompt = template["analyse_image"][0]["user_template"]

gptJsonModel = ChatOpenAI(
    model = GPT_MODEL,
    model_kwargs = {
        "response_format": {
            "type": "json_object"
        }
    }
)

# Define a Pydantic model for the JSON data input
class UserInput(BaseModel):
    type: str
    gender: str
    level: str
    frequency: int = None
    goal: str
    size: int
    weight: int
    age: int
    number_of_weeks: str = None
    email: str = None
    # image is a URL
    image: str = None
    image_bytes: bytes = None
    days: str = None

# Need all user input plus evidences as dict
class MethodsInput(UserInput):
    evidences: list

# Need all user input plus methods as dict
class ProgramInput(UserInput):
    methods: list

app = FastAPI()

@app.post("/api/provide_evidences/")
async def provide_evidences_api(input_data: UserInput):
    input = input_data.dit()
    evidences = provide_evidences(input, OPENAI_API_CLIENT)
    return evidences

@app.post("/api/generate_methods/")
async def generate_methods_api(input_data: MethodsInput):
    input = input_data.dit()
    methods = generate_methods_from_evidences(input, OPENAI_API_CLIENT)
    return methods

@app.post("/api/generate_program/")
def generate_program_api(input_data: ProgramInput):
    input = input_data.dict()
    program = generate_program(input, OPENAI_API_CLIENT)
    return program

# For the full workflow, only the User Input is needed
@app.post("/api/generate_train_program/")
def generate_train_program_api(input_data: UserInput):
    input = input_data.dict()
    return generate_program(input)

# Ping GET endpoint for testing purposes
@app.get("/api/ping")
def ping():
    return "Hello!"

@app.post("/api/generate_train_program_background/")
def generate_train_program_background_api(background_tasks: BackgroundTasks, input_data: UserInput):
    background_tasks.add_task(background_task, input_data)
    return {"message": "Accepted. Your training program is being generated!"}

def background_task(input_data: UserInput):
    input = input_data.dict()
    email = input["email"]
    goal = input["goal"]
    gender = input['gender']
    level = input['level']
    frequency = input['frequency']
    goal = input['goal']
    size_in_cm = input['size']
    weight_in_kg = input['weight']
    age = input['age']
    logging.info(f"Task started for {email}.")

    if input['image']:
        # Image is a URL like
        # https://api.typeform.com/forms/oUyltSVy/responses/ytekltwpn4fmggq34s7kytekfln6xqq0/fields/fFn1Y2QDwCJQ/files/1dd1423e78c2-Will_Smith_Dad_Bod.png
        image_url = input["image"]
        typeform_headers = {
            "Authorization": f"Bearer {TYPEFORM_TOKEN}"
        }
        typeform_response = requests.get(image_url, headers=typeform_headers)
        if typeform_response.status_code == 200:
            input["image_bytes"] = typeform_response.content
            program = generate_program_multimodal(input)
            html_body = generate_html(program, goal, True)
        else:
            logging.info(f'Error: {typeform_response.status_code}')
    else:
        program = generate_program(input)
        html_body = generate_html(program, goal)
        # Store program
        insert_complete_program(program, email, input, firebase_service)
        # Store user profile
        firebase_service.insert_profile(email, gender, age, goal, level, frequency, size_in_cm, weight_in_kg)
        logging.info(f"Task ended for {email}.")

    trigger_zap(email, html_body)
    
def trigger_zap(email, html_body):
    logging.info(f"Triggering Zap for {email}")
    input = {'email': email, "body": html_body}
    response = requests.post(TRIGGER_URL, json=input)
    if response.status_code == 200:
        logging.info(response.json())
    else:
        logging.info(f'Error: {response.status_code}')

def provide_evidences(input, api_client):
    provide_evidences_system_prompt = template["provide_evidences"][0]["system_template"]
    provide_evidences_user_prompt = template["provide_evidences"][0]["user_template"].format(**input)
    evidences = api_client.invoke(provide_evidences_system_prompt, provide_evidences_user_prompt)
    # Remove nutrion related evidences
    for evidence in evidences["evidences"]:
        if "nutrition" in evidence["topic"].lower():
            del evidence
    return evidences

def generate_methods_from_evidences(input, api_client):
    # Generate training methods based on the evidences
    generate_methods_system_prompt = template["generate_methods"][0]["system_template"].format(**input)
    generate_methods_user_prompt = template["generate_methods"][0]["user_template"].format(**input)
    methods = api_client.invoke(generate_methods_system_prompt, generate_methods_user_prompt)
    return methods

def generate_program_from_methods(input, api_client):
    generate_program_system_prompt = template["generate_program_from_methods"][0]["system_template"].format(**input)
    generate_program_user_prompt = template["generate_program_from_methods"][0]["user_template"].format(**input)
    program = api_client.invoke(generate_program_system_prompt, generate_program_user_prompt)
    return program

def generate_program(input):
    api_client = OPENAI_API_CLIENT

    # Provide evidences
    evidences = provide_evidences(input, api_client)

    # Generate training methods based on the evidences
    methods = generate_methods_from_evidences({**input, **evidences}, api_client)

    # Generate program from the methods
    program = generate_program_from_methods({**input, **methods}, api_client)
    
    return program

def review_program(input, api_client):
    review_program_system_prompt = template["review_program"][0]["system_template"].format(**input)
    review_program_user_prompt = template["review_program"][0]["user_template"].format(**input)
    review = api_client.invoke(review_program_system_prompt, review_program_user_prompt)
    return review

def generate_program_multimodal(input):
    image_binary = input["image_bytes"]

    api_client = OPENAI_API_CLIENT
    image_analysis, returned = api_client.analyse_image(image_binary, image_system_prompt, image_user_prompt)

    if (returned):
        # Error handling
        assert image_analysis["muscular_definition_and_symmetry"] is not None, "muscular_definition_and_symmetry is null"
        assert image_analysis["body_fat_percentage_estimate"] is not None, "body_fat_percentage_estimate is null"
        assert image_analysis["strength_indicators"] is not None, "strength_indicators is null"
        assert image_analysis["potential_weaknesses"] is not None, "potential_weaknesses is null"

        muscular_definition_and_symmetry = image_analysis["muscular_definition_and_symmetry"]
        body_fat_percentage_estimate = image_analysis["body_fat_percentage_estimate"]
        strength_indicators = image_analysis["strength_indicators"]
        potential_weaknesses = image_analysis["potential_weaknesses"]

        # Input data
        age = input["age"]
        gender = input["gender"]
        weight = input["weight"]
        size = input["size"]
        level = input["level"]
        type = input["type"]
        weeks = DEFAULT_WEEK_NUMBER
        frequency = input["frequency"]
        goal = input["goal"]

        # Formatting the prompt with dynamic values
        system_prompt = template["generate_program_body_analysis"][0]["system_template"]
        user_prompt = template["generate_program_body_analysis"][0]["user_template"].format(muscular_definition_and_symmetry=muscular_definition_and_symmetry, body_fat_percentage_estimate=body_fat_percentage_estimate, strength_indicators=strength_indicators, potential_weaknesses=potential_weaknesses, age=age, gender=gender, weight=weight, size=size, level=level, type=type, frequency=frequency, goal=goal, weeks=weeks)

        program = api_client.generate_program(system_prompt, user_prompt)
    
        return({**program, **image_analysis})
    else:
        return ({**generate_program(input), **image_analysis})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)