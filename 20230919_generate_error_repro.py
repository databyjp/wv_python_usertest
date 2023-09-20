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

# user_test.py
for collection_name in ["TestArticle", "TestAuthor"]:
    client.collection.delete(collection_name)

articles = client.collection.create(
    name="TestArticle",
    properties=[
        wvc.Property(
            name="title",
            data_type=wvc.DataType.TEXT,
        ),
        wvc.Property(
            name="body",
            data_type=wvc.DataType.TEXT,
        ),
        wvc.Property(
            name="url",
            data_type=wvc.DataType.TEXT,
            tokenization=wvc.Tokenization.FIELD,
        ),
    ],
    vectorizer_config=wvc.VectorizerFactory.text2vec_openai(),
    generative_config=wvc.GenerativeFactory.openai(),
    replication_config=wvc.ConfigFactory.replication(factor=1),
    inverted_index_config=wvc.ConfigFactory.inverted_index(
        index_property_length=True
    )
)

authors = client.collection.create(
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
        wvc.ReferenceProperty(name="wroteArticle", target_collection="TestArticle")
    ],
    vectorizer_config=wvc.VectorizerFactory.text2vec_openai(),
)

print(client.collection.exists("TestAuthor"))
print(client.collection.exists("TestArticle"))

# user_test.py
my_first_obj = {
    "title": "Something something dark side",
    "body": "A long long time ago, in a galaxy far, far away...",
    "url": "http://www.starwars.com"
}

article_uuid = articles.data.insert(my_first_obj)
print(article_uuid)

# user_test.py
author_uuid = authors.data.insert(
    {
        "name": "G Lucas",
        "birth_year": 1944,
        "wroteArticle": wvc.ReferenceFactory.to(uuids=[article_uuid])
    }
)

print(author_uuid)

# user_test.py
articles_to_add = [
    wvc.DataObject(
        properties={
            "title": f"The best restaurants of {1980+i}:",
            "body": "1. McDonald's, 2. ...",
            "url": "ss"
        },
    )
    for i in range(5)
]

response = articles.data.insert_many(articles_to_add)

from weaviate.collection.classes.grpc import Generate

try:
    response = articles.query.near_text(
        query="The dark side",
        limit=1,
        generate=Generate(single_prompt="Re-write this in Japanese: {body}")
    )

    print(response)
except Exception as e:
    print(e)

response = (
    client.query.get("TestArticle", ["body"])
    .with_near_text({"concepts": ["The dark side"]})
    .with_limit(1)
    .with_generate(single_prompt="Re-write this in Japanese: {body}")
    .do()
)
print(response)