# Dockerfile
FROM apache/airflow:2.10.1-python3.11

USER root

# copy requirements
COPY requirements.txt /tmp/requirements.txt

# create prefix dir and give ownership before pip install to avoid permission issues
RUN mkdir -p /opt/airflow/.local \
    && chown -R airflow: /opt/airflow/.local \
    && python -m pip install --no-cache-dir -r /tmp/requirements.txt --prefix=/opt/airflow/.local \
    && rm /tmp/requirements.txt

ENV PATH=/opt/airflow/.local/bin:$PATH

# prepare directories (owned by airflow)
RUN mkdir -p /opt/airflow/dags /opt/airflow/plugins /opt/airflow/scripts \
    && chown -R airflow: /opt/airflow/dags /opt/airflow/plugins /opt/airflow/scripts

USER airflow

