import requests
import json
import logging

class AIModelService:
    """Service for interacting with the external AI model API"""
    
    def __init__(self, api_base_url, api_key):
        """Initialize the service with API credentials"""
        self.api_base_url = api_base_url
        self.api_key = api_key
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        self.logger = logging.getLogger(__name__)
    
    def make_api_request(self, endpoint, payload):
        """Make a request to the AI API with error handling"""
        try:
            full_url = f"{self.api_base_url}{endpoint}"
            self.logger.info(f"Making API request to {full_url}")
            response = requests.post(
                full_url, 
                headers=self.headers, 
                json=payload,
                timeout=30  # Set a timeout to prevent hanging
            )
            
            response.raise_for_status()  # Raise exception for non-200 status codes
            return response.json()
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"API request failed: {str(e)}")
            raise Exception(f"API request failed: {str(e)}")
        except json.JSONDecodeError:
            self.logger.error("Failed to parse API response as JSON")
            raise Exception("Failed to parse API response as JSON")
    
    def summarize_transcript(self, transcript_text):
        """Call the AI API to summarize an earnings call transcript"""
        endpoint = "/summarize"
        
        # Truncate extremely long transcripts if needed
        # Most APIs have input token limits
        max_chars = 100000  # Adjust based on API limits
        truncated_text = transcript_text[:max_chars] if len(transcript_text) > max_chars else transcript_text
        
        payload = {
            "text": truncated_text,
            "max_length": 1000,  # Request a summary of this maximum length
            "format": "paragraph"  # Request paragraph format rather than bullets
        }
        
        try:
            result = self.make_api_request(endpoint, payload)
            return result
        except Exception as e:
            self.logger.error(f"Summarization failed: {str(e)}")
            # Return a fallback result with an error message
            return {
                "summary": f"Summary generation failed: {str(e)}",
                "error": str(e)
            }
    
    def analyze_sentiment(self, text):
        """Call the AI API to analyze sentiment of text"""
        endpoint = "/sentiment"
        
        # Truncate extremely long text if needed
        max_chars = 50000  # Adjust based on API limits
        truncated_text = text[:max_chars] if len(text) > max_chars else text
        
        payload = {
            "text": truncated_text,
            "include_aspects": False  # Only need overall sentiment, not aspect-based
        }
        
        try:
            result = self.make_api_request(endpoint, payload)
            # Return a float between -1 and 1 representing sentiment
            return result.get('sentiment_score', 0)
        except Exception as e:
            self.logger.error(f"Sentiment analysis failed: {str(e)}")
            # Return neutral sentiment on error
            return 0
    
    def generate_forecast(self, ticker, historical_data, metric, periods=4):
        """Call the AI API to generate financial forecasts"""
        endpoint = "/forecast"
        
        payload = {
            "ticker": ticker,
            "historical_data": historical_data,
            "metric": metric,
            "periods": periods,
            "include_confidence_intervals": True
        }
        
        try:
            result = self.make_api_request(endpoint, payload)
            return result
        except Exception as e:
            self.logger.error(f"Forecast generation failed: {str(e)}")
            # Return a fallback result with an error message
            return {
                "predictions": [],
                "error": str(e)
            }