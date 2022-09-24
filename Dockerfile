FROM perrygeo/gdal-base:latest as builder

COPY requirements.txt .
RUN python -m pip install --no-binary fiona,shapely -r requirements.txt
RUN python -m pip install -r requirements.txt

FROM python:3.9-slim-buster as final

RUN apt-get update \
    && apt-get install --yes --no-install-recommends \
        libfreexl1 libxml2 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /usr/local /usr/local
RUN ldconfig

RUN mkdir /app
COPY . /app/

#
##RUN python3.9 -m pip install --no-binary fiona,rasterio,shapely -r /app/requirements.txt
##
#RUN #python3.9 -m pip install -r /app/requirements.txt
##



WORKDIR "/app"
#
CMD ["python3.9", "/app/main_flask.py"]