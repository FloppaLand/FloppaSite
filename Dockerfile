FROM python:3.10-slim-buster

WORKDIR /app

RUN apt-get -y update
RUN apt-get -y install libpq-dev gcc

COPY requirements.txt /app/requirements.txt
RUN pip3 install -r requirements.txt

COPY . /app

#CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]