from workflow import Workflow
from langchain_community.chat_models import ChatOpenAI
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

gptJsonModel = ChatOpenAI(
    #models : https://platform.openai.com/docs/models/gpt-3-5
    #model="gpt-4-1106-preview",
    model="gpt-3.5-turbo-1106",
    model_kwargs={
        "response_format": {
            "type": "json_object"
        }
    }
)

# Define a Pydantic model for the JSON data input
class ProgramInput(BaseModel):
    type: str
    gender: str
    level: str
    frequency: int = None
    goal: str
    size: int
    weight: int
    age: int

app = FastAPI()

@app.post("/program/")
async def create_program(input_data: ProgramInput):
    result = Workflow(gptJsonModel, input_data.dict())
    return result

@app.get("/ping")
def ping():
    return "Hello!"

def main():
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()