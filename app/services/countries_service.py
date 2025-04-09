import requests
from flask import current_app
import json

class CountriesService:
    """Service for interacting with RestCountries API"""
    
    def __init__(self, app=None):
        self.app = app
        self.base_url = None
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize with Flask app"""
        self.app = app
        self.base_url = app.config.get('COUNTRIES_API_URL', 'https://restcountries.com/v3.1')
    
    def _make_request(self, endpoint, params=None):
        """Make a request to the RestCountries API"""
        if self.base_url is None:
            self.base_url = current_app.config.get('COUNTRIES_API_URL', 'https://restcountries.com/v3.1')
        
        url = f"{self.base_url}/{endpoint}"
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            current_app.logger.error(f"Countries API error: {str(e)}")
            return {'error': str(e)}
    
    def _filter_country_data(self, country):
        """Filter country data to include only required fields"""
        try:
            # Handle different API response structures
            filtered = {
                'name': country.get('name', {}).get('common', ''),
                'official_name': country.get('name', {}).get('official', ''),
                'capital': country.get('capital', [''])[0] if country.get('capital') else '',
                'languages': country.get('languages', {}),
                'currencies': {},
                'flag': country.get('flags', {}).get('png', '')
            }
            
            # Process currencies
            currencies = country.get('currencies', {})
            for code, details in currencies.items():
                filtered['currencies'][code] = {
                    'name': details.get('name', ''),
                    'symbol': details.get('symbol', '')
                }
            
            return filtered
        except Exception as e:
            current_app.logger.error(f"Error filtering country data: {str(e)}")
            return {
                'name': country.get('name', {}).get('common', ''),
                'error': 'Could not parse all data'
            }
    
    def get_all_countries(self):
        """Get a list of all countries with filtered data"""
        countries = self._make_request('all')
        
        if isinstance(countries, list):
            return [self._filter_country_data(country) for country in countries]
        return {'error': 'Failed to retrieve countries'}
    
    def get_country_by_name(self, name):
        """Get a specific country by name"""
        countries = self._make_request(f'name/{name}')
        
        if isinstance(countries, list) and countries:
            return [self._filter_country_data(country) for country in countries]
        return {'error': f'Country not found: {name}'}
    
    def get_countries_by_currency(self, currency_code):
        """Get countries by currency code"""
        countries = self._make_request(f'currency/{currency_code}')
        
        if isinstance(countries, list):
            return [self._filter_country_data(country) for country in countries]
        return {'error': f'No countries found with currency: {currency_code}'}
    
    def get_countries_by_language(self, language_code):
        """Get countries by language code"""
        countries = self._make_request(f'lang/{language_code}')
        
        if isinstance(countries, list):
            return [self._filter_country_data(country) for country in countries]
        return {'error': f'No countries found with language: {language_code}'}
    
    def get_countries_by_region(self, region):
        """Get countries by region"""
        countries = self._make_request(f'region/{region}')
        
        if isinstance(countries, list):
            return [self._filter_country_data(country) for country in countries]
        return {'error': f'No countries found in region: {region}'}

# Create an instance to be used with init_app pattern
countries_service = CountriesService()