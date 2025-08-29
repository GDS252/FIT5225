FROM public.ecr.aws/lambda/python:3.9
RUN yum install -y zip
RUN mkdir -p /opt/python
WORKDIR /opt/python
COPY requirements-numpy.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements-numpy.txt --target .