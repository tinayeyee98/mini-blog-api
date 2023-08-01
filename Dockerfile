# Use the official python3.8 image as the base image
FROM python:3.8

# Set the working directory inside the container
WORKDIR /mini-blog-api

# Copy mini-blog application into the container
COPY . .

# Create a virtual environment
RUN python -m venv .venv

# Activate the virtual environment
ENV PATH="/mini-blog-api/.venv/bin:$PATH"

# Upgrade pip in the virtual environment
RUN pip install --no-cache-dir --upgrade pip

# Install the required python packages
RUN pip install .

# Expose the port on which FastAPI will run
EXPOSE 8000

# Serve application with uvicorn server.
ENTRYPOINT ["uvicorn", "mini_blog_api.main:create_app", "--host", "0.0.0.0", "--port", "8000", "--factory"]
