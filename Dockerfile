FROM python:3.6

WORKDIR /app
COPY . /app
EXPOSE 8080
RUN pip3 install -U pipenv && pipenv install --system --deploy

CMD ["python3","main.py"]
