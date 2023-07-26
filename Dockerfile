# Use the official python3.8 image as the base image
FROM python:3.8

# Set the working directory inside the container
WORKDIR /mini-blog-api

# Copy the requirements.txt file into the container
COPY requirements.txt .

# Create a virtual environment
RUN python -m venv .venv

# Activate the virtual environment
ENV PATH="/mini-blog-api/.venv/bin:$PATH"

# Upgrade pip in the virtual environment
RUN pip install --no-cache-dir --upgrade pip

# Install the required python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application directory into the container
COPY mini-blog-api/ .

# Expose the port on which FastAPI will run
EXPOSE 8000

# Serve application with uvicorn server.
ENTRYPOINT ["uvicorn", "mini_blog_api.main:app", "--host", "0.0.0.0", "--port", "8000", "--factory"]
