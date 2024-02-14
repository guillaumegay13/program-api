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
    
def generate_html(json_data, goal, include_body_analysis=False):
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
        html += f"<h2>Program</h2><p>{week['weekDescription']}</p>"
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

    if include_body_analysis:
        # TODO continue....
        html += f"<h2>Body Analysis</h2><p>{week['weekDescription']}</p>"
        html += f""" 
                <p><strong></strong><br>
        """


    conclusion = f"""<p>Good luck and stay strong!</p>"""
    html += conclusion

    html += """
        </body>
    </html>
    """
    return html