FROM python:3.7.15-slim


WORKDIR /ui_service


COPY . .


RUN pip install -r src/requirements.txt


ENTRYPOINT [ "python", "src/cli.py" ]

