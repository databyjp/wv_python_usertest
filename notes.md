### Setup

Python 3.10.12
Installed client with:
`pip install git+https://github.com/weaviate/weaviate-python-client.git@schema_dataclass`
`pip install git+https://github.com/weaviate/weaviate-python-client.git@pydantic_experiment`
`pip install git+https://github.com/weaviate/weaviate-python-client.git@addition_props`


### Notes

2023-06-23
- It might need class-level ModuleConfig setting added (e.g. for setting module models)
- X-references missing at this point. It could accept the target class directly?