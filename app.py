"""
Football Score Prediction - Ứng dụng chính.
Đăng ký các Blueprint: Prediction, Prediction History, Matches, Standings, News, Favorites.
"""
from flask import Flask, render_template
from datetime import timedelta

from config import app_config
from blueprints import prediction, prediction_history, matches, standings, news, favorites, auth

app = Flask(__name__)
app.config.update(app_config)
app.secret_key = app_config.get("SECRET_KEY", "football-prediction-secret-key")
app.permanent_session_lifetime = timedelta(days=7)

# Đăng ký Blueprints (không dùng url_prefix để giữ nguyên đường dẫn)
app.register_blueprint(prediction.bp)
app.register_blueprint(prediction_history.bp)
app.register_blueprint(matches.bp)
app.register_blueprint(standings.bp)
app.register_blueprint(news.bp)
app.register_blueprint(favorites.bp)
app.register_blueprint(auth.bp)


@app.route('/')
def home():
    """Trang chủ."""
    return render_template('home.html', active_tab='home')


if __name__ == '__main__':
    app.run(debug=True)
