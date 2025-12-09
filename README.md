# Draft Ministers - Soccer Match Prediction Platform
<img width="2958" height="1616" alt="image" src="https://github.com/user-attachments/assets/692f3182-b5eb-4eb6-89c3-ab0672183275" />

<img width="2896" height="1498" alt="image" src="https://github.com/user-attachments/assets/875098ac-bce5-4bef-bb11-cb04e3b4f88c" />

<img width="2960" height="1582" alt="image" src="https://github.com/user-attachments/assets/b1743859-42ab-4f5d-b50f-ffdf7b101869" />

## Overview

Draft Ministers is a Flask-based web application that provides accurate match win probability predictions for soccer fans and analysts. The platform uses machine learning models to calculate team ratings (DMR - Draft Minister Rating) and predict match outcomes, helping users make informed betting decisions.

**Key Technologies:**
- **Backend**: Python 3.x, Flask
- **Database**: MySQL (Containerized)
- **Big Data & Streaming**: Kafka, Cassandra, Hadoop (HDFS)
- **Containerization**: Docker & Docker Compose
- **Machine Learning**: scikit-learn, pandas, numpy
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Data Source**: API-Sports.io Football API, Kaggle datasets

---

## Features

### Core Functionality
- **Match Predictions**: Real-time win probability calculations for upcoming matches
- **Team Ratings**: DMR (Draft Minister Rating) system for team strength assessment
- **Match Browsing**: Browse upcoming, past, and filtered matches
- **Interactive Overlay**: Detailed match information with team statistics
- **Star System**: Save favorite matches for quick access
- **Admin Dashboard**: Manage ML model runs and view team DMR ratings

### User Interface
- **Modern Design**: Clean, responsive interface with glassmorphism effects
- **Match Cards**: Visual cards displaying team logos, win percentages, and match details
- **Tabbed Navigation**: Organized views for Upcoming, Past, Most Likely to Win/Lose, and Starred matches
- **Filtering System**: Filter matches by home team, away team, date, and win chance percentage
- **Swiper Carousel**: Interactive banner showcasing featured matches
- **Match Overlay**: Detailed modal view with team statistics and probability visualization

---

## Project Structure

```
DraftMinnesters/
├── app.py                      # Main Flask application entry point
├── Dockerfile                  # Docker build definition
├── docker-compose.yml          # Service orchestration (Flask, MySQL, Kafka, etc.)
├── entrypoint.sh               # Container startup script (auto-init DB)
├── requirements.txt            # Python dependencies
├── migrate_db.py               # Script to migrate data from SQLite to MySQL
│
├── routes/                     # Flask blueprints (modular routes)
│   ├── __init__.py
│   ├── matches.py             # Match data endpoints and logic
│   ├── admin.py               # Admin dashboard and ML integration
│   ├── user.py                # User profile routes
│   └── index.py               # Index page utilities
│
├── templates/                  # Jinja2 HTML templates
│   ├── index.html             # Main match browsing page
│   ├── admin.html             # Admin dashboard
│   └── profile.html           # User profile page
│
├── static/                     # Static assets
│   ├── css/
│   │   ├── styles.css         # Main application styles
│   │   ├── overlaystyles.css  # Overlay modal styles
│   │   └── theme.css          # Theme variables
│   ├── js/
│   │   ├── nav.js             # Navigation functionality
│   │   └── overlay.js         # Match overlay functionality
│   ├── images/                # Team logos, banners, icons
│   └── fonts/                  # Custom fonts (Libre Baskerville)
│
├── machine_learning/            # ML model and DMR calculations
│   ├── machine_learning.py    # DMR calculation module
│   ├── football_database.sqlite # Historical match data (for ML training)
│   └── *.ipynb                # Jupyter notebooks for analysis
│
├── json_response/              # Local JSON data (fallback)
│   ├── teams_response.json
│   └── fixtures_response.json
│
└── logs/                       # Application logs
    └── app.log
```

---

## Installation & Setup

### Prerequisites
- **Docker Desktop** (or Docker Engine + Docker Compose)
- **Git**

### Step 1: Clone the Repository
```bash
git clone <repository-url>
cd DraftMinnesters
```

### Step 2: Build and Run with Docker
The entire application stack (Flask, MySQL, Kafka, Cassandra, Hadoop) is containerized.

```bash
docker-compose up -d --build
```


---

## Architecture

The platform has been modernized with a robust data architecture:

1.  **Flask App**: Serves the frontend. Reads "live" banner/match data from the **Shared Volume** and historical data from **MySQL**.
2.  **MySQL**: Primary relational database for user data and historical fixtures.
3.  **Kafka**:
    -   **Producer**: Simulates live events from `draft_ministers.db`.
    -   **Consumer**: Downloads content to **Shared Volume** and **Cassandra**.
4.  **Cassandra**: Stores high-velocity team banner associations.
5.  **Hadoop (HDFS)**: Distributed file system for large-scale historical data.

---

## Troubleshooting

### Common Issues

**Database Connection Errors**:
-   The application waits for MySQL to be ready on startup. If it fails, check logs: `docker-compose logs flask-app`.
-   Ensure the `mysql` container is running: `docker-compose ps`.

**Permission Denied (entrypoint.sh)**:
-   If you see "permission denied" for `entrypoint.sh`, ensure your `Dockerfile` uses `ENTRYPOINT ["/bin/bash", "/app/entrypoint.sh"]`.

**Port Conflicts**:
-   Ensure ports 5000 (Flask), 3306 (MySQL), 9092 (Kafka), 9042 (Cassandra), and 9870 (Hadoop) are free on your host machine.

---

## Future Enhancements

-   User authentication and accounts
-   Real-time match updates via WebSockets
-   Advanced statistics and analytics
-   Betting integration
-   Mobile app version
-   CI/CD pipeline
-   API rate limiting
-   Caching layer (Redis)

---

## License

[Specify your license here]

## Contributors

[Add contributor information]

---

## Contact & Support

For issues, questions, or contributions, please [create an issue / contact maintainers].
