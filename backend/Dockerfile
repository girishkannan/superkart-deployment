# Lightweight Python base image
FROM python:3.10-slim

# Working directory inside the container
WORKDIR /app

# Installing the dependencies first so that Docker can cache this layer
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copying the application code and the serialized model
COPY app.py .
COPY superkart_model.joblib .

# The Flask API listens on port 7860
EXPOSE 7860

# Starting the API
CMD ["python", "app.py"]
