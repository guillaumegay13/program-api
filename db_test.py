from supabase import create_client, Client

url: str = 'https://gwaecqsezwyazhrmnnrx.supabase.co'
key: str = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imd3YWVjcXNlend5YXpocm1ubnJ4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MTMxNjg0MzAsImV4cCI6MjAyODc0NDQzMH0.oqdzLwYoMGyjce5XtHVByklKq1aH1Y02u8pC7W7eEgU'

supabase: Client = create_client(url, key)

def get_user_id_by_email(client, email: str) -> str:
    response = client.auth.admin.list_users(email=email)
    if response.error:
        print(f"Error fetching user ID: {response.error.message}")
        return None

    users = response.data['users']
    if users:
        return users[0]['id']
    else:
        print('User not found')
        return None
    
print(get_user_id_by_email(get_user_id_by_email, 'guillaume_gay@ymail.com'))