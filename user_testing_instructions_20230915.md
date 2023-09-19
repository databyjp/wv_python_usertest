# Early user testing for the Weaviate 'collections' client

Welcome!

We have been working on a new (and hopefully improved) API for our Python client. We are excited for you to try it out and provide feedback for us.

## Overview

If you have feedback about any part of this, we want to know. Also, you will see sections marked **Please provide feedback from this section**. These are areas in which we are particularly interested. 

Please let us know **on a 1-5 scale, where 5 is awesome, and 1 is bad**.

Did you find the section / code to be:
- An improvement or worse than before?
- Intuitive or unintuitive: 
    - Did you instinctively try something different to the defined syntax? 
    - Did you see how it's defined and think it should be something else? 
- Easy to use?

## Installation

We recommend you create a **new environment** (whether venv, or Conda/Mamba) for this, in a new project directory.

#### How to create a virtual environment with `venv`

Go to your project directory and run:

```shell
python -m venv .venv
```

(Depending on your setup, `python` might need to be `python3`)

Then activate it with:

```shell
source .venv/bin/activate
```

### Client installation

Once you are in your desired environment:

```shell
pip install -U "git+https://github.com/weaviate/weaviate-python-client.git@pydantic_experiment#egg=weaviate-client[GRPC]"
```
#### Start Weaviate

You will also need a pre-release version of Weaviate.

Save the below to `docker-compose.yml` in the project directory. Then, go to the directory and run `docker compose up -d`.

```yaml
---
version: '3.4'
services:
  weaviate:
    command:
    - --host
    - 0.0.0.0
    - --port
    - '8080'
    - --scheme
    - http
    image: semitechnologies/weaviate:preview-automatically-return-all-props-metadata-for-refs-07fce6f
    restart: on-failure:0
    ports:
     - "8080:8080"
     - "50051:50051"
    environment:
      QUERY_DEFAULTS_LIMIT: 25
      QUERY_MAXIMUM_RESULTS: 10000
      AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED: 'true'
      PERSISTENCE_DATA_PATH: '/var/lib/weaviate'
      DEFAULT_VECTORIZER_MODULE: 'text2vec-openai'
      ENABLE_MODULES: 'text2vec-contextionary,text2vec-openai,text2vec-cohere,text2vec-huggingface,text2vec-palm,generative-openai'
      CLUSTER_HOSTNAME: 'node1'
      CONTEXTIONARY_URL: contextionary:9999
      AUTOSCHEMA_ENABLED: 'false'
  contextionary:
    environment:
      OCCURRENCE_WEIGHT_LINEAR_FACTOR: 0.75
      EXTENSIONS_STORAGE_MODE: weaviate
      EXTENSIONS_STORAGE_ORIGIN: http://weaviate:8080
      NEIGHBOR_OCCURRENCE_IGNORE_PERCENTILE: 5
      ENABLE_COMPOUND_SPLITTING: 'false'
    image: semitechnologies/contextionary:en0.16.0-v1.2.1
    ports:
    - 9999:9999
...
```

You can check that the containers are up and available by running `docker ps` from the shell. This should show two Docker containers running - like: 

```shell
CONTAINER ID   IMAGE                                                                                        COMMAND                  CREATED          STATUS         PORTS                                              NAMES
4be7efdff229   semitechnologies/contextionary:en0.16.0-v1.2.1                                               "/contextionary-serv…"   10 seconds ago   Up 9 seconds   0.0.0.0:9999->9999/tcp                             try_new_wv_api_202306-contextionary-1
e90a63fe1e15   semitechnologies/weaviate:preview-automatically-return-all-props-metadata-for-refs-07fce6f   "/bin/weaviate --hos…"   10 seconds ago   Up 9 seconds   0.0.0.0:8080->8080/tcp, 0.0.0.0:50055->50051/tcp   try_new_wv_api_202306-weaviate-1
```

The `STATUS` should include `Up` and closely match the `CREATED` time.

#### Troubleshooting

