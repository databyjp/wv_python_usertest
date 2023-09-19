import weaviate
import os

from weaviate import Config

client = weaviate.Client(
    "http://localhost:8080",
    additional_config=Config(grpc_port_experimental=50051),
    additional_headers={
        "X-OpenAI-Api-Key": os.environ["OPENAI_API_KEY"]
    }
)

if client.schema.exists("TestClass"):
    client.schema.delete_class("TestClass")

assert client.is_ready()

collection_config = {
    "class": "TestClass",
    "vectorizer": "text2vec-openai"
}

client.schema.create_class(collection_config)

assert client.schema.exists("TestClass")

with client.batch as batch:
    for i in range(10):
        data_obj = {
            "body": f"Something {i}"
        }
        batch.add_data_object(data_obj, "TestClass")

