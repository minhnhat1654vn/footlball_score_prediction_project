"""
ML Models module for Football Score Prediction application.
Loads and manages machine learning models.
"""
import joblib

# Load ML models
logistic_model = joblib.load('logistic_regression_model.pkl')
poisson_home_model = joblib.load('poisson_home_model.pkl')
poisson_away_model = joblib.load('poisson_away_model.pkl')
