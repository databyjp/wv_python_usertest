# from weaviate.collection.collection_model import (
#     CollectionConfigModel,
#     BaseProperty,
#     PropertyConfig,
#     ReferenceTo,
# )
from weaviate.weaviate_classes import BaseProperty

import weaviate

client = weaviate.Client("http://localhost:8080", additional_config=weaviate.Config(grpc_port_experimental=50051))

# from pydantic import Ba

class Group(BaseProperty):
    name: str

import weaviate.weaviate_classes as wvc


collection = client.collection_model.create(
    wvc.CollectionModelConfig(vectorizer=wvc.Vectorizer.NONE), Group
)
