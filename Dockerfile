# Stage 1: Build environment
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better layer caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy entire project
COPY . .

# Expose Streamlit port
EXPOSE 8501

# Set working directory to Bedrock-chatbot (where app.py is)
WORKDIR /app/Bedrock-chatbot

# Healthcheck
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Run Streamlit app with server config
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501", "--logger.level=info"]
