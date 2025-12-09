FROM ubuntu:20.04

# Avoid prompts from apt
ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies
RUN apt-get update && apt-get install -y \
    openjdk-8-jdk \
    python3 \
    python3-pip \
    wget \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Install Python libraries
RUN pip3 install hdfs pandas

# Install Hadoop
ENV HADOOP_VERSION=3.2.1
RUN wget https://archive.apache.org/dist/hadoop/common/hadoop-$HADOOP_VERSION/hadoop-$HADOOP_VERSION.tar.gz \
    && tar -xzvf hadoop-$HADOOP_VERSION.tar.gz -C /opt/ \
    && rm hadoop-$HADOOP_VERSION.tar.gz \
    && mv /opt/hadoop-$HADOOP_VERSION /opt/hadoop

# Set environment variables
ENV JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
ENV HADOOP_HOME=/opt/hadoop
ENV PATH=$PATH:$HADOOP_HOME/bin:$HADOOP_HOME/sbin

WORKDIR /app

# Copy scripts
COPY . /app/
RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/bin/bash", "/app/entrypoint.sh"]
