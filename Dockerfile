FROM python:3.8-buster


WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY . .
ADD . /code/
CMD [ "taskset", "--cpu-list" , "0-3", "python3", "server.py"]