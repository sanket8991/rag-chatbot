import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

model = os.getenv("OPENAI_MODEL")

response = client.responses.create(
    model=model,
    input="Reply with exactly: OpenAI connection successful."
)

print("Model:", model)
print("Response:", response.output_text)