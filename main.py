from api import TrainProgramApi
from langchain_community.chat_models import ChatOpenAI
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

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
    evidences = trainProgramApi.provide_evidences()
    methods = trainProgramApi.generate_methods(evidences)
    return methods

@app.post("/api/generate_program/")
async def generate_program(input_data: ProgramInput):
    trainProgramApi = TrainProgramApi(gptJsonModel, input_data.dict())
    evidences = trainProgramApi.provide_evidences()
    methods = trainProgramApi.generate_methods(evidences)
    program = trainProgramApi.generate_program(methods)
    return program

# For the full workflow, only the User Input is needed
@app.post("/api/generate_train_program/")
async def generate_train_program(input_data: UserInput):
    trainProgramApi = TrainProgramApi(gptJsonModel, input_data.dict())
    # Run the end-to-end workflow
    # TODO : write the workflow code below instead of a class method
    trainProgramApi.run_workflow()

# Ping GET endpoint for testing purposes
@app.get("/api/ping")
def ping():
    return "Hello!"

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)