# FROM python:3.9-slim

# # Set working directory
# WORKDIR /app

# # Copy project files
# COPY . /app

# # Install dependencies
# RUN pip install --no-cache-dir --upgrade pip \
#  && pip install --no-cache-dir -r requirements.txt

# # Expose FastAPI's default port
# EXPOSE 8000

# # Run the FastAPI app using Uvicorn
# CMD ["python", "main.py"]



# Start from official Python image
FROM python:3.10-slim


# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y build-essential

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app source code
COPY . .

# Expose the port FastAPI will run on (App Runner listens on 8080)
EXPOSE 8080

# Start FastAPI using uvicorn (binding to 0.0.0.0 and port 8080)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
