from openai import OpenAI

from dotenv import load_dotenv

load_dotenv()

from openai import OpenAI


def generate_embedding(text):
    client = OpenAI()

    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )

    return response.data[0].embedding