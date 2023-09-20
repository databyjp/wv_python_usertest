# user_test.py
import weaviate
from weaviate import Config
import weaviate.weaviate_classes as wvc
import os

client = weaviate.Client(
    "http://localhost:8080",
    additional_config=Config(grpc_port_experimental=50051),
    # ⬇️ Optional, if you want to try it with an inference API:
    additional_headers={
        "X-OpenAI-Api-Key": os.environ["OPENAI_APIKEY"],  # Replace with your key
    },
)

print(client.is_ready())

import weaviate_datasets as wd

dataset = wd.JeopardyQuestions1k()
dataset.upload_dataset(client, 300)

questions = client.collection.get("JeopardyQuestion")

from weaviate.collection.classes.grpc import Generate

response = questions.query.near_text(
    query="The dark side",
    auto_limit=1,
    generate=Generate(single_prompt="Re-write this in Japanese: {question}")
)

print(response)