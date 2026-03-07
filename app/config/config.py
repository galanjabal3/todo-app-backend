import os

PROVIDER = os.getenv("provider")
USER = os.getenv("user")
PASSWORD = os.getenv("password")
HOST = os.getenv("host")
PORT = os.getenv("port")
DBNAME = os.getenv("dbname")
ENVIRONMENT = os.getenv("environment")
JWT_SECRET = os.getenv("jwt_secret")
DOMAIN_URLS = os.getenv("domain_urls", "").split(",") if os.getenv("domain_urls") else []
SECRET_KEY = os.getenv("secret_key")

# Supabase Storage
SUPABASE_URL = os.getenv("supabase_url")
SUPABASE_SERVICE_KEY = os.getenv("supabase_service_key")