FROM python:3.6-buster

RUN pip install numpy scipy cython astropy

WORKDIR /code
ADD src src

WORKDIR /code/src/python_modules/plato_wp36/
RUN pip install plato_wp36

