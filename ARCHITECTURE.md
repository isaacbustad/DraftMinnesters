# Draft Ministers Platform Architecture

## Executive Summary
Draft Ministers is a state-of-the-art soccer match prediction platform designed to deliver high-accuracy win probability forecasts. By integrating advanced machine learning with a robust, heterogeneous data architecture, the platform provides actionable insights for fans and analysts. This document outlines the architectural decisions that enable scalable data processing, real-time event streaming, and reliable storage.

## Value Creation Story
In the competitive landscape of sports analytics, speed and accuracy are paramount. Traditional systems often suffer from data latency and siloed storage. Draft Ministers addresses this by:
1.  **Unifying Data Streams**: Ingesting real-time match data via Kafka ensures that predictions are based on the latest events.
2.  **Scalable Storage**: Utilizing Cassandra for high-velocity write operations allows us to capture granular match details without performance bottlenecks.
3.  **Historical Analysis**: Leveraging Hadoop for batch processing enabling deep learning on years of historical match data to refine our DMR (Draft Minister Rating) algorithms.
4.  **User-Centric Delivery**: A responsive Flask application delivers these insights instantly to users through an intuitive interface.

## Platform Architecture

The platform is containerized using Docker, orchestrating the following components:

### 1. Application Layer (Flask)
-   **Role**: Serves the web interface and API endpoints.
-   **Function**: Orchestrates data retrieval from the heterogeneous database system and presents it to the user.
-   **Key Components**:
    -   `routes/`: Modular endpoints for matches, admin, and user data.
    -   `machine_learning/`: Real-time inference engine.

### 2. Event Streaming (Kafka)
-   **Role**: Real-time data ingestion pipeline.
-   **Function**: Decouples data producers (external APIs) from consumers (storage and analytics).
-   **Flow**: External API -> Kafka Producer -> Kafka Broker -> Consumers (Hadoop/Cassandra).

### 3. Heterogeneous Database System
The platform employs a polyglot persistence strategy:
-   **SQLite/MySQL**: Relational data for user profiles, configuration, and structured match schedules.
-   **Cassandra (NoSQL)**: High-availability storage for massive volumes of match events and player statistics. Optimized for write-heavy workloads.
-   **Hadoop (HDFS)**: Data lake for storing raw unstructured data and historical archives for batch processing and model retraining.

### 4. Machine Learning Engine
-   **Role**: Predictive analytics.
-   **Function**: Calculates Draft Minister Ratings (DMR) and win probabilities.
-   **Integration**: Fetches historical data from HDFS/SQL, trains models, and serves predictions via the Flask app.

## Data Flow Diagram

```mermaid
graph TD
    User[User] -->|HTTP Request| Flask[Flask Web App]
    
    subgraph "Data Ingestion"
        API[Football API] -->|JSON| Kafka[Kafka Cluster]
    end
    
    subgraph "Storage Layer"
        Kafka -->|Stream| Cassandra[Cassandra (Real-time DB)]
        Kafka -->|Batch| Hadoop[Hadoop HDFS (Data Lake)]
        Flask <-->|Read/Write| SQL[SQLite/MySQL (Relational DB)]
    end
    
    subgraph "Analytics"
        Hadoop -->|Training Data| ML[ML Engine]
        Cassandra -->|Recent Stats| ML
        ML -->|Predictions| Flask
    end
```

## Stakeholders
-   **Upstream**: Data Providers (API-Sports), System Administrators.
-   **Downstream**: End Users (Fans, Bettors), Data Analysts, Internal Auditors.

## Deployment
The entire stack is defined in `docker-compose.yml`, ensuring consistent deployment across development, testing, and production environments on Ubuntu systems.
