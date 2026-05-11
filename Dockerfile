# Base image
FROM python:3.12-slim

# Work directory inside container
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Flask port
EXPOSE 5000

# Run app
CMD ["python", "app.py"]