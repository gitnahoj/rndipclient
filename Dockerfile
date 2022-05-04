FROM python:3

WORKDIR /app

ADD ./code /app
RUN pip install requests
RUN pip install psutil
RUN pip install urllib3==1.25.11
RUN pip install PySocks

CMD [ "python", "main.py", "http://v562757.macloud.host", "ttt" ]
