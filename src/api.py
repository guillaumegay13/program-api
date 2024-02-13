from chain import Chain
import time
import json
import base64
from openai import OpenAI

class TrainProgramApi:

    # number_of_weeks = 4

    def __init__(self, model, input):

        # Init model and input
        self.model = model
        self.input = input
        self.client = OpenAI()

    def run_workflow(self):

        # Record the start time
        start_time = time.time()
        # Provide evidences
        self.evidences = self.provide_evidences()
        # Concatenate dict to build the next input
        GM_input = {**self.input, **self.evidences}
        self.methods = self.generate_methods(GM_input)
        # Concatenate dict to build the next input
        GP_input = {**self.input, **self.methods}
        self.program = self.generate_program(GP_input)

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
        self.time = round(end_time - start_time, 2)
    
    def provide_evidences(self):
        # Provide evidences prompt template
        # TODO: Add prompt to Hub (https://docs.smith.langchain.com/cookbook/hub-examples)
        PE_system_template = """You are a worldwide known scientist specialized in body science and fitness training.
        Your goal is to provide science-based evidences for a customized fitness training program tailored to the individual's goal of {goal}.
        Your recommendations should be backed by scientific research in the field of body science and should consider physiological data."""
        PE_human_template="""Please provide detailed and informative science-based evidences to assist in creating a tailored fitness plan for a person is a {gender} doing {type} training {frequency} times a week.
        The evidences should be related to any factor that influence the fitness plan to achieve the goal of {goal}, such as training method, intensity, number of reps, number of sets, type of exercices, techniques and rest.
        Return the evidences as a JSON and feel free to quote meta-analysis, studies, articles.
        The JSON should be structured as follow: "evidences": [ "topic": "training", "title": "title", "description": "description", "references": "references" ]"""
            
        # Create PE Chain
        PEChain = Chain(PE_system_template, PE_human_template, self.model)
        
        # Invoke
        return PEChain.invoke(**self.input)

    def generate_methods(self, input):

        if (input["number_of_weeks"] == "one"):
            GM_system_template = """You are a top-tier personal trainer known for crafting unique, result-driven fitness programs rooted in science.
            Based on the science-based evidences that the user will pass you, you will generate the best fitness {type} training methods for a {age} years old {gender} person {size}cm tall, weights {weight}. 
            Explain briefly how this method is related with the provided scientific evidences and why would it fits perfectly to this person.
            Return the training method as a JSON that follows this structure: "methods": [ "name": "name", "description": "description", "execution": "execution", "reference_to_evidence": "reference_to_evidence", "tailored": "tailored" ]"""
            GM_human_template="""{evidences}"""

        else:
            # Generate methods prompt template
            # TODO: Add prompt to Hub (https://docs.smith.langchain.com/cookbook/hub-examples)
            GM_system_template = """You are a top-tier personal trainer known for crafting unique, result-driven fitness programs rooted in science.
            Based on the science-based evidences that the user will pass you, you will generate the best fitness {type} training methods for a {age} years old {gender} person. 
            Explain briefly how those methods are related with the provided scientific evidences and why would they fit perfectly to this person.
            Return the training methods as a JSON that follows this structure: "methods": [ "name": "name", "description": "description", "execution": "execution", "reference_to_evidence": "reference_to_evidence", "tailored": "tailored" ]"""
            GM_human_template="""{evidences}"""

        # Create GM Chain
        GMChain = Chain(GM_system_template, GM_human_template, self.model)

        # Invoke
        return GMChain.invoke(**input)

    def generate_program(self, input):

        if (input["number_of_weeks"] == "one"):
            ## Add more parameters because we have more tokens available
            GP_system_template = """You are a top-tier personal trainer known for crafting unique, result-driven programs rooted in science.
            Based on the training methods the user will send, design a distinguished {number_of_weeks}-week {type} training schedule for a {gender} at an {level} level with a {level} level. 
            Each week MUST have exactly {frequency} sessions.
            You MUST return the program formatted as JSON object with the following fields: weeks [ weekNumber, weekDescription, sessions [ sessionNumber, description, reference_to_method, exercises [ name, description, execution, sets, reps, rest_in_seconds ] ] ]."""

        else:
            ## Generate weekly program prompt template
            # TODO: Add prompt to Hub (https://docs.smith.langchain.com/cookbook/hub-examples)
            ## Prompt one-week or four-weeks
            GP_system_template = """You are a top-tier personal trainer known for crafting unique, result-driven programs rooted in science.
            Based on the training methods the user will send, design a distinguished {number_of_weeks}-week {type} training schedule for a {gender} at an {level} level with a {level} level. 
            Each week MUST have exactly {frequency} sessions.
            You MUST return the program formatted as JSON object with the following fields: weeks [ weekNumber, weekDescription, sessions [ sessionNumber, description, reference_to_method, exercises [ name, sets, reps, rest_in_seconds ] ] ]."""
        
        # User template is the same regardless the number of weeks
        GP_user_template = """{methods}"""

        # Create WP Chain
        GPChain = Chain(GP_system_template, GP_user_template, self.model)

        # Invoke
        return GPChain.invoke(**input)
    
    def review_program(self, input):
        # TODO: Add program reviews
        # TODO: Add prompt to Hub (https://docs.smith.langchain.com/cookbook/hub-examples)
        review_system_template = """You are a world class physiotherapy.
        You will receive a fitness program and you need to review it and make sure that it is perfectly tailored for a {age} {gender} person, weight {weight} kg and {size} cm, with {level} level for a {type} training.
        You MUST return the program formatted as JSON object with the following fields: reviews [ problem, exercice, solution, replacement_exercice ]."""
        review_user_template = """{weeks}"""

        # Create WP Chain
        RChain = Chain(review_system_template, review_user_template, self.model)

        # Invoke
        return RChain.invoke(**input)
    
    def analyse_image(self, system_template, user_template, image_binary):
        # Convert binary data to base64 encoded bytes
        image_base64_bytes = base64.b64encode(image_binary).decode('utf-8')

        response = self.client.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=[
                {"role": "system", "content": system_template},
                {
                "role": "user",
                "content": [
                    {"type": "text", "text": user_template},
                    {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image_base64_bytes}"
                    },
                    },
                ],
                }
            ],
            max_tokens=1500,
        )

        outer_data = json.loads(response.json())

        # Access the "content" string
        content_string = outer_data["choices"][0]["message"]["content"]

        # Extract the JSON string from the "content" field
        # Here, removing the leading and trailing ```json and ``` along with escaped newlines
        json_content = content_string.strip("```json\n").rstrip("```").replace("\\n", "\n").replace('\\"', '"')

        # Parse the extracted JSON string
        content_data = json.loads(json_content)

        # Return content data
        return(content_data)
