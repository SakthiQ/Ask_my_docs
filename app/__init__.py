import os
from dotenv import load_dotenv

# Load .env file BEFORE anything else runs
load_dotenv()

# Set HF_TOKEN for HuggingFace (it looks for this specific env var)
hf_token = os.getenv("HF_TOKEN")
if hf_token:
    os.environ["HF_TOKEN"] = hf_token
    os.environ["HUGGING_FACE_HUB_TOKEN"] = hf_token
