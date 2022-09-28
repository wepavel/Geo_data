FROM osgeo/gdal:ubuntu-small-latest

COPY requirements.txt \
     scripts \
     ./app/

RUN apt update -y && apt -y install python3-pip

RUN pip3 install -r /app/requirements.txt

WORKDIR "/app"

CMD ["python3.10", "/app/main_flask.py"]
