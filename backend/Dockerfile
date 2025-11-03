# Use official Python runtime as base image
FROM python:3.11-slim

# Set working directory in container
WORKDIR /app

# Use Chinese mirror for faster downloads (or your local mirror)
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

# Copy requirements first (for better caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of application code
COPY . .

# Expose the port FastAPI runs on
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "src.server:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]