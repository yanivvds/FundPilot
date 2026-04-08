from dotenv import load_dotenv
import os

load_dotenv()
print("SUPABASE_URL=", os.getenv("SUPABASE_URL"))
print("SUPABASE_PUBLISHABLE_KEY=", os.getenv("SUPABASE_PUBLISHABLE_KEY"))
