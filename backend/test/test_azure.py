import os
import traceback
from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv()

print("Starting Azure test...")
print("Endpoint:", os.getenv("AZURE_OPENAI_ENDPOINT"))
print("Deployment:", os.getenv("AZURE_OPENAI_DEPLOYMENT"))
print("API Version:", os.getenv("AZURE_OPENAI_API_VERSION"))
print("API Key Exists:", bool(os.getenv("AZURE_OPENAI_API_KEY")))

try:
    client = AzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    )

    print("Client created")

    response = client.chat.completions.create(
        model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
        messages=[
            {"role": "user", "content": "Say only Hello"}
        ],
    )

    print("Response received:")
    print(response.choices[0].message.content)

except Exception as e:
    print("\n===== ERROR =====")
    print(type(e).__name__)
    print(e)
    traceback.print_exc()