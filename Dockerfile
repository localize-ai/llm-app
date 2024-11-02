# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the pyproject.toml and poetry.lock files to the container
COPY pyproject.toml poetry.lock ./

# Install Poetry
RUN pip install poetry

# Install the dependencies
RUN poetry install --no-root

# Copy the rest of the application code to the container
COPY . .

# Expose the port the app runs on
EXPOSE 8080

# Run the application
CMD ["python", "app/main.py"]