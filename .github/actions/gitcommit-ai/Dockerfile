FROM python:3.11-slim

LABEL maintainer="GitCommit AI Contributors"
LABEL description="GitHub Action for AI-powered commit message validation"

# Install git
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy project files
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -e .

# Copy entrypoint script
COPY .github/actions/gitcommit-ai/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Set entrypoint
ENTRYPOINT ["/entrypoint.sh"]
