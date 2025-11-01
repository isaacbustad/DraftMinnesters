# DraftMinnesters

roof of Concept: Draft Ministers Platform
1. Overview
Draft Ministers is a platform to demonstrate accurate match win probability predictions for fans and analysts. Fans can then place informed bets on upcoming matches informed by our platform. It uses Python, Kafka, MySQL, and Kaggle datasets on Ubuntu virtualization to validate 70% prediction accuracy.

2. Objectives
Prototype an application with a web browser user interface for desktop computers for EPL 2025-26 match win probability predictions.
Achieve 70% prediction accuracy using a simplified ML model.
Showcase interactive visualizations for a comprehensive dashboard.
Validate real-time updates and historical analysis (2008-2016 subset).

3. Requirements
These define the specific capabilities the system must possess to meet the use case (Fran placing a bet).
3.1 Match Selection and Display

R-01: Upcoming Match Browsing: The user interface (UI) must allow fans to easily browse and select matches from the target league (EPL 2025-2026 subset).

R-02: Prediction Presentation: Upon selecting a match, the system must immediately display the calculated match win probability for each team, represented as a percentage and conceptual betting odds.

3.2 Data and Statistical Insights
R-03: Comprehensive Team Statistics: The system must retrieve and display key statistical data supporting the prediction, specifically:
Head-to-Head Records (past outcomes between the two teams).
Key Player Statistics relevant to the current match.
Coach Performance Metrics.

3.3 Data Pipeline and Model
R-05: Data Ingestion and Processing: The platform must ingest the Kaggle historical data (2008-2016 subset) via an Kafka and store structured data in a MySQL database.
R-06: Model Training and Validation: The machine learning model (trained on the 2016-2020 dataset) must be integrated to generate predictions and provide a verifiable backtest report confirming the 70% accuracy goal.

3.4 Performance and Reliability
R-07: Real-Time Data Flow: The architecture must utilize Kafka to support the ingestion and processing of data, enabling near-real-time updates necessary for any future scaling.
R-08: Predictability: The model and platform components must demonstrate the capacity to reliably achieve the 70% accuracy requirement.

3.5 Technical and Operational
R-09: Scalability Focus: The PoC must be containerized using Docker on Ubuntu to ensure the deployment is scalable and cloud-ready, despite the initial physical resource limits.
R-10: Infrastructure Constraint: The entire development and deployment environment is constrained to an 8GB Ubuntu VM.
R-11: Development Stack: The solution must utilize the defined stack: Python (FastAPI/Flask), SciKitLearn/SciPy, Kafka, and MySQL.

4. Project Constraints and Deliverables
Constraints
Scope: Limited to EPL 2025-26 matches and the 2008-2016 Kaggle dataset subset.
Resources: 4 dedicated developers and one 8GB Ubuntu VM.
Timeline: Strict 6-week development period.

5. Pass System

Lord:
Price: free tier to pass system
Adds: Targeted ads before prediction feedback
Limitations: Users can only use the prediction feature 5 times with limited team selection. Sale of non-PPI Data

Duke:
Price: First level paid tier
Adds: Minimal adds before prediction feedback
Limitations: none

Minister:
Price: Premium paid service subscription
Adds: none
Limitations: none.

6. Key Deliverables
Dockerized PoC Application: A fully functional, containerized web application deployed on the VM.

7. Use Case:
Visit: A fan named Fran desires to place a bet on a Soccer team.
Select: Fran visits Draft Ministers Website and selects a match they wish to place a bet on.
Analyze: Fran can view a combination of our predictions and statistics to inform her bet.
Place: Fran places a bet on a team based on the predicted winner or statistics displayed.
Win Big!!!

