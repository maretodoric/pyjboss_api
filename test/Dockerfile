FROM python:3.10

COPY jdk-8u251-linux-x64.tar.gz /
COPY wildfly-10.1.0.Final.tar.gz /
COPY wrapper.sh /
COPY pyjboss.py /

RUN tar -xvf /jdk-8u251-linux-x64.tar.gz -C /opt && \
    rm -rf /jdk-8u251-linux-x64.tar.gz && \
    for f in /opt/jdk1.8.0_251/bin/*; do ln -s $f /usr/bin/$(basename $f); done && \
    tar -xvf /wildfly-10.1.0.Final.tar.gz -C /opt && \
    rm -rf /wildfly-10.1.0.Final.tar.gz

ENV PYTHONUNBUFFERED=x
ENTRYPOINT [ "/wrapper.sh" ]