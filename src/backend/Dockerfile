# Stage 1: Backend (Python)
FROM python:3.8 AS backend

# Set the working directory to /app
WORKDIR /app

# Copy the requirements file first to leverage Docker layer caching (optimizes build)
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# Expose MongoDB port and MongoDB Exporter metrics port
EXPOSE 27017 9216

# Copy the rest of the working directory contents into the container at /app
COPY . .

# Run app.py when the container launches
ENTRYPOINT ["python", "back.py"]

