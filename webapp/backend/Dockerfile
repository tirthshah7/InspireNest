# InspireNest Backend Dockerfile

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY . .

# Copy nesting engine (from parent directory)
COPY ../../src /app/engine_src

# Add engine to Python path
ENV PYTHONPATH="/app/engine_src:${PYTHONPATH}"

# Expose port
EXPOSE 8000

# Run server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

