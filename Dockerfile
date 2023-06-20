# Specify the base image
FROM python:alpine3.17

# Set the working directory
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy the app files into the container
COPY . .

# Run the app
CMD [ "python", "bot.py" ]