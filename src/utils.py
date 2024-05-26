import yaml
import json
from datetime import datetime, timedelta

# Define a dictionary to map day names to their corresponding integer value
days_of_week = {
    'monday': 0,
    'tuesday': 1,
    'wednesday': 2,
    'thursday': 3,
    'friday': 4,
    'saturday': 5,
    'sunday': 6
}

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

    html += f"<h2>Program</h2>"

    # Then Program
    index = 1
    for week in json_data['weeks']:
        html += f"<h3>Week {index}</h3><p>{week['weekDescription']}</p>"
        index += 1
        for session in week['sessions']:
            html += f"<h4>Session {session['sessionNumber']}</h4><p>{session['description']}</p><ul>"
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

def insert_complete_program(program_data, client, email, input):

    days_specified = False

    if 'days' in input:

        days_specified = True

        # days as list
        days = input['days'].replace(' ', '').split(',')

        if len(days) != input["frequency"]:
            print("days don't match the frequency!")

        # Start date of the program is today, but it can be changed in the user's input
        today = datetime.now().date()

        # Start day of the program is the first selected day, which means it will start next week
        program_start_day = days[0]

        # program_start_date is the exact date when the program starts
        program_start_date = get_program_start_date(program_start_day, today)

        # Insert program
        program_response = client.table("programs").insert({
            "user_email": email,
            "program_raw": program_data,
            "start_date": program_start_date.isoformat() # as ISO 8601 string to be stored in supabase database
        }).execute()

    else:
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
            if days_specified:
                # days start at 0 while sessionNumner starts at 1
                session_date = get_session_date(program_start_date, days_of_week[program_start_day], days_of_week[days[session['sessionNumber'] - 1]], week["weekNumber"])
                session_response = client.table("sessions").insert({
                    "week_id": week_id,
                    "name": session["sessionName"],
                    "number": session['sessionNumber'],
                    "description": session['description'],
                    "reference": session['reference_to_method'],
                    "number_of_exercices": len(session['exercises']),
                    "session_date": session_date.isoformat()  # as ISO 8601 string to be stored in supabase database
                }).execute()
            else:
                session_response = client.table("sessions").insert({
                    "week_id": week_id,
                    "name": session["sessionName"],
                    "number": session['sessionNumber'],
                    "description": session['description'],
                    "reference": session['reference_to_method'],
                    "number_of_exercices": len(session['exercises'])
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

def get_program_start_date(start_day, today):

    # Get the integer value for the target day
    target_day_num = days_of_week[start_day.lower()]

    # Calculate how many days until the next occurrence of the target day
    days_until_next_target = (target_day_num - today.weekday() + 7) % 7
    if days_until_next_target == 0:  # If today is the target day, get the next occurrence
        days_until_next_target = 7

    # Get the date of the next target day
    next_target_date = today + timedelta(days=days_until_next_target)
    return next_target_date

# date, int, int, int
def get_session_date(program_start_date, start_day, session_day, week_number):
    session_date = program_start_date + timedelta(days=(session_day - start_day) + (week_number - 1) * 7)
    return session_date