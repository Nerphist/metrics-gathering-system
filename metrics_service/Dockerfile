FROM python:3.8
WORKDIR /usr/src/app
ADD requirements.txt ./
RUN pip install -r requirements.txt
ADD . /usr/src/app
EXPOSE 8002
CMD python update_db.py && uvicorn main:app --host 0.0.0.0 --port 8002