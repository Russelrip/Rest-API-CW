import pytest
import json
from unittest.mock import patch, MagicMock
from app import create_app
from app.database import db
from app.models import User, APIKey
from app.services.countries_service import CountriesService

# Sample country data for mocking API responses
SAMPLE_COUNTRIES = [
    {
        "name": {
            "common": "United States",
            "official": "United States of America"
        },
        "capital": ["Washington, D.C."],
        "languages": {
            "eng": "English"
        },
        "currencies": {
            "USD": {
                "name": "United States dollar",
                "symbol": "$"
            }
        },
        "flags": {
            "png": "https://flagcdn.com/w320/us.png"
        }
    },
    {
        "name": {
            "common": "Canada",
            "official": "Canada"
        },
        "capital": ["Ottawa"],
        "languages": {
            "eng": "English",
            "fra": "French"
        },
        "currencies": {
            "CAD": {
                "name": "Canadian dollar",
                "symbol": "$"
            }
        },
        "flags": {
            "png": "https://flagcdn.com/w320/ca.png"
        }
    }
]

@pytest.fixture
def client():
    """Create and configure a Flask app for testing"""
    app = create_app('test')
    
    # Create the database and tables
    with app.app_context():
        db.create_all()
        
        # Create test user and API key
        user = User(
            username='testuser',
            email='test@example.com',
            password='Test123!'
        )
        db.session.add(user)
        db.session.commit()
        
        api_key = APIKey(user_id=user.id, name='Test Key')
        db.session.add(api_key)
        db.session.commit()
        
        # Store the API key for tests
        app.config['TEST_API_KEY'] = api_key.key_value
        app.config['TEST_USER_ID'] = user.id
    
    # Create a test client
    with app.test_client() as client:
        yield client
    
    # Clean up
    with app.app_context():
        db.drop_all()

@pytest.fixture
def mock_requests():
    """Fixture to mock requests to external API"""
    with patch('app.services.countries_service.requests') as mock_req:
        # Configure the mock to return a response with sample data
        mock_response = MagicMock()
        mock_response.json.return_value = SAMPLE_COUNTRIES
        mock_response.raise_for_status.return_value = None
        mock_response.ok = True
        mock_req.get.return_value = mock_response
        yield mock_req

def test_get_all_countries(client, mock_requests):
    """Test retrieving all countries"""
    app = client.application
    
    # Make a request with the test API key
    response = client.get(
        '/api/v1/countries',
        headers={'X-API-Key': app.config['TEST_API_KEY']}
    )
    
    # Check status code and response structure
    assert response.status_code == 200
    data = response.get_json()
    assert 'items' in data
    assert 'pagination' in data
    
    # Verify API key was called
    mock_requests.get.assert_called_once()
    
    # Check filtered data structure
    countries = data['items']
    assert len(countries) > 0
    assert 'name' in countries[0]
    assert 'capital' in countries[0]
    assert 'languages' in countries[0]
    assert 'currencies' in countries[0]
    assert 'flag' in countries[0]

def test_get_country_by_name(client, mock_requests):
    """Test retrieving a country by name"""
    app = client.application
    
    # Configure mock to return filtered data for Canada
    mock_response = MagicMock()
    mock_response.json.return_value = [SAMPLE_COUNTRIES[1]]  # Canada data
    mock_response.raise_for_status.return_value = None
    mock_requests.get.return_value = mock_response
    
    # Make a request with the test API key
    response = client.get(
        '/api/v1/countries/canada',
        headers={'X-API-Key': app.config['TEST_API_KEY']}
    )
    
    # Check status code and response data
    assert response.status_code == 200
    data = response.get_json()
    assert data[0]['name'] == 'Canada'
    assert 'Ottawa' in data[0]['capital']
    assert 'CAD' in data[0]['currencies']

def test_get_countries_by_currency(client, mock_requests):
    """Test retrieving countries by currency"""
    app = client.application
    
    # Configure mock to return filtered data for USD
    mock_response = MagicMock()
    mock_response.json.return_value = [SAMPLE_COUNTRIES[0]]  # US data
    mock_response.raise_for_status.return_value = None
    mock_requests.get.return_value = mock_response
    
    # Make a request with the test API key
    response = client.get(
        '/api/v1/countries/currency/USD',
        headers={'X-API-Key': app.config['TEST_API_KEY']}
    )
    
    # Check status code and response data
    assert response.status_code == 200
    data = response.get_json()
    assert 'items' in data
    countries = data['items']
    assert len(countries) > 0
    assert 'USD' in countries[0]['currencies']

