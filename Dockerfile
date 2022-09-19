FROM ubuntu:20.04

EXPOSE 1060

RUN apt-get update && apt-get upgrade -y && apt-get install -y nginx curl && rm -rf /var/lib/pt/lists/*

# ADD . /app

RUN apt -y install mc

RUN yes | apt install software-properties-common

RUN add-apt-repository ppa:deadsnakes/ppa

RUN apt-get update

RUN yes | apt-get install python3.9

RUN yes | apt-get install python3.9-dev 

RUN yes | apt-get install python3-pip

RUN mkdir /app

RUN apt install python3.9-venv

RUN python3.9 -m venv --system-site-packages /app/venv

COPY ./requirements.txt /app/


ENV VIRTUAL_ENV /app/venv
ENV PATH /app/venv/bin:$PATH

# RUN /app/venv/bin/python3.9 -m pip install --upgrade pip

COPY main_flask.py /app/

COPY model.py /app/

COPY conf.ini /app/

# Install GDAL dependencies
# RUN apt-get install -y libgdal-dev g++ --no-install-recommends && apt-get clean -y
RUN apt update && apt-get install -y gdal-bin libgdal-dev g++ --no-install-recommends\
 && apt-get clean -y && rm -rf /var/lib/apt/lists/*


# Update C env vars so compiler can find gdal
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal

RUN pip3 install -r /app/requirements.txt


RUN mv /usr/lib/python3/dist-packages/osgeo/_gdal.cpython-38-aarch64-linux-gnu.so\
 /usr/lib/python3/dist-packages/osgeo/_gdal.so
RUN mv /usr/lib/python3/dist-packages/osgeo/_gdal_array.cpython-38-aarch64-linux-gnu.so\
 /usr/lib/python3/dist-packages/osgeo/_gdal_array.so
RUN mv /usr/lib/python3/dist-packages/osgeo/_gdalconst.cpython-38-aarch64-linux-gnu.so\
 /usr/lib/python3/dist-packages/osgeo/_gdalconst.so
RUN mv /usr/lib/python3/dist-packages/osgeo/_gnm.cpython-38-aarch64-linux-gnu.so\
 /usr/lib/python3/dist-packages/osgeo/_gnm.so
RUN mv /usr/lib/python3/dist-packages/osgeo/_ogr.cpython-38-aarch64-linux-gnu.so\
 /usr/lib/python3/dist-packages/osgeo/_ogr.so
RUN mv /usr/lib/python3/dist-packages/osgeo/_osr.cpython-38-aarch64-linux-gnu.so\
 /usr/lib/python3/dist-packages/osgeo/_osr.so

 #RUN cd /app/

 WORKDIR "/app"

CMD ["python3.9", "/app/main_flask.py"]