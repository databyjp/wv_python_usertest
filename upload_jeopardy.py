from weaviate import Config
import weaviate_datasets as wd
import weaviate
import os

client = weaviate.Client(
    "http://localhost:8080",
    additional_config=Config(grpc_port_experimental=50051),
    additional_headers={
        "X-OpenAI-Api-Key": os.environ["OPENAI_APIKEY"],
    },
)

client.schema.delete_all()

dataset = wd.JeopardyQuestions1k()
dataset.upload_dataset(client, batch_size=300)
