# mini-blog-api
Back-end server for a mini-blog application

## Getting started

## Prequisities

`mini-blog-api` requires
- python 3.8+
- mongodb
- poetry (optional)

## Deployment with Docker

### Build and deploy the application
```python
# Build the docker image
docker-compose build

# Deploy the application
docker-compose up -d
```

### Access the application
```
http://0.0.0.0:8000
```

### Update the application
if you need to update the application or configuration, follow these steps
```shell
# Stop the current stack
docker-compose down

# Make necessary changes

# Rebuild and deploy
docker-compose build
docker-compose up -d
```

## Deployment with virtual environment

make sure you have already copied ".env" file for configs.

```python
# Create python virtual environment
python3.8 -m venv .venv

# Activate the environment
source .venv/bin/activate

# Upgrade pip to keep python package management system up to date
python -m pip install --upgrade pip

# This will install all required packages from pyproject.toml
python -m pip install .
(or)

# Otherwise, we can install from requirements.txt
python -m pip install -r requirements.txt 
```

## Run

Run Mini-Blog-API application with ASGI server

```shell
# Run the command manually
uvicorn mini_blog_api.main:create_app --host 0.0.0.0 --port 8000 --factory

(or)

# Otherwise, we can run using automation shell scripts fom scripts folder
. ./scripts/server
```

## Documentation

Project documentation and [API schema][openapi.yaml] are also available as HTML docs.

The HTML documentation can be accessed at http://0.0.0.0:8000/docs

