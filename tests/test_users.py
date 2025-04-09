import pytest
from datetime import datetime, timedelta
from app import create_app
from app.database import db
from app.models import User, APIKey, APIUsage

@pytest.fixture
def client():
    """Create and configure a Flask app for testing"""
    app = create_app('test')
    
    # Create the database and tables
    with app.app_context():
        db.create_all()
        
        # Create test user
        user = User(
            username='profileuser',
            email='profile@example.com',
            password='Password123!'
        )
        db.session.add(user)
        db.session.commit()
        
        # Create an API key for the user
        api_key = APIKey(
            user_id=user.id,
            name='Test Profile Key'
        )
        db.session.add(api_key)
        db.session.commit()
        
        # Log some API usage
        usage = APIUsage(
            api_key_id=api_key.id,
            endpoint='/api/v1/countries',
            method='GET',
            status_code=200,
            response_time_ms=150,
            ip_address='127.0.0.1'
        )
        db.session.add(usage)
        db.session.commit()
        
        # Store user ID for tests
        app.config['TEST_USER_ID'] = user.id
    
    # Create a test client
    with app.test_client() as client:
        # Login to get the access token
        response = client.post(
            '/auth/login',
            json={
                'username': 'profileuser',
                'password': 'Password123!'
            }
        )
        data = response.get_json()
        app.config['TEST_ACCESS_TOKEN'] = data['access_token']
        
        yield client
    
    # Clean up
    with app.app_context():
        db.drop_all()

def test_get_profile(client):
    """Test retrieving user profile"""
    app = client.application
    access_token = app.config['TEST_ACCESS_TOKEN']
    
    # Get the user profile
    response = client.get(
        '/user/profile',
        headers={'Authorization': f'Bearer {access_token}'}
    )
    
    # Check response
    assert response.status_code == 200
    data = response.get_json()
    assert 'user' in data
    assert data['user']['username'] == 'profileuser'
    assert data['user']['email'] == 'profile@example.com'

def test_get_api_keys(client):
    """Test retrieving user API keys"""
    app = client.application
    access_token = app.config['TEST_ACCESS_TOKEN']
    
    # Get the user's API keys
    response = client.get(
        '/user/api-keys',
        headers={'Authorization': f'Bearer {access_token}'}
    )
    
    # Check response
    assert response.status_code == 200
    data = response.get_json()
    assert 'api_keys' in data
    assert len(data['api_keys']) == 1
    assert data['api_keys'][0]['name'] == 'Test Profile Key'
    assert data['api_keys'][0]['is_active'] == True
    # Ensure key value is not included in the response
    assert 'key' not in data['api_keys'][0]

def test_create_api_key(client):
    """Test creating a new API key"""
    app = client.application
    access_token = app.config['TEST_ACCESS_TOKEN']
    
    # Create a new API key
    response = client.post(
        '/user/api-keys',
        headers={'Authorization': f'Bearer {access_token}'},
        json={
            'name': 'New Test Key',
            'expires_in_days': 90
        }
    )
    
    # Check response
    assert response.status_code == 201
    data = response.get_json()
    assert 'api_key' in data
    assert data['api_key']['name'] == 'New Test Key'
    assert 'key' in data['api_key']  # Key value should be included when first created
    
    # Check expiration date is around 90 days from now
    expiry = datetime.fromisoformat(data['api_key']['expires_at'].replace('Z', '+00:00'))
    now = datetime.utcnow()
    assert (expiry - now).days >= 89  # Allow for slight timing differences
    assert (expiry - now).days <= 91

def test_revoke_api_key(client):
    """Test revoking an API key"""
    app = client.application
    access_token = app.config['TEST_ACCESS_TOKEN']
    
    # Get the user's API keys first
    keys_response = client.get(
        '/user/api-keys',
        headers={'Authorization': f'Bearer {access_token}'}
    )
    keys_data = keys_response.get_json()
    key_id = keys_data['api_keys'][0]['id']
    
    # Revoke the key
    response = client.delete(
        f'/user/api-keys/{key_id}',
        headers={'Authorization': f'Bearer {access_token}'}
    )
    
    # Check response
    assert response.status_code == 200
    data = response.get_json()
    assert 'message' in data
    assert 'revoked successfully' in data['message']
    
    # Check that the key is now inactive
    check_response = client.get(
        '/user/api-keys',
        headers={'Authorization': f'Bearer {access_token}'}
    )
    check_data = check_response.get_json()
    assert check_data['api_keys'][0]['is_active'] == False

def test_create_api_key_with_invalid_expiry(client):
    """Test creating API key with invalid expiration"""
    app = client.application
    access_token = app.config['TEST_ACCESS_TOKEN']
    
    # Try to create an API key with too long expiration
    response = client.post(
        '/user/api-keys',
        headers={'Authorization': f'Bearer {access_token}'},
        json={
            'name': 'Invalid Expiry Key',
            'expires_in_days': 5000  # Too many days
        }
    )
    
    # Check response
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data
    assert 'Expiration days' in data['error']

def test_unauthorized_access(client):
    """Test unauthorized access to API endpoints"""
    # Try to access user profile without token
    response = client.get('/user/profile')
    
    # Check response
    assert response.status_code == 401
    data = response.get_json()
    assert 'error' in data

def test_revoke_nonexistent_key(client):
    """Test revoking a nonexistent API key"""
    app = client.application
    access_token = app.config['TEST_ACCESS_TOKEN']
    
    # Try to revoke a nonexistent key
    response = client.delete(
        '/user/api-keys/999999',  # Nonexistent ID
        headers={'Authorization': f'Bearer {access_token}'}
    )
    
    # Check response
    assert response.status_code == 404
    data = response.get_json()
    assert 'error' in data
    assert 'not found' in data['error']

def test_revoke_other_users_key(client):
    """Test revoking another user's API key"""
    app = client.application
    access_token = app.config['TEST_ACCESS_TOKEN']
    
    # Create another user with their own API key
    with app.app_context():
        other_user = User(
            username='otheruser',
            email='other@example.com',
            password='Password123!'
        )
        db.session.add(other_user)
        db.session.commit()
        
        other_key = APIKey(
            user_id=other_user.id,
            name='Other User Key'
        )
        db.session.add(other_key)
        db.session.commit()
        
        other_key_id = other_key.id
    
    # Try to revoke the other user's key
    response = client.delete(
        f'/user/api-keys/{other_key_id}',
        headers={'Authorization': f'Bearer {access_token}'}
    )
    
    # Check response - should be unauthorized
    assert response.status_code == 403
    data = response.get_json()
    assert 'error' in data
    assert 'Unauthorized' in data['error']