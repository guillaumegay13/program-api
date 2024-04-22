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

    # Body Analysis first
    if include_body_analysis:
        html += f"<h2>Body Analysis</h2>"
        html += f"<h3>Body Fat Percentage Estimation</h2><p>{json_data['body_fat_percentage_estimate']}</p>"
        html += f"<h3>Muscular Definition and Symmetry</h3><p>{json_data['muscular_definition_and_symmetry']}</p>"
        html += f"<h3>Strength Indicators</h3><p>{json_data['strength_indicators']}</p>"
        html += f"<h3>Potential Weaknesses</h3><p>{json_data['potential_weaknesses']}</p>"

    # Then Program
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

    conclusion = f"""<p>Good luck and stay strong!</p>"""
    html += conclusion

    html += """
        </body>
    </html>
    """
    return html

def insert_complete_program(program_data, client, email):

    # Insert program
    program_response = client.table("programs").insert({
        "user_email": email,
        "program_raw": program_data
    }).execute()

    program_id = program_response.data[0]['id']

    # Insert weeks
    for week in program_data['weeks']:
        week_response = client.table("weeks").insert({
            "program_id": program_id,
            "number": week['weekNumber'],
            "description": week['weekDescription']
        }).execute()

        week_id = week_response.data[0]['id']

        # Insert sessions
        for session in week['sessions']:
            session_response = client.table("sessions").insert({
                "week_id": week_id,
                "number": session['sessionNumber'],
                "description": session['description'],
                "reference_to_method": session['reference_to_method']
            }).execute()

            session_id = session_response.data[0]['id']

            # Insert exercises and session exercises
            for exercise in session['exercises']:
                # Check if exercise already exists in the database to avoid duplication
                existing_exercise = client.table("exercises").select("*").eq("name", exercise['name']).execute()
                if not existing_exercise.data:
                    exercise_response = client.table("exercises").insert({
                        "name": exercise['name'],
                        "description": exercise['description'],
                        "execution": exercise['execution']
                    }).execute()
                    exercise_id = exercise_response.data[0]['id']
                else:
                    exercise_id = existing_exercise.data[0]['id']

                # Insert session specific exercise details
                session_exercise_response = client.table("session_exercises").insert({
                    "session_id": session_id,
                    "exercise_id": exercise_id,
                    "sets": exercise['sets'],
                    "reps": exercise['reps'],
                    "rest_in_seconds": exercise['rest_in_seconds']
                }).execute()

    return "Program and all related data inserted successfully"