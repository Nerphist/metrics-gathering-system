FROM python:3.8
WORKDIR /usr/src/app
ADD requirements.txt ./
RUN pip install -r requirements.txt
ADD . /usr/src/app
EXPOSE 8001
CMD /bin/bash -c "sleep 5; python manage.py migrate && python manage.py runserver  0.0.0.0:8001 --noreload"