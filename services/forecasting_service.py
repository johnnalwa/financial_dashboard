import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
import json
import requests
from extensions import db
from models import Forecast
from services.api_service import AIModelService
from config import AI_API_BASE_URL, AI_API_KEY

class ForecastingService:
    """Service for generating financial forecasts using Alpha Vantage API"""
    
    def __init__(self):
        """Initialize the forecasting service with the AI model service"""
        self.ai_service = AIModelService(AI_API_BASE_URL, AI_API_KEY)
        self.alpha_vantage_api_key = "KAFJ4O9W4HJGZOAU"
        self.alpha_vantage_base_url = "https://www.alphavantage.co/query"
        self.logger = logging.getLogger(__name__)
        
    def fetch_historical_data(self, ticker, metric='revenue', lookback_days=1095):
        """
        Fetch historical financial data for a company using Alpha Vantage API
        """
        self.logger.info(f"Fetching historical {metric} data for {ticker} from Alpha Vantage")
        
        try:
            if metric.lower() == 'revenue':
                # Fetch income statement data which includes revenue
                params = {
                    "function": "INCOME_STATEMENT",
                    "symbol": ticker,
                    "apikey": self.alpha_vantage_api_key
                }
                
                response = requests.get(self.alpha_vantage_base_url, params=params)
                response.raise_for_status()
                data = response.json()
                
                # Extract quarterly reports
                if 'quarterlyReports' in data:
                    quarters = data['quarterlyReports']
                    
                    dates = []
                    values = []
                    
                    for quarter in quarters:
                        date = quarter.get('fiscalDateEnding')
                        # Get total revenue
                        revenue = quarter.get('totalRevenue')
                        
                        if date and revenue:
                            dates.append(datetime.fromisoformat(date))
                            values.append(float(revenue))
                    
                    # Create dataframe with most recent first
                    historical_data = pd.DataFrame({
                        'date': dates,
                        'value': values
                    })
                    
                    # Sort by date (newest first)
                    historical_data = historical_data.sort_values(by='date', ascending=False)
                    
                    # Limit to lookback period
                    cutoff_date = datetime.now() - timedelta(days=lookback_days)
                    historical_data = historical_data[historical_data['date'] >= cutoff_date]
                    
                    return historical_data
                else:
                    self.logger.warning(f"No quarterly reports found for {ticker}, falling back to stock price data")
                    # Fall back to stock price data
                    metric = 'stock_price'
            
            if metric.lower() == 'stock_price':
                # Fetch time series data for stock prices
                params = {
                    "function": "TIME_SERIES_MONTHLY",
                    "symbol": ticker,
                    "apikey": self.alpha_vantage_api_key
                }
                
                response = requests.get(self.alpha_vantage_base_url, params=params)
                response.raise_for_status()
                data = response.json()
                
                if 'Monthly Time Series' in data:
                    time_series = data['Monthly Time Series']
                    
                    dates = []
                    values = []
                    
                    for date_str, values_dict in time_series.items():
                        # Convert date string to datetime
                        date = datetime.strptime(date_str, '%Y-%m-%d')
                        
                        # Get closing price
                        close_price = values_dict.get('4. close')
                        
                        if date and close_price:
                            dates.append(date)
                            values.append(float(close_price))
                    
                    # Create dataframe with most recent first
                    historical_data = pd.DataFrame({
                        'date': dates,
                        'value': values
                    })
                    
                    # Sort by date (newest first)
                    historical_data = historical_data.sort_values(by='date', ascending=False)
                    
                    # Limit to lookback period
                    cutoff_date = datetime.now() - timedelta(days=lookback_days)
                    historical_data = historical_data[historical_data['date'] >= cutoff_date]
                    
                    return historical_data
                else:
                    self.logger.error(f"No time series data found for {ticker}")
                    return pd.DataFrame(columns=['date', 'value'])
            
            # If metric is neither revenue nor stock_price, return empty dataframe
            self.logger.warning(f"Unsupported metric: {metric}")
            return pd.DataFrame(columns=['date', 'value'])
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"API request to Alpha Vantage failed: {str(e)}")
            return pd.DataFrame(columns=['date', 'value'])
        except Exception as e:
            self.logger.error(f"Error fetching historical data: {str(e)}")
            return pd.DataFrame(columns=['date', 'value'])
    
    def generate_forecast(self, ticker, metric='revenue', forecast_periods=4):
        """
        Generate financial forecasts using historical data from Alpha Vantage
        """
        self.logger.info(f"Generating {metric} forecast for {ticker}")
        
        try:
            # Check if forecasts already exist for this ticker and metric
            existing_forecasts = Forecast.query.filter_by(
                company_id=ticker,
                metric=metric
            ).all()
            
            # Only generate new forecasts if none exist or if they're older than 7 days
            if existing_forecasts:
                newest_forecast = max(existing_forecasts, key=lambda f: f.created_at)
                forecast_age = (datetime.utcnow() - newest_forecast.created_at).days
                
                if forecast_age < 7:
                    self.logger.info(f"Using existing forecasts for {ticker} {metric} (age: {forecast_age} days)")
                    return existing_forecasts
                else:
                    self.logger.info(f"Existing forecasts are {forecast_age} days old, generating new ones")
                    
                    # Delete existing forecasts
                    for forecast in existing_forecasts:
                        db.session.delete(forecast)
                    db.session.commit()
            
            # Fetch historical data from Alpha Vantage
            historical_data = self.fetch_historical_data(ticker, metric)
            
            if historical_data.empty:
                raise Exception(f"No historical data available for {ticker}")
            
            # Sort by date for forecasting (oldest first)
            historical_data = historical_data.sort_values(by='date')
            
            # Simple forecasting algorithm if AI API is not available for forecasting
            # Prepare data for model (simple linear regression)
            X = np.array(range(len(historical_data))).reshape(-1, 1)
            y = historical_data['value'].values
            
            # Fit linear regression model
            from sklearn.linear_model import LinearRegression
            model = LinearRegression()
            model.fit(X, y)
            
            # Generate future dates
            last_date = historical_data['date'].iloc[-1]
            
            if metric.lower() == 'revenue':
                # Quarterly for revenue (90 days apart)
                future_dates = [last_date + timedelta(days=90*(i+1)) for i in range(forecast_periods)]
            else:
                # Monthly for stock prices (30 days apart)
                future_dates = [last_date + timedelta(days=30*(i+1)) for i in range(forecast_periods)]
            
            # Generate predictions
            future_X = np.array(range(len(historical_data), len(historical_data) + forecast_periods)).reshape(-1, 1)
            predictions = model.predict(future_X)
            
            # Calculate confidence intervals
            # This is a simple approach; more sophisticated methods exist
            from sklearn.metrics import mean_squared_error
            y_pred = model.predict(X)
            rmse = np.sqrt(mean_squared_error(y, y_pred))
            
            # Standard error increases with forecast horizon
            confidence_interval = 1.96 * rmse  # 95% confidence interval
            
            # Save forecasts to database
            forecasts = []
            for i, (pred_date, pred_value) in enumerate(zip(future_dates, predictions)):
                # Increase uncertainty for further-out predictions
                uncertainty_factor = 1 + (i * 0.2)  # 20% more uncertainty per period
                current_ci = confidence_interval * uncertainty_factor
                
                forecast = Forecast(
                    company_id=ticker,
                    forecast_date=pred_date,
                    metric=metric,
                    prediction=float(pred_value),
                    confidence_interval_low=float(pred_value - current_ci),
                    confidence_interval_high=float(pred_value + current_ci)
                )
                db.session.add(forecast)
                forecasts.append(forecast)
            
            db.session.commit()
            self.logger.info(f"Successfully generated {len(forecasts)} forecasts for {ticker} {metric}")
            return forecasts
            
        except Exception as e:
            self.logger.error(f"Error generating forecast: {str(e)}")
            db.session.rollback()
            raise
    
    def get_company_forecasts(self, ticker, metric='revenue'):
        """Get existing forecasts for a company and metric"""
        return Forecast.query.filter_by(
            company_id=ticker,
            metric=metric
        ).order_by(Forecast.forecast_date).all()