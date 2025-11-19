from flask import Blueprint, render_template

user_bp = Blueprint('user', __name__)

@user_bp.route('/profile')
def profile():
    # User data
    user_details = {
        "username": "Bustad, Isaac",
        "email": "BustadIsaac@mnsu.com",
        "join_date": "Nov 2023",
        "vip_status": "Lord"
    }
    
    # Portfolio data
    portfolio = {
        "wallet_balance": 35934556.00,
        "total_profit": 1568300.00,
        "win_rate": 82,
        "placed_bets": [
            {"match": "Man City vs Real Madrid", "bet": "Man City Win", "amount": 500000, "status": "Active", "potential_win": 950000},
            {"match": "Bayern Munich vs PSG", "bet": "Over 2.5 Goals", "amount": 250000, "status": "Won", "pnl": 212500},
            {"match": "Inter Milan vs Juventus", "bet": "Inter Win", "amount": 150000, "status": "Won", "pnl": 180000},
            {"match": "Liverpool vs Man Utd", "bet": "Liverpool Win", "amount": 100000, "status": "Lost", "pnl": -100000},
            {"match": "Barcelona vs Atletico", "bet": "Barcelona Win", "amount": 300000, "status": "Won", "pnl": 240000},
            {"match": "Arsenal vs Tottenham", "bet": "Arsenal Win", "amount": 200000, "status": "Won", "pnl": 170000}
        ]
    }
    
    return render_template('profile.html', user=user_details, portfolio=portfolio)
