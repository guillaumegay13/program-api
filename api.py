from chain import Chain
import time

class TrainProgramApi:

    def __init__(self, model, input):

        # Init model and input
        self.model = model
        self.input = input

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
        assert len(self.program['weeks']) == 4, "The number of weeks is not correct"
        for week in self.program['weeks']:
            assert len(week['sessions']) == int(GP_input['frequency']), "The number of sessions per week is not correct"

        # Concatenate dict to build the next input
        review_input = {**input, **self.program}
        self.review = self.review_program(review_input)

        # Verify output quality
        for review in self.review['reviews']:
            assert review["problem"] is not None, "Problem is null"
            assert review["solution"] is not None, "soluion is null"
        
        # Record the end time
        end_time = time.time()
        self.time = round(end_time - start_time, 2)
    
    def provide_evidences(self):
        # Provide evidences prompt template
        # TODO: Add prompt to Hub (https://docs.smith.langchain.com/cookbook/hub-examples)
        PE_system_template = """You are a worldwide known scientist specialized in body science and fitness training.
        Your goal is to provide science-based evidences for a customized fitness training program tailored to the individual's goal of {goal}. 
        Your recommendations should be backed by scientific research in the field of body science and should consider physiological data."""
        PE_human_template="""Please provide detailed and informative science-based evidences to assist in creating a tailored fitness plan for a person is a {gender}, {size}cm tall, weights {weight}.
        The evidences should be related to any factor that influence the fitness plan to achieve the goal of {goal}, such as training method, intensity, number of reps, number of sets, type of exercices, techniques and rest.
        Return the evidences as a JSON and feel free to quote meta-analysis, studies, articles.
        The JSON should be structured as follow: "evidences": [ "topic": "training", "title": "title", "description": "description", "references": "references" ]"""
            
        # Create PE Chain
        PEChain = Chain(PE_system_template, PE_human_template, self.model)
        
        # Invoke
        return PEChain.invoke(**self.input)

    def generate_methods(self, input):

        # Generate methods prompt template
        # TODO: Add prompt to Hub (https://docs.smith.langchain.com/cookbook/hub-examples)
        GM_system_template = """You are a top-tier personal trainer known for crafting unique, result-driven fitness programs rooted in science.
        Based on the science-based evidences that the user will pass you, you will generate the best fitness {type} training methods for a {age} years old {gender} person. 
        Explain briefly how those methods are related with the provided scientific evidences and why would they fit perfectly to this person.
        Return the training method as a JSON that follows this structure: "methods": [ "name": "name", "description": "description", "execution": "execution", "reference_to_evidence": "reference_to_evidence", "tailored": "tailored" ]"""
        GM_human_template="""{evidences}"""

        # Create GM Chain
        GMChain = Chain(GM_system_template, GM_human_template, self.model)

        # Invoke
        return GMChain.invoke(**input)

    def generate_program(self, input):

        ## Generate weekly program prompt template
        # TODO: Add prompt to Hub (https://docs.smith.langchain.com/cookbook/hub-examples)
        GP_system_template = """You are a top-tier personal trainer known for crafting unique, result-driven programs rooted in science.
        Based on the training methods the user will send, design a distinguished four-week {type} training schedule for a {gender} at an {level} level with a {level} level. 
        Each week MUST have exactly {frequency} sessions.
        You MUST return the program formatted as JSON object with the following fields: weeks [ weekNumber, weekDescription, sessions [ sessionNumber, goal, description, reference_to_method, exercises [ name, description, sets, reps, restTime ] ] ]."""
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