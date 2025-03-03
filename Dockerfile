FROM python:3.8

WORKDIR /api

COPY requirements.txt /api
COPY api.py /api

RUN pip install -r requirements.txt

EXPOSE 5000

CMD ["python", "api.py"]