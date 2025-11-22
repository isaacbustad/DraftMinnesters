# Draft Ministers - Soccer Match Prediction Platform
<img width="2958" height="1616" alt="image" src="https://github.com/user-attachments/assets/692f3182-b5eb-4eb6-89c3-ab0672183275" />

<img width="2896" height="1498" alt="image" src="https://github.com/user-attachments/assets/875098ac-bce5-4bef-bb11-cb04e3b4f88c" />

<img width="2960" height="1582" alt="image" src="https://github.com/user-attachments/assets/b1743859-42ab-4f5d-b50f-ffdf7b101869" />



## Overview

Draft Ministers is a Flask-based web application that provides accurate match win probability predictions for soccer fans and analysts. The platform uses machine learning models to calculate team ratings (DMR - Draft Minister Rating) and predict match outcomes, helping users make informed betting decisions.

**Key Technologies:**
- **Backend**: Python 3.x, Flask
- **Database**: SQLite (with support for MySQL)
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
├── requirements.txt            # Python dependencies
├── draft_ministers.db         # SQLite database (created on first run)
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
│   ├── football_database.sqlite # Historical match data
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
- Python 3.8 or higher
- pip (Python package manager)
- SQLite3 (usually included with Python)

### Step 1: Clone the Repository
```bash
git clone <repository-url>
cd DraftMinnesters
```

### Step 2: Create Virtual Environment (Recommended)
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On Linux/Mac
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

**Note**: The `requirements.txt` may need updating. Core dependencies include:
- Flask
- requests
- sqlite3 (built-in)
- pandas
- numpy
- scikit-learn

### Step 4: Initialize Database
The database is automatically created on first run. The `init_db()` function in `app.py` will:
- Create SQLite database file (`draft_ministers.db`)
- Set up all required tables
- Initialize default configuration values

### Step 5: Run the Application
```bash
python app.py
```

The application will start on `http://0.0.0.0:5000` (accessible at `http://localhost:5000`)

---

## Configuration

### Database Configuration
- **Database File**: `draft_ministers.db` (SQLite)
- **Location**: Root directory
- **Auto-initialization**: Database and tables are created automatically on first run

### API Configuration
The application uses API-Sports.io for match data:
- **Base URL**: `https://v3.football.api-sports.io`
- **API Key**: Configured in `routes/matches.py`
- **Fallback**: Local JSON files in `json_response/` directory

### Logging
- **Log Directory**: `logs/`
- **Log File**: `logs/app.log`
- **Log Level**: DEBUG (configurable in `app.py`)

### Match Cutoff Date
- **Configuration Table**: `app_config`
- **Key**: `upcoming_match_cutoff_date`
- **Default**: `2023-12-31`
- **Purpose**: Distinguishes between upcoming and past matches

---

## Database Schema

### Tables

#### `soccer_teams`
Stores team information and DMR ratings.
```sql
- id (INTEGER PRIMARY KEY)
- name (TEXT UNIQUE)
- code (TEXT)
- country (TEXT)
- founded (INTEGER)
- national (INTEGER)
- logo (TEXT)
- venue_id, venue_name, venue_address, venue_city, venue_capacity, venue_surface, venue_image
- league (TEXT)
- dmr (REAL)  -- Draft Minister Rating
```

#### `soccer_fixtures`
Stores match/fixture data with predictions.
```sql
- fixture_id (INTEGER PRIMARY KEY)
- date, timestamp
- status_long, status_short
- home_team_id, away_team_id
- league_id, league_name, season, round
- venue_id, venue_name, venue_city
- referee
- home_goals, away_goals
- home_winner, away_winner
- raw_data (TEXT JSON)
- home_win_percentage (REAL)
- away_win_percentage (REAL)
- draw_percentage (REAL)
```

#### `soccer_players`
Stores player information (for future use).
```sql
- id (INTEGER PRIMARY KEY AUTOINCREMENT)
- name, position, age
- team_id (FOREIGN KEY)
```

#### `ml_run_history`
Tracks machine learning model execution history.
```sql
- id (INTEGER PRIMARY KEY AUTOINCREMENT)
- run_time (TEXT)
- status (TEXT)
- teams_updated (INTEGER)
```

#### `app_config`
Application configuration key-value store.
```sql
- key (TEXT PRIMARY KEY)
- value (TEXT)
```

---

## API Endpoints

### Main Routes

#### `GET /`
- **Description**: Home page with match listings
- **Returns**: Rendered `index.html` template
- **Features**: Displays upcoming matches, featured teams (winners/underdogs)

#### `GET /api/matches`
- **Description**: Fetch all match data (upcoming, past, predictions)
- **Returns**: JSON object with:
  ```json
  {
    "upcoming": [...],
    "past": [...],
    "most_likely_to_win": [...],
    "most_likely_to_lose": [...]
  }
  ```
- **Use Case**: Frontend JavaScript fetches match data for display

#### `POST /api/refresh-data`
- **Description**: Clear database and fetch fresh data from API
- **Returns**: JSON with `teams_count` and `fixtures_count`
- **Use Case**: Admin function to refresh match data

### Admin Routes

#### `GET /admin`
- **Description**: Admin dashboard
- **Returns**: Rendered `admin.html` template
- **Features**: 
  - View team DMR ratings
  - Trigger ML model runs
  - View ML run history

