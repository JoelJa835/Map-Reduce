FROM python:3.11.2 as build


WORKDIR /manager_service


COPY . .


RUN pip install --no-cache-dir -r src/requirements.txt

EXPOSE 8081

ENTRYPOINT [ "python", "src/app.py" ]