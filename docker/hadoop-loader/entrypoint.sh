#!/bin/bash

# Wait for namenode to be ready (naive check)
echo "Waiting for namenode..."
until hdfs dfs -ls /; do
  echo "Namenode not ready, retrying..."
  sleep 5
done

echo "Namenode is ready!"

# Extract data
echo "Extracting data from SQLite..."
python3 extract_data.py

if [ $? -ne 0 ]; then
    echo "Data extraction failed!"
    exit 1
fi

# Prepare HDFS directories
echo "Preparing HDFS directories..."
hdfs dfs -mkdir -p /input
hdfs dfs -mkdir -p /output
# Clean previous runs
hdfs dfs -rm -r /output/* > /dev/null 2>&1
hdfs dfs -rm /input/matches.csv > /dev/null 2>&1

# Upload data
echo "Uploading input data..."
hdfs dfs -put matches.csv /input/

# Find Hadoop Streaming JAR
HADOOP_STREAMING_JAR=$(find $HADOOP_HOME -name "hadoop-streaming*.jar" | head -n 1)
echo "Using Hadoop Streaming JAR: $HADOOP_STREAMING_JAR"

# Run MapReduce Job
echo "Starting MapReduce Job..."
hadoop jar $HADOOP_STREAMING_JAR \
    -mapper "python3 mapper.py" \
    -reducer "python3 reducer.py" \
    -input /input/matches.csv \
    -output /output/match_stats \
    -file mapper.py \
    -file reducer.py

if [ $? -eq 0 ]; then
    echo "MapReduce Job Completed Successfully!"
    # List output
    hdfs dfs -ls /output/match_stats
    hdfs dfs -cat /output/match_stats/part-00000 | head -n 5
    
    # Keep container running for inspection, or exit?
    # We'll keep it running idle so we can exec into it if needed
    echo "Job done. Container staying alive."
    tail -f /dev/null
else
    echo "MapReduce Job Failed!"
    exit 1
fi
