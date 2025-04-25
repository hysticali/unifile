FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy only necessary files
COPY pyproject.toml setup.py README.md /app/
COPY src /app/src

# Install the package
RUN pip install .

# Default entrypoint for CLI usage (can override with docker run)
ENTRYPOINT ["unifile"]