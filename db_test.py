from supabase import create_client, Client

url: str = 'https://gwaecqsezwyazhrmnnrx.supabase.co'
key: str = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imd3YWVjcXNlend5YXpocm1ubnJ4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MTMxNjg0MzAsImV4cCI6MjAyODc0NDQzMH0.oqdzLwYoMGyjce5XtHVByklKq1aH1Y02u8pC7W7eEgU'

supabase: Client = create_client(url, key)

json = {
    "weeks": [
        {
            "weekNumber": 1,
            "weekDescription": "Intermediate Level Gym Training with Machines",
            "sessions": [
                {
                    "sessionNumber": 1,
                    "description": "High-Frequency Full Body Workout - Session 1",
                    "reference_to_method": "High-Frequency Full Body Workouts",
                    "exercises": [
                        {
                            "name": "Leg Press",
                            "description": "Compound exercise targeting quads, hamstrings, and glutes.",
                            "execution": "Sit in the leg press machine, place your feet shoulder-width apart on the platform, and extend your legs without locking your knees.",
                            "sets": 4,
                            "reps": 10,
                            "rest_in_seconds": 120
                        },
                        {
                            "name": "Chest Press",
                            "description": "Compound exercise for the chest, shoulders, and triceps.",
                            "execution": "Grip the handles and push forward in a smooth motion without locking your elbows.",
                            "sets": 3,
                            "reps": 10,
                            "rest_in_seconds": 120
                        },
                        {
                            "name": "Seated Cable Row",
                            "description": "Compound exercise for the back and biceps.",
                            "execution": "Pull the handle towards your torso, keeping your back straight and elbows close to your body.",
                            "sets": 3,
                            "reps": 10,
                            "rest_in_seconds": 120
                        },
                        {
                            "name": "Shoulder Press",
                            "description": "Compound movement for the deltoids.",
                            "execution": "Press the handles overhead without locking your elbows.",
                            "sets": 3,
                            "reps": 10,
                            "rest_in_seconds": 120
                        },
                        {
                            "name": "Tricep Pushdown",
                            "description": "Isolation exercise for the triceps.",
                            "execution": "Push the bar down until your elbows are fully extended, then slowly return.",
                            "sets": 3,
                            "reps": 12,
                            "rest_in_seconds": 60
                        },
                        {
                            "name": "Bicep Curl",
                            "description": "Isolation exercise for the biceps.",
                            "execution": "Curl the handles towards your shoulders without swinging your elbows.",
                            "sets": 3,
                            "reps": 12,
                            "rest_in_seconds": 60
                        },
                        {
                            "name": "Leg Curl",
                            "description": "Isolation exercise for the hamstrings.",
                            "execution": "Curl the legs towards your buttocks, maintaining smooth and controlled movement.",
                            "sets": 3,
                            "reps": 10,
                            "rest_in_seconds": 60
                        }
                    ]
                },
                {
                    "sessionNumber": 2,
                    "description": "Progressive Overload with Moderate Volume - Session 2",
                    "reference_to_method": "Progressive Overload with Moderate Volume",
                    "exercises": [
                        {
                            "name": "Squat Machine",
                            "description": "Compound exercise for lower body strength.",
                            "execution": "Use the squat machine to perform squats with a focus on progressive overload.",
                            "sets": 4,
                            "reps": 8,
                            "rest_in_seconds": 180
                        },
                        {
                            "name": "Incline Chest Press",
                            "description": "Compound exercise for the upper chest, shoulders, and triceps.",
                            "execution": "Incline the bench and press the weight upward in a controlled motion.",
                            "sets": 3,
                            "reps": 8,
                            "rest_in_seconds": 180
                        },
                        {
                            "name": "Lat Pulldown",
                            "description": "Compound exercise for the latissimus dorsi and biceps.",
                            "execution": "Pull the bar down to your chest, squeezing your shoulder blades together.",
                            "sets": 3,
                            "reps": 8,
                            "rest_in_seconds": 180
                        },
                        {
                            "name": "Leg Extension",
                            "description": "Isolation exercise for the quadriceps.",
                            "execution": "Extend your legs until they are straight, then slowly return to the starting position.",
                            "sets": 3,
                            "reps": 12,
                            "rest_in_seconds": 60
                        },
                        {
                            "name": "Calf Raise Machine",
                            "description": "Isolation exercise for the calves.",
                            "execution": "Lift your heels by extending your ankles and then lower them back down.",
                            "sets": 4,
                            "reps": 15,
                            "rest_in_seconds": 60
                        }
                    ]
                },
                {
                    "sessionNumber": 3,
                    "description": "Varied Intensity Training - Session 3",
                    "reference_to_method": "Varied Intensity Training",
                    "exercises": [
                        {
                            "name": "Machine Deadlift",
                            "description": "Compound exercise for overall posterior chain development.",
                            "execution": "Perform deadlifts using the machine to focus on form and varied intensity.",
                            "sets": 4,
                            "reps": 6,
                            "rest_in_seconds": 180
                        },
                        {
                            "name": "Pec Deck Fly",
                            "description": "Isolation exercise for the chest.",
                            "execution": "Bring the handles together in front of you, squeezing your chest muscles.",
                            "sets": 3,
                            "reps": 12,
                            "rest_in_seconds": 60
                        },
                        {
                            "name": "Seated Leg Curl",
                            "description": "Isolation exercise for the hamstrings.",
                            "execution": "Curl the weight towards your buttocks, focusing on the hamstring contraction.",
                            "sets": 3,
                            "reps": 10,
                            "rest_in_seconds": 60
                        },
                        {
                            "name": "Machine Shoulder Press",
                            "description": "Compound exercise for the deltoids.",
                            "execution": "Perform shoulder presses with the machine, varying the intensity throughout the sets.",
                            "sets": 3,
                            "reps": 8,
                            "rest_in_seconds": 120
                        },
                        {
                            "name": "Machine Preacher Curl",
                            "description": "Isolation exercise for the biceps.",
                            "execution": "Curl the weight while keeping your upper arms stationary on the pad.",
                            "sets": 3,
                            "reps": 12,
                            "rest_in_seconds": 60
                        },
                        {
                            "name": "Machine Tricep Extension",
                            "description": "Isolation exercise for the triceps.",
                            "execution": "Extend your arms to lower the weight, then slowly return to the starting position.",
                            "sets": 3,
                            "reps": 12,
                            "rest_in_seconds": 60
                        }
                    ]
                },
                {
                    "sessionNumber": 4,
                    "description": "Optimized Rest Interval Training - Session 4",
                    "reference_to_method": "Optimized Rest Interval Training",
                    "exercises": [
                        {
                            "name": "Machine Bench Press",
                            "description": "Compound exercise for the chest, shoulders, and triceps.",
                            "execution": "Press the weight up until your arms are extended, then lower it under control.",
                            "sets": 4,
                            "reps": 8,
                            "rest_in_seconds": 180
                        },
                        {
                            "name": "Machine Row",
                            "description": "Compound exercise for the back muscles.",
                            "execution": "Pull the weight towards your torso, keeping your shoulders down and back.",
                            "sets": 4,
                            "reps": 8,
                            "rest_in_seconds": 180
                        },
                        {
                            "name": "Machine Hack Squat",
                            "description": "Compound lower body exercise targeting the quads, hamstrings, and glutes.",
                            "execution": "Position yourself in the hack squat machine and perform the squat motion.",
                            "sets": 4,
                            "reps": 8,
                            "rest_in_seconds": 180
                        },
                        {
                            "name": "Machine Lateral Raise",
                            "description": "Isolation exercise for the lateral deltoids.",
                            "execution": "Lift the weight using your shoulders, keeping your arms straight, then lower under control.",
                            "sets": 3,
                            "reps": 15,
                            "rest_in_seconds": 60
                        },
                        {
                            "name": "Machine Ab Crunch",
                            "description": "Isolation exercise for the abdominal muscles.",
                            "execution": "Contract your abs to curl your upper body towards your knees.",
                            "sets": 3,
                            "reps": 20,
                            "rest_in_seconds": 60
                        }
                    ]
                },
                {
                    "sessionNumber": 5,
                    "description": "Incorporation of Advanced Techniques - Session 5",
                    "reference_to_method": "Incorporation of Advanced Techniques",
                    "exercises": [
                        {
                            "name": "Smith Machine Squat",
                            "description": "Compound exercise for the legs using the Smith machine for stability.",
                            "execution": "Squat down while keeping your back straight and push back up to the starting position.",
                            "sets": 4,
                            "reps": 8,
                            "rest_in_seconds": 180
                        },
                        {
                            "name": "Chest Fly Machine",
                            "description": "Isolation exercise for the pectoral muscles, incorporating drop sets.",
                            "execution": "Perform chest flies, and upon reaching failure, immediately reduce the weight and continue for more reps.",
                            "sets": 3,
                            "reps": "10-12, drop set on final set",
                            "rest_in_seconds": 60
                        },
                        {
                            "name": "Superset: Leg Extension and Leg Curl",
                            "description": "Isolation exercises for the quadriceps and hamstrings, performed back-to-back without rest.",
                            "execution": "Complete a set of leg extensions immediately followed by leg curls for one superset.",
                            "sets": 3,
                            "reps": "12 each exercise",
                            "rest_in_seconds": 60
                        },
                        {
                            "name": "Machine Overhead Press",
                            "description": "Compound exercise for the shoulders, incorporating supersets.",
                            "execution": "Perform overhead presses, and upon completion, immediately perform lateral raises with dumbbells.",
                            "sets": 3,
                            "reps": "8 press, 15 raise",
                            "rest_in_seconds": 120
                        },
                        {
                            "name": "Seated Calf Raise Machine",
                            "description": "Isolation exercise for the calves, using drop sets for intensity.",
                            "execution": "Perform calf raises, and upon reaching failure, reduce the weight and continue for more reps.",
                            "sets": 4,
                            "reps": "15, drop set on final set",
                            "rest_in_seconds": 60
                        }
                    ]
                }
            ]
        }
    ]
}

# supabase.table('programs').insert({"user_id": "9ded088f-9381-4764-a861-a7a9506bd050", "program_raw": json}).execute()

response = supabase.table('programs').select("*").execute()

print (response)