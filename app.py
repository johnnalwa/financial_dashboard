from flask import Flask, render_template, request, redirect, url_for, jsonify, flash, session
import os
from extensions import db
from datetime import datetime

def create_app():
    app = Flask(__name__)
    app.config.from_object('config')
    
    # Initialize extensions with app
    db.init_app(app)
    
    # Import models
    from models import Transcript, Forecast, User
    
    # Import services
    from services.transcript_service import TranscriptService
    from services.forecasting_service import ForecastingService
    
    transcript_service = TranscriptService()
    forecasting_service = ForecastingService()
    
    # Routes
    @app.route('/')
    def index():
        return render_template('index.html')
    
    @app.route('/dashboard')
    def dashboard():
        # Get recent transcripts
        recent_transcripts = Transcript.query.order_by(Transcript.call_date.desc()).limit(5).all()
        return render_template('dashboard.html', transcripts=recent_transcripts)
    
    @app.route('/transcript/<int:transcript_id>')
    def view_transcript(transcript_id):
        transcript = Transcript.query.get_or_404(transcript_id)
        return render_template('transcript_detail.html', transcript=transcript)
    
    @app.route('/company')
    def company_detail():
        ticker = request.args.get('ticker', '').upper()
        if not ticker:
            flash('Please enter a ticker symbol', 'warning')
            return redirect(url_for('dashboard'))
        
        # Get historical and forecast data
        forecasts = Forecast.query.filter_by(company_id=ticker).order_by(Forecast.forecast_date).all()
        
        # If no forecasts exist, generate them
        if not forecasts:
            try:
                forecasts = forecasting_service.generate_forecast(ticker, 'revenue')
            except Exception as e:
                flash(f"Error generating forecast: {str(e)}", 'danger')
                forecasts = []
        
        return render_template('company_detail.html', ticker=ticker, forecasts=forecasts)
    
    @app.route('/api/transcripts/recent')
    def api_recent_transcripts():
        transcripts = Transcript.query.order_by(Transcript.call_date.desc()).limit(5).all()
        return jsonify({
            'transcripts': [
                {
                    'id': t.id,
                    'company_name': t.company_name,
                    'ticker': t.ticker,
                    'quarter': t.quarter,
                    'year': t.year,
                    'call_date': t.call_date.isoformat(),
                    'summary': t.summary[:100] + '...' if len(t.summary) > 100 else t.summary,
                    'sentiment_score': t.sentiment_score
                } for t in transcripts
            ]
        })
    
    @app.route('/api/process-transcript', methods=['POST'])
    def api_process_transcript():
        data = request.json
        
        # Basic validation
        required_fields = ['company_name', 'ticker', 'quarter', 'year', 'call_date', 'raw_text']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        try:
            transcript = transcript_service.process_transcript(
                data['raw_text'],
                data['company_name'],
                data['ticker'],
                data['call_date'],
                data['quarter'],
                data['year']
            )
            
            return jsonify({
                'id': transcript.id,
                'summary': transcript.summary,
                'sentiment_score': transcript.sentiment_score
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/forecasts/<string:ticker>')
    def api_forecasts(ticker):
        metric = request.args.get('metric', 'revenue')
        
        forecasts = Forecast.query.filter_by(
            company_id=ticker,
            metric=metric
        ).all()
        
        if not forecasts:
            try:
                forecasts = forecasting_service.generate_forecast(ticker, metric)
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        return jsonify({
            'ticker': ticker,
            'metric': metric,
            'forecasts': [
                {
                    'date': f.forecast_date.isoformat(),
                    'value': f.prediction,
                    'lower_bound': f.confidence_interval_low,
                    'upper_bound': f.confidence_interval_high
                } for f in forecasts
            ]
        })
    
    return app

# Create the Flask application
app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)