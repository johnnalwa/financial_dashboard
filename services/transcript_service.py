from datetime import datetime
from app import db
from models import Transcript
from services.api_service import AIModelService
from config import AI_API_BASE_URL, AI_API_KEY
import logging

class TranscriptService:
    """Service for processing earnings call transcripts"""
    
    def __init__(self):
        """Initialize the transcript service with the AI model service"""
        self.ai_service = AIModelService(AI_API_BASE_URL, AI_API_KEY)
        self.logger = logging.getLogger(__name__)
    
    def fetch_transcript(self, ticker, quarter, year):
        """
        Fetch an earnings call transcript from external source
        This is a placeholder - in a real implementation, you would 
        call an API or scrape a website to get the transcript
        """
        self.logger.info(f"Fetching transcript for {ticker} {quarter} {year}")
        
        # This is just a placeholder - replace with actual implementation
        # Example: return requests.get(f"https://api.example.com/transcripts/{ticker}/{quarter}/{year}").json()
        
        return {
            "status": "error",
            "message": "Direct transcript fetching not implemented. Please upload transcript manually."
        }
    
    def process_transcript(self, raw_text, company_name, ticker, call_date, quarter, year):
        """
        Process an earnings call transcript through the AI service
        and save to database
        """
        self.logger.info(f"Processing transcript for {company_name} ({ticker}) {quarter} {year}")
        
        try:
            # Generate summary using AI API
            summary_result = self.ai_service.summarize_transcript(raw_text)
            summary = summary_result.get('summary', 'Summary generation failed')
            
            # Analyze sentiment using AI API
            sentiment_score = self.ai_service.analyze_sentiment(raw_text)
            
            # Convert call_date to datetime if it's a string
            if isinstance(call_date, str):
                call_date = datetime.fromisoformat(call_date.replace('Z', '+00:00'))
            
            # Save to database
            transcript = Transcript(
                company_name=company_name,
                ticker=ticker,
                call_date=call_date,
                quarter=quarter,
                year=int(year),
                raw_text=raw_text,
                summary=summary,
                sentiment_score=sentiment_score
            )
            
            db.session.add(transcript)
            db.session.commit()
            
            self.logger.info(f"Successfully processed transcript ID {transcript.id}")
            return transcript
            
        except Exception as e:
            self.logger.error(f"Error processing transcript: {str(e)}")
            # Rollback the database session in case of error
            db.session.rollback()
            raise
    
    def get_recent_transcripts(self, limit=10):
        """Get most recent transcripts from the database"""
        return Transcript.query.order_by(Transcript.call_date.desc()).limit(limit).all()
    
    def get_company_transcripts(self, ticker, limit=5):
        """Get recent transcripts for a specific company"""
        return Transcript.query.filter_by(ticker=ticker).order_by(Transcript.call_date.desc()).limit(limit).all()
    
    def get_transcript_by_id(self, transcript_id):
        """Get a specific transcript by ID"""
        return Transcript.query.get(transcript_id)