FROM python:3.10.4-slim-bullseye as build-python
  
WORKDIR /server

COPY ./server/requirements /requirements
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /wheels \
  -r /requirements/test.txt

FROM python:3.10.4-slim-bullseye
ENV PYTHONUNBUFFERED 1
WORKDIR /server
   
RUN addgroup --system server \
  && adduser --system --ingroup server server
   
# copy pre-build artifacts from previous biuld stages
COPY --from=build-python /wheels /wheels
   
RUN pip install --no-cache /wheels/* \
  && rm -rf /wheels \
  && rm -rf /root/.cache/pip/*

COPY --chown=server:server ./server /server

USER server
CMD python -m unittest discover 
