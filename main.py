from src.api import TrainProgramApi
from langchain_community.chat_models import ChatOpenAI
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
import uvicorn
import time
import requests
import logging
from src.utils import read_config, extract_openai_response_content, load_template, generate_html
from src.program_openai_api import ProgramOpenAI
from supabase import create_client, Client

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

# Supabase
SUPABASE_URL = config_data['supabase']['url']
SUPABASE_KEY = config_data['supabase']['key']

DEFAULT_WEEK_NUMBER = "one"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

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

# Need all user input plus evidences as dict
class MethodsInput(UserInput):
    evidences: list

# Need all user input plus methods as dict
class ProgramInput(UserInput):
    methods: list

app = FastAPI()

@app.post("/api/provide_evidences/")
async def provide_evidences_api(input_data: UserInput):
    trainProgramApi = TrainProgramApi(gptJsonModel, input_data.dict())
    evidences = trainProgramApi.provide_evidences()
    return evidences

@app.post("/api/generate_methods/")
async def generate_methods_api(input_data: MethodsInput):
    trainProgramApi = TrainProgramApi(gptJsonModel, input_data.dict())
    methods = trainProgramApi.generate_methods(input_data.dict())
    return methods

@app.post("/api/generate_program/")
def generate_program_api(input_data: ProgramInput):
    trainProgramApi = TrainProgramApi(gptJsonModel, input_data.dict())
    program = trainProgramApi.generate_program(input_data.dict())
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

# For the full workflow, only the User Input is needed
@app.post("/api/generate_train_program/")
def generate_train_program_api(input_data: UserInput):
    return generate_program(input_data)

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
    if input["image"]:
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
    logging.info(f"Task ended for {email}.")

    # Store program
    supabase.table('programs').insert({"user_email": email, "program_raw": program}).execute()
    # Store user profile
    supabase.table('profiles').insert({"user_email": email, "gender": gender, 'age': age, 'goal': goal, 'level': level, 'frequency': frequency, 'size_in_cm': size_in_cm, 'weight_in_kg': weight_in_kg}).execute()

    trigger_zap(email, html_body)
    
def trigger_zap(email, html_body):
    logging.info(f"Triggering Zap for {email}")
    input = {'email': email, "body": html_body}
    response = requests.post(TRIGGER_URL, json=input)
    if response.status_code == 200:
        logging.info(response.json())
    else:
        logging.info(f'Error: {response.status_code}')

def generate_program(input):
    trainProgramApi = TrainProgramApi(gptJsonModel, input)
    # Run the end-to-end workflow
    # Record the start time
    start_time = time.time()
    # Provide evidences
    evidences = trainProgramApi.provide_evidences()
    for evidence in evidences["evidences"]:
        if "nutrition" in evidence["topic"].lower():
            del evidence
    # TODO: exclude nutrition
    # Concatenate dict to build the next input
    GM_input = {**input, **evidences}
    methods = trainProgramApi.generate_methods(GM_input)
    # Concatenate dict to build the next input
    GP_input = {**input, **methods}
    program = trainProgramApi.generate_program(GP_input)

    # Verify output quality
    """
    assert len(program['weeks']) == input["number_of_weeks"], "The number of weeks is not correct"
    for week in program['weeks']:
        assert len(week['sessions']) == int(GP_input['frequency']), "The number of sessions per week is not correct"
    """
        
     # Concatenate dict to build the next input
    """
    review_input = {**self.input, **self.program}
    self.review = self.review_program(review_input)

    # Verify output quality
       for review in self.review['reviews']:
        assert review["problem"] is not None, "Problem is null"
        assert review["solution"] is not None, "soluion is null"
    """
        
    # Record the end time
    end_time = time.time()
    duration = round(end_time - start_time, 2)
    print("duration = " + str(duration))
    return program

def generate_program_multimodal(input):
    image_binary = input["image_bytes"]

    api_client = ProgramOpenAI(TEXT_MODEL, IMAGE_MODEL, OPENAI_API_KEY)
    image_analysis = api_client.analyse_image(image_binary, image_system_prompt, image_user_prompt)

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
    system_prompt = template["generate_program_BD"][0]["system_template"]

    # print (template["generate_program_BD"][0])
    user_prompt = template["generate_program_BD"][0]["user_template_BD"].format(muscular_definition_and_symmetry=muscular_definition_and_symmetry, body_fat_percentage_estimate=body_fat_percentage_estimate, strength_indicators=strength_indicators, potential_weaknesses=potential_weaknesses, age=age, gender=gender, weight=weight, size=size, level=level, type=type, frequency=frequency, goal=goal, weeks=weeks)

    program = api_client.generate_program(system_prompt, user_prompt)
    
    return({**program, **image_analysis})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)