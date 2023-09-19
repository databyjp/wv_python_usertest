### Setup

Python 3.10.12
Installed client with:
`pip install git+https://github.com/weaviate/weaviate-python-client.git@main`
`pip install git+https://github.com/weaviate/weaviate-python-client.git@schema_dataclass`
`pip install git+https://github.com/weaviate/weaviate-python-client.git@pydantic_experiment`
`pip install git+https://github.com/weaviate/weaviate-python-client.git@addition_props`


pip install -U git+https://github.com/weaviate/weaviate-python-client.git@main
pip install -U git+https://github.com/weaviate/weaviate-python-client.git@grpc_batch

pip install -U "git+https://github.com/weaviate/weaviate-python-client.git@main#egg=weaviate-client[GRPC]"
pip install -U "git+https://github.com/weaviate/weaviate-python-client.git@pydantic_experiment#egg=weaviate-client[GRPC]"
pip install -U "git+https://github.com/weaviate/weaviate-python-client.git@grpc_batch#egg=weaviate-client[GRPC]"


pip install -U "git+https://github.com/weaviate/weaviate-python-client.git@grpc_vectorizer_auth#egg=weaviate-client[GRPC]"

pip install -U "git+https://github.com/weaviate/weaviate-python-client.git@grpc_client#egg=weaviate-client[GRPC]"
pip install -U "git+https://github.com/weaviate/weaviate-python-client.git@filters2#egg=weaviate-client[GRPC]"


### Notes

2023-06-23
- It might need class-level ModuleConfig setting added (e.g. for setting module models)
- X-references missing at this point. It could accept the target class directly?


client = weaviate.Client("http://localhost:8080", additional_config=weaviate.Config(grpc_port_experimental=50051))