def test_get_countries_by_language(client, mock_requests):
    """Test retrieving countries by language"""
    app = client.application
    
    # Configure mock to return filtered data for English
    mock_response = MagicMock()
    mock_response.json.return_value = SAMPLE_COUNTRIES  # Both US and Canada have English
    mock_response.raise_for_status.return_value = None
    mock_requests.get.return_value = mock_response
    
    # Make a request with the test API key
    response = client.get(
        '/api/v1/countries/language/eng',
        headers={'X-API-Key': app.config['TEST_API_KEY']}
    )
    
    # Check status code and response data
    assert response.status_code == 200
    data = response.get_json()
    assert 'items' in data
    assert len(data['items']) == 2  # Both US and Canada

def test_get_countries_by_region(client, mock_requests):
    """Test retrieving countries by region"""
    app = client.application
    
    # Configure mock to return filtered data for North America
    mock_response = MagicMock()
    mock_response.json.return_value = SAMPLE_COUNTRIES  # Both US and Canada
    mock_response.raise_for_status.return_value = None
    mock_requests.get.return_value = mock_response
    
    # Make a request with the test API key
    response = client.get(
        '/api/v1/countries/region/americas',
        headers={'X-API-Key': app.config['TEST_API_KEY']}
    )
    
    # Check status code and response data
    assert response.status_code == 200
    data = response.get_json()
    assert 'items' in data
    assert 'pagination' in data

def test_invalid_api_key(client):
    """Test request with invalid API key"""
    response = client.get(
        '/api/v1/countries',
        headers={'X-API-Key': 'invalid_key'}
    )
    
    # Check status code
    assert response.status_code == 401
    data = response.get_json()
    assert 'error' in data

def test_missing_api_key(client):
    """Test request with no API key"""
    response = client.get('/api/v1/countries')
    
    # Check status code
    assert response.status_code == 401
    data = response.get_json()
    assert 'error' in data

def test_create_api_key(client):
    """Test API key creation"""
    app = client.application
    
    # Get a JWT token first (login)
    login_response = client.post(
        '/auth/login',
        json={
            'username': 'testuser',
            'password': 'Test123!'
        }
    )
    assert login_response.status_code == 200
    login_data = login_response.get_json()
    access_token = login_data['access_token']
    
    # Create a new API key
    response = client.post(
        '/user/api-keys',
        headers={'Authorization': f'Bearer {access_token}'},
        json={
            'name': 'New Test Key',
            'expires_in_days': 30
        }
    )
    
    # Check response
    assert response.status_code == 201
    data = response.get_json()
    assert 'api_key' in data
    assert data['api_key']['name'] == 'New Test Key'
    
    # Verify key was created in the database
    with app.app_context():
        user_id = app.config['TEST_USER_ID']
        user = User.query.get(user_id)
        assert len(user.api_keys) == 2  # Original + new key

def test_revoke_api_key(client):
    """Test revoking an API key"""
    app = client.application
    
    # Get a JWT token first (login)
    login_response = client.post(
        '/auth/login',
        json={
            'username': 'testuser',
            'password': 'Test123!'
        }
    )
    assert login_response.status_code == 200
    login_data = login_response.get_json()
    access_token = login_data['access_token']
    
    # Get the user's API keys
    keys_response = client.get(
        '/user/api-keys',
        headers={'Authorization': f'Bearer {access_token}'}
    )
    assert keys_response.status_code == 200
    keys_data = keys_response.get_json()
    
    # Get the first key's ID
    key_id = keys_data['api_keys'][0]['id']
    
    # Revoke the key
    response = client.delete(
        f'/user/api-keys/{key_id}',
        headers={'Authorization': f'Bearer {access_token}'}
    )
    
    # Check response
    assert response.status_code == 200
    
    # Verify key was revoked in the database
    with app.app_context():
        api_key = APIKey.query.get(key_id)
        assert api_key.is_active == False