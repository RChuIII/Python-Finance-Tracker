# Use the official Python image from Docker Hub
FROM python:3.12.4-bookworm

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container
COPY ./app /app

# Create an external volume for app
VOLUME ["/app"]

# Install the app requirements
RUN pip install -r /app/requirements.txt

# Make port 6900 to make the app available on the network
EXPOSE 6900

# Run the Streamlit app
CMD ["streamlit", "run", "--server.port=6900", "--server.address=0.0.0.0", "pyFinanceTrackerWebapp.py"]
