# Lightweight Python base image
FROM python:3.10-slim

# Working directory inside the container
WORKDIR /app

# Installing the dependencies first so that Docker can cache this layer
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copying the Streamlit application
COPY app.py .

# Streamlit listens on port 8501
EXPOSE 8501

# Starting the UI. --server.address=0.0.0.0 makes it reachable from outside the container
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
