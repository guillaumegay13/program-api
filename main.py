from api import TrainProgramApi
from langchain_community.chat_models import ChatOpenAI
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
import time

gptJsonModel = ChatOpenAI(
    #models : https://platform.openai.com/docs/models/gpt-3-5
    # trying GPT-4 turbo preview
    model="gpt-4-1106-preview",
    #model="gpt-3.5-turbo-1106",
    model_kwargs={
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

# Need all user input plus evidences as dict
class MethodsInput(UserInput):
    evidences: list

# Need all user input plus methods as dict
class ProgramInput(UserInput):
    methods: list

app = FastAPI()

@app.post("/api/provide_evidences/")
async def provide_evidences(input_data: UserInput):
    trainProgramApi = TrainProgramApi(gptJsonModel, input_data.dict())
    evidences = trainProgramApi.provide_evidences()
    return evidences

@app.post("/api/generate_methods/")
async def generate_methods(input_data: MethodsInput):
    trainProgramApi = TrainProgramApi(gptJsonModel, input_data.dict())
    methods = trainProgramApi.generate_methods(input_data.dict())
    return methods

@app.post("/api/generate_program/")
async def generate_program(input_data: ProgramInput):
    trainProgramApi = TrainProgramApi(gptJsonModel, input_data.dict())
    program = trainProgramApi.generate_program(input_data.dict())
    return program

# For the full workflow, only the User Input is needed
@app.post("/api/generate_train_program/")
async def generate_train_program(input_data: UserInput):
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
    assert len(self.program['weeks']) == self.number_of_weeks, "The number of weeks is not correct"
    for week in self.program['weeks']:
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

# Ping GET endpoint for testing purposes
@app.get("/api/ping")
def ping():
    return "Hello!"

@app.get("/api/deploy")
def ping():
    return "Deployed!"

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)