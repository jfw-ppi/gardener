FROM python:3.12

# Set the working directory inside the container
WORKDIR /backend

# Copy the requirements file and install dependencies
COPY main.py .
COPY requirements.txt ./
COPY resources/ resources/
RUN pip install -r requirements.txt

# Copy the app directory into the container
COPY app/ ./app/

# Copy the main.py file into the container
COPY main.py ./

EXPOSE 8000

# Command to run the application
CMD ["python", "main.py"]
