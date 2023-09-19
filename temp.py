from weaviate import Config
import weaviate
import os
import weaviate.weaviate_classes as wvc

client = weaviate.Client(
    "http://localhost:8080",
    additional_config=Config(grpc_port_experimental=50051),
    additional_headers={
        "X-OpenAI-Api-Key": os.environ["OPENAI_APIKEY"]
    }
)

for n in ["TestArticle", "TestAuthor"]:
    if client.schema.exists(n):
        client.schema.delete_class(n)

authors = client.collection.create(
    config=wvc.CollectionConfig(
        name="TestAuthor",
        properties=[
            wvc.Property(
                name="name",
                data_type=wvc.DataType.TEXT,
            ),
            wvc.Property(
                name="birth_year",
                data_type=wvc.DataType.INT,
            ),
        ],
        vectorizer_config=wvc.Text2VecOpenAIConfig(),
    )
)

authors_to_add = [
    wvc.DataObject(
        properties={
            "name": f"Jim {i+1}",
            "birth_year": 1970 + i
        }
    )
    for i in range(10)
]

authors.data.insert_many(authors_to_add)
