# Use Python 3.11 slim image as base
# 
# ⚠️ IMPORTANT NOTE: The tools demonstrated are placeholder implementations
# designed to showcase the ReAct agent's capabilities. They serve as a 
# foundation that can be easily extended with any DevOps tools you need 
# for your specific environment.
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Create a directory for traces if it doesn't exist
RUN mkdir -p traces

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Expose port if needed (for Flask components)
EXPOSE 5000

# Run the main application
CMD ["python", "run_tool_calling_react_agent_pipeline.py"] 