If your gRPC port is not open, try remapping it to another port (it can be anything). For example, you can change it from 50051 to 50055 by editing:

```yaml
    ports:
     - "8080:8080"
     - "50051:50051"
```

To 

```yaml
    ports:
     - "8080:8080"
     - "50055:50051"
```

Note that this will require you to edit the gRPC port in the client for `grpc_port_experimental` below.

## Try out the client

We're good to go! Fire up your preferred way to edit / run Python code (Jupyter, VSCode, PyCharm, vim, whatever) and follow along. 

> #### Code examples to run
>
> You will see a comment **user_test.py** at the top of the code snippet where you are to to *run* or *try* it.


### Key ideas

We are calling this the `collections` client, because many of the data interactions will be at the collections (currently called `Class` in Weaviate) level. 

From here, we will call Weaviate `classes`  

This client also includes custom Python classes to provide assistance for building collection definitions, objects, performing searches, and so on. 

You can import them individually, like so:

```
from weaviate.weaviate_classes import Property, ConfigFactory, VectorizerFactory, DataObject
```

But you can import the whole set of classes like this.

```
import weaviate.weaviate_classes as wvc
```

This will let you use them as required like `wvc.Property(...)` and so on.

### Instantiation

Run the below to connect to Weaviate. Note that you need a `grpc` port specified. It should return `True`.

```python
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
```

> Expected output:
> 
> ```
> True
> ```

Run the below delete any existing classes, or in case you are re-running the same code:

```python
# user_test.py

for collection_name in ["TestArticle", "TestAuthor"]:
    client.collection.delete(collection_name)
```

> Expected output:
> 
> ```
> None
> ```

### Collection creation

#### Existing API 

The existing API uses a raw dictionary / JSON object to create classes, like so:

```python
# Old API example
collection_definition = {
    "class": "Article",
    "vectorizer": "text2vec-openai",
    "vectorIndexConfig": {
        "distance": "cosine"
    },
    "moduleConfig": {
        "generative-openai": {}
    },
    "properties": [
        {
            "name": "title",
            "dataType": ["text"]
        },
        {
            "name": "chunk_no",
            "dataType": ["int"]
        },
        {
            "name": "url",
            "dataType": ["text"],
            "tokenization": "field",
            "moduleConfig": {
                "text2vec-openai": {
                    "skip": True
                }
            }
        }
    ]
}

client.schema.create_class(collection_definition)
```

Now, collection creation looks like this 

```python
# New API example
articles = client.collection.create(
    name="TestArticle",
    properties=[
        wvc.Property(
            name="title",
            data_type=wvc.DataType.TEXT,
        ),
    ],
    vectorizer_config=wvc.VectorizerFactory.text2vec_openai(),
    replication_config=wvc.ConfigFactory.replication(factor=1), 
)
```

It uses Weaviate-specific classes to define properties (`wvc.Property`), specify vectorizers (`wvc.ConfigFactory`), and complex configuration options (`wvc.ConfigFactory`) and so on.

The below is a partially complete collection definition. Please see if you can edit the below based on the comments:

```python
# user_test.py
# Edit the following to create collection definitions
articles = client.collection.create(
    name="TestArticle",
    properties=[
        wvc.Property(
            name="title",
            data_type=wvc.DataType.TEXT,
        ),
        # Try creating a new property 'body', with the text datatype
        # Try creating a new property 'url', with the text datatype and field tokenization
    ],
    vectorizer_config=wvc.VectorizerFactory.text2vec_openai(),
    replication_config=wvc.ConfigFactory.replication(factor=1),
    # Try adding an inverted index config with property length 
)

authors = client.collection.create(
    name="TestAuthor",
    properties=[
        wvc.Property(
            name="name",
            data_type=wvc.DataType.TEXT,
        ),
        # Try creating a new property 'birth_year', with the int datatype
        # Try creating a new cross-reference 'wroteArticle', linking to `TestArticle` collection
    ],
    # Add a Contextionary vectorizer
)
```

