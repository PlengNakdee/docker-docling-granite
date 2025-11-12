FROM python:3.12-slim

WORKDIR /app

# Install system dependencies needed for Docling
RUN apt-get update && apt-get install -y \
  build-essential \
  libgl1 \
  libglib2.0-0 \
  libgomp1 \
  poppler-utils \
  && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir \
  docling \
  fastapi \
  uvicorn[standard] \
  python-multipart \
  pillow

# Copy your application
COPY app.py .

# Expose port
EXPOSE 8000

# Run the application with Uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]