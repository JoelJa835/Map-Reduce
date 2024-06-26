FROM python:3.11.2 as build

ENV MANAGER_SERVICE_URL="http://manager-service:8081"


WORKDIR /worker_service


COPY . .


RUN pip install --no-cache-dir -r src/requirements.txt


ENTRYPOINT [ "python", "src/main.py" ]