#### `POST /admin/run-ml`
- **Description**: Trigger machine learning model to calculate/update DMR ratings
- **Returns**: JSON status
- **Note**: Runs asynchronously in background thread

### User Routes

#### `GET /profile`
- **Description**: User profile page
- **Returns**: Rendered `profile.html` template
- **Features**: User statistics and portfolio (if implemented)

---

## Machine Learning Integration

### DMR (Draft Minister Rating) System

The application uses a machine learning-based rating system to assess team strength:

**Location**: `machine_learning/machine_learning.py`

**Key Functions**:
- `get_all_team_dmrs()`: Retrieves DMR ratings for all teams
- `get_team_dmrs(team_names)`: Get DMR for specific teams
- `_load_data_and_models()`: Loads trained ML models and historical data

**Model Details**:
- Uses scikit-learn (LogisticRegression, LinearRegression)
- Trained on historical match data (2008-2016 subset)
- Features include team performance metrics, match statistics
- Output: DMR rating (typically 30-60 range)

**Win Percentage Calculation**:
- Located in `routes/admin.py`: `calculate_win_percentages()`
- Uses DMR difference between teams
- Calculates home win, away win, and draw probabilities
- Accounts for home advantage and team strength differential

---

## Frontend Features

### Match Display System

**Match Cards**:
- Grid layout (responsive: 3 columns → 2 → 1 on smaller screens)
- Displays team logos, names, win percentages
- Badge indicators (Upcoming, Past, Likely Win, Likely Lose)
- Star button for favorites
- Click to view detailed overlay

**Filtering**:
- Filter by home team name
- Filter by away team name
- Filter by date
- Filter by minimum win chance percentage
- Real-time filtering as you type

**Tabs**:
1. **Upcoming Matches**: Future fixtures
2. **Past Matches**: Completed matches (sorted by most recent)
3. **Most Likely to Win**: Teams with highest win probability
4. **Most Likely to Lose**: Teams with lowest win probability
5. **Starred**: User's saved matches

### Match Overlay

**Features**:
- Modal overlay with detailed match information
- Team logos and names
- Win percentages for both teams
- Visual probability scale (color-coded gradient)
- Match details: League, Round, Venue, Referee, Date, Status
- Placeholder sections for team statistics

**Interaction**:
- Click any match card to open overlay
- Close via X button, backdrop click, or Escape key
- Smooth animations (fade-in, slide-up)

### Star System

**Functionality**:
- Click star button (☆) to save match
- Starred matches appear in "Starred" tab
- Uses browser localStorage for persistence
- Star state persists across page refreshes

---

## Development Guidelines

### Code Structure

**Flask Blueprints**:
- Routes organized into blueprints for modularity
- `matches_bp`: Match-related endpoints
- `admin_bp`: Admin functionality
- `user_bp`: User profile routes

**Error Handling**:
- Try-except blocks around database operations
- Logging for debugging and monitoring
- Graceful fallbacks (JSON files if API fails)

**Database Operations**:
- Always close connections after use
- Use row factories for easier data access
- Handle missing columns gracefully (ALTER TABLE with try-except)

### Adding New Features

1. **New Route**: Add to appropriate blueprint in `routes/`
2. **New Template**: Add HTML file to `templates/`
3. **New Static Asset**: Add to `static/css/`, `static/js/`, or `static/images/`
4. **Database Changes**: Update `init_db()` in `app.py` with migration logic

### Testing

- Check logs in `logs/app.log` for errors
- Test database operations with SQLite browser
- Verify API responses in browser DevTools Network tab
- Test responsive design on different screen sizes

---

## Deployment

### Development Server
```bash
python app.py
```
Runs on `http://localhost:5000` (development mode)

### Production Considerations

**WSGI Server** (Recommended):
- Use Gunicorn or uWSGI for production
- Example: `gunicorn -w 4 -b 0.0.0.0:5000 app:app`

**Environment Variables**:
- Set `FLASK_ENV=production`
- Configure API keys securely
- Use environment variables for sensitive data

**Database**:
- Consider migrating to PostgreSQL/MySQL for production
- Implement database backups
- Use connection pooling

**Static Files**:
- Serve via CDN or reverse proxy (Nginx) in production
- Enable compression for CSS/JS files

---

## Troubleshooting

### Common Issues

**Database Errors**:
- Ensure `draft_ministers.db` has write permissions
- Check if database file exists in root directory
- Review `logs/app.log` for specific error messages

**API Failures**:
- Verify API key is valid in `routes/matches.py`
- Check internet connection
- Application falls back to local JSON files if API fails

**ML Model Not Loading**:
- Ensure `machine_learning/football_database.sqlite` exists
- Check file paths in `machine_learning.py`
- Verify scikit-learn and pandas are installed

**Port Already in Use**:
- Change port in `app.py`: `app.run(host='0.0.0.0', port=5001)`
- Or kill process using port 5000

---

## Future Enhancements

- User authentication and accounts
- Real-time match updates via WebSockets
- Advanced statistics and analytics
- Betting integration
- Mobile app version
- Docker containerization
- CI/CD pipeline
- Unit and integration tests
- API rate limiting
- Caching layer (Redis)

---

## License

[Specify your license here]

## Contributors

[Add contributor information]

---

## Contact & Support

For issues, questions, or contributions, please [create an issue / contact maintainers].
