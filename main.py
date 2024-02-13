from api import TrainProgramApi
from langchain_community.chat_models import ChatOpenAI
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
import uvicorn
import time
import requests
import logging
import base64
from utils import read_config

config_file = 'config.yaml'
config_data = read_config(config_file)

TRIGGER_URL = config_data['zapier']['trigger_url']
OPENAI_API_KEY = config_data['openai']['key']
GPT_MODEL = config_data['openai']['text_model']

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
    image: bytes = None

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
    return generate_program(input_data)

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
    email = input_data.dict()["email"]
    goal = input_data.dict()["goal"]
    logging.info(f"Task started for {email}.")
    program = generate_program(input_data)
    logging.info(f"Task ended for {email}.")
    trigger_zap(email, program, goal)
    
def trigger_zap(email, program, goal):
    logging.info(f"Triggering Zap for {email}")
    html_body = generate_html(program, goal)
    input = {'email': email, "body": html_body}
    response = requests.post(TRIGGER_URL, json=input)
    if response.status_code == 200:
        logging.info(response.json())
    else:
        logging.info(f'Error: {response.status_code}')

def generate_program(input_data):
    input = input_data.dict()
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

def generate_html(json_data, goal):
    html = """
    <html>
        <head>
            <style>
                body {
                    font-family: 'Courier New', Courier, monospace;
                    margin: 20px;
                    color: #000;
                    background-color: #fff;
                }
                h2, h3 {
                    border-bottom: 1px solid #000;
                    padding-bottom: 5px;
                }
                p {
                    margin: 5px 0 20px 0;
                }
                ul {
                    list-style-type: none;
                    padding-left: 0;
                }
                li {
                    margin-bottom: 5px;
                }
            </style>
        </head>
        <body>
    """
    
    introduction = f"""<p>Hello,</p>
            <p>This email outlines your personalized workout plan designed to help you {goal}. Please review the weekly schedule and each session's details to get started.</p>"""
    html += introduction

    for week in json_data['weeks']:
        html += f"<h2>Week {week['weekNumber']}</h2><p>{week['weekDescription']}</p>"
        for session in week['sessions']:
            html += f"<h3>Session {session['sessionNumber']}</h3><p>{session['description']}</p><ul>"
            # html += f"<li>{session['reference_to_method']}</li>"
            html += "</ul>"
            for exercise in session['exercises']:
                html += f"""
                <p><strong>{exercise['name']}</strong><br>
                {exercise['description']}<br>
                Execution: {exercise['execution']}<br>
                Sets: {exercise['sets']}, Reps: {exercise['reps']}, Rest: {exercise['rest_in_seconds']} seconds</p>
                """

    conclusion = f"""<p>Good luck and stay strong!</p>"""
    html += conclusion

    html += """
        </body>
    </html>
    """
    return html

def analyse_image(image_binary):
    # Convert binary data to base64 encoded bytes
    image_base64_bytes = base64.b64encode(image_binary).decode('utf-8')
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }

    payload = {
        "model": "gpt-4-vision-preview",
        "messages": [
        {
            "role": "user",
            "content": [
            {"type": "text", "text": "What’s in this image?"},
            {
                "type": "image_url",
                "image_url": {
                "url": f"data:image/jpeg;base64,{image_base64_bytes}"
                }
            }
            ]
        }
        ],
        "max_tokens": 300
    }

    # Make the API request and print out the response
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    print(response.json())

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)