Here is one that we created as an example. Did you end up with the same? 

**Please provide feedback from this section**

```python
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
            vectorizer_config=wvc.PropertyVectorizerConfig()
        ),
    ],
    vectorizer_config=wvc.VectorizerFactory.text2vec_openai(),
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
```

> Expected output:
> 
> ```
> True
> True
> ```

You can also create an object from existing collections in Weaviate like this:

```python
# user_test.py
articles = client.collection.get("TestArticle")
authors = client.collection.get("TestAuthor")
```

### Collection methods

You should now see code autocomplete suggestions for the `articles` / `authors` objects. Two key submodules are:

-  `data`: CRUD operations
-  `query`: Search operations (old GraphQL, now gRPC)

### CRUD operations

You can add objects with the `insert` method.

Run this to add an object to the `articles` collection:

```python
# user_test.py
my_first_obj = {
    "title": "Something something dark side",
    "body": "A long long time ago, in a galaxy far, far away...",
    "url": "http://www.starwars.com"
}

article_uuid = articles.data.insert(my_first_obj)
print(article_uuid)
```

And run this to add an object to the `authors` collection:

```python
# user_test.py
author_uuid = authors.data.insert(
    {
        "name": "G Lucas",
        "birth_year": 1944,
        "wroteArticle": wvc.ReferenceFactory.to(uuids=[article_uuid])
    }
)
```

#### Add objects (batch)

You can also add multiple objects at once. The new syntax allows you to pass a list of (wvc.DataObject) objects. 

```python
# user_test.py
articles_to_add = [
    wvc.DataObject(
        properties={
            "title": f"The best restaurants of {1980+i}:",
            "body": "1. McDonald's, 2. ...",
        },
    )
    for i in range(5)
]

response = articles.data.insert_many(articles_to_add)
print(response)
```

The `response` object contains the UUIDs of the created objects, and more.

> Expected output:
> 
> ```
> _BatchReturn(all_responses=[UUID('f5697fcf-29f0-4ea9-b93a-750e42de41f6'), UUID('9a324be2-c7e4-426f-ab8d-506b48100ef5'), UUID('9f563ee5-9f30-44b5-a3fd-4741f4dbc245'), UUID('e750323b-4937-469c-9026-da270187e09f'), UUID('307be462-0002-4a5c-a991-bc081e35d972')], uuids={0: UUID('f5697fcf-29f0-4ea9-b93a-750e42de41f6'), 1: UUID('9a324be2-c7e4-426f-ab8d-506b48100ef5'), 2: UUID('9f563ee5-9f30-44b5-a3fd-4741f4dbc245'), 3: UUID('e750323b-4937-469c-9026-da270187e09f'), 4: UUID('307be462-0002-4a5c-a991-bc081e35d972')}, errors={}, has_errors=False)
> ```

This is how we add some articles to 'authors', with a cross-reference to `articles`:

```python
# user_test.py
authors_to_add = [
    wvc.DataObject(
        properties={
            "name": f"Jim {i+1}",
            "birth_year": 1970 + i,
            "wroteArticle": wvc.ReferenceFactory.to(uuids=[article_uuid])
        },
        # vector=CUSTOM_VECTOR_HERE,
        # uuid=CUSTOM_UUID_HERE
    )
    for i in range(5)
]

authors.data.insert_many(authors_to_add)
```

> Expected output:
> 
> ```
> _BatchReturn(all_responses=[UUID('8c033488-c6d7-49c2-be1f-995af5bf08ff'), UUID('2ca8fa5c-5bec-4ad3-a591-b2d694d07987'), UUID('e771130e-a461-4124-9727-66c965f7221e'), UUID('6055c796-d187-4b27-baf1-aeee5cf8a4d6'), UUID('c6b776b0-026b-4ea0-a437-e8514475e89e')], uuids={0: UUID('8c033488-c6d7-49c2-be1f-995af5bf08ff'), 1: UUID('2ca8fa5c-5bec-4ad3-a591-b2d694d07987'), 2: UUID('e771130e-a461-4124-9727-66c965f7221e'), 3: UUID('6055c796-d187-4b27-baf1-aeee5cf8a4d6'), 4: UUID('c6b776b0-026b-4ea0-a437-e8514475e89e')}, errors={}, has_errors=False)
>```

