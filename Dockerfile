FROM python:3.9.7

RUN mkdir cse312
RUN cd cse312
WORKDIR /cse312

COPY . .

RUN pip install pymongo
RUN pip install bcrypt

EXPOSE 8080

ADD https://github.com/ufoscout/docker-compose-wait/releases/download/2.2.1/wait /wait
RUN chmod +x /wait

CMD /wait && python server.py