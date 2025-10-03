FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user for security
RUN useradd -m -u 1000 botuser && chown -R botuser:botuser /app
USER botuser

# Force Supabase environment variables
ENV CONTAINER_DEPLOYMENT=true
ENV FORCE_SUPABASE_REST=true
ENV DISABLE_SQLITE_FALLBACK=true
ENV SUPABASE_PRIORITY=high

# Run with Supabase priority
CMD ["python", "main_railway_buttons_supabase.py"]