Of course, you can still add custom vectors and UUIDs as shown above.

#### Errors

The client will now automatically capture errors. Try this example, where the `url` property is erroneously provided a numerical value for one of the inputs:   

```python
articles_to_add = [
    wvc.DataObject(
        properties={
            "title": f"The best restaurants of {1980+i}:",
            "body": "1. McDonald's, 2. ...",
            "url": str(i) if i != 2 else i
        },
    )
    for i in range(5)
]

response = articles.data.insert_many(articles_to_add)
print(response.errors)
```



> Expected output:
> 
> ```
> {2: Error(message="invalid text property 'url' on class 'TestArticle': not a string, but float64", code=None, original_uuid=None)}
> ```

```python
# user_test.py
authors_to_add = [
    wvc.DataObject(
        properties={
            "name": f"Jim {i+1}",
            "birth_year": 1970 + i,
            "wroteArticle": wvc.ReferenceFactory.to(uuids=[uuid])
        },
    )
    for i in range(10)
]

authors.data.insert_many(authors_to_add)
```

> **TRY THESE OUT**
> Try out methods for other functionalities, like `delete`.

### Queries

You can now get objects like this! 

```python
response = articles.query.get(limit=2)

print(response)
```

> Expected output:
> 
> ```
> _QueryReturn(objects=[_Object(properties={'title': 'The best restaurants of 1983:', 'body': "1. McDonald's, 2. ..."}, metadata=_MetadataReturn(uuid=UUID('01cf04d4-d066-4871-8a17-204356e5070e'), vector=None, creation_time_unix=1694795353140, last_update_time_unix=1694795353140, distance=None, certainty=None, score=0.0, explain_score='', is_consistent=False, generative=None)), _Object(properties={'title': 'The best restaurants of 1981:', 'body': "1. McDonald's, 2. ..."}, metadata=_MetadataReturn(uuid=UUID('045c11f8-f4c7-4b9c-b8f1-7755f975c593'), vector=None, creation_time_unix=1694795353140, last_update_time_unix=1694795353140, distance=None, certainty=None, score=0.0, explain_score='', is_consistent=False, generative=None))])
> ```

Notice how you don't have to specify the collection name (provided in the object), and properties to retrieve.

You can also specify these if you wish.

```python
response = articles.query.get(
    limit=2,
    return_properties=["title"],
    return_metadata=wvc.MetadataQuery(uuid=True)
)

print(response)
```

> Expected output:
> 
> ```
> _QueryReturn(objects=[_Object(properties={'title': 'The best restaurants of 1983:'}, metadata=_MetadataReturn(uuid=UUID('01cf04d4-d066-4871-8a17-204356e5070e'), vector=None, creation_time_unix=None, last_update_time_unix=None, distance=None, certainty=None, score=None, explain_score=None, is_consistent=False, generative=None)), _Object(properties={'title': 'The best restaurants of 1981:'}, metadata=_MetadataReturn(uuid=UUID('045c11f8-f4c7-4b9c-b8f1-7755f975c593'), vector=None, creation_time_unix=None, last_update_time_unix=None, distance=None, certainty=None, score=None, explain_score=None, is_consistent=False, generative=None))])
> ```

#### Filters

You can add filters like so, with a `Filter` object:

```python
response = authors.query.get(
  filters=wvc.Filter(path=["birth_year"]).greater_than_equal(1971)
)

for o in response.objects:
    print(o.properties["birth_year"])
```

> Expected output:
> 
> ```
> 1974.0
> 1971.0
> 1973.0
> 1972.0
> ```

#### Near text search

```python
response = articles.query.near_text(
    query="The dark side",
    certainty=0.75,
)

print(response)
```

