FROM python:3.11.2-slim


WORKDIR /ui_service


COPY . .


RUN pip install --no-cache-dir -r src/requirements.txt


ENTRYPOINT [ "python", "src/app.py" ]

