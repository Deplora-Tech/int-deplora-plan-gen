import os
from dotenv import load_dotenv, find_dotenv

env_path = find_dotenv()
print("Using .env from:", env_path)
load_dotenv(dotenv_path=env_path)

jenkins_url = os.getenv("JENKINS_URL")
print("repr:", repr(jenkins_url))
print("str :", jenkins_url)
