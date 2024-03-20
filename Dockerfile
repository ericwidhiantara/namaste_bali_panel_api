# Use a base image
FROM python:3.9

# Set the working directory in the container
WORKDIR /app

# Create a directory for logs
RUN mkdir logs

# Copy the requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the workspace files to the container
COPY . .

# Run the command to start your application
CMD [ "python", "main.py" ]
