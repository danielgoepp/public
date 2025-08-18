FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy script
COPY backup_cpu_alert_silence.py .

# Make script executable
RUN chmod +x backup_cpu_alert_silence.py

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Default command runs the silence script for 15 minutes
CMD ["python3", "backup_cpu_alert_silence.py", "15"]