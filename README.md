# Financial Dashboard

A comprehensive web application that provides real-time analysis of earnings call transcripts and financial forecasting capabilities. The dashboard helps stakeholders make data-driven decisions by offering automated transcript summarization, sentiment analysis, and predictive financial metrics.

## Features

- **Earnings Call Transcript Analysis**
  - Automated processing and summarization
  - Sentiment analysis
  - Historical transcript storage and retrieval
  - Quick access to recent transcripts

- **Financial Forecasting**
  - Revenue predictions
  - Confidence intervals for forecasts
  - Historical data visualization
  - Company-specific metrics tracking

- **Interactive Dashboard**
  - Real-time data updates
  - Company-specific detailed views
  - API endpoints for data access
  - User-friendly interface

## Technical Stack

- **Backend**: Flask (Python)
- **Database**: SQLAlchemy
- **Frontend**: HTML/CSS/JavaScript (Templates)

## Setup

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure your environment:
   - Create a `config.py` file with your database and application settings
   - Set up your database connection

4. Initialize the database:
```bash
flask db upgrade
```

5. Run the application:
```bash
python app.py
```

The application will be available at `http://localhost:5000`

## API Endpoints

### Transcripts
- `GET /api/transcripts/recent` - Get recent earnings call transcripts
- `POST /api/process-transcript` - Process and analyze a new transcript

### Forecasts
- `GET /api/forecasts/<ticker>` - Get financial forecasts for a specific company

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
