FROM python:3.10.12-bullseye

WORKDIR /app

# copy the requirements file used for dependencies
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

# CMD [ "python3", "-m" , "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80" ]
ENTRYPOINT ["python3", "main.py"]
