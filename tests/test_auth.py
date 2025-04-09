import pytest
from app import create_app
from app.database import db
from app.models import User

@pytest.fixture
def client():
    """Create and configure a Flask app for testing"""
    app = create_app('test')
    
    # Create the database and tables
    with app.app_context():
        db.create_all()
    
    # Create a test client
    with app.test_client() as client:
        yield client
    
    # Clean up
    with app.app_context():
        db.drop_all()

def test_user_registration(client):
    """Test user registration"""
    # Register a new user
    response = client.post(
        '/auth/register',
        json={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'Password123!'
        }
    )
    
    # Check response
    assert response.status_code == 201
    data = response.get_json()
    assert 'user' in data
    assert 'access_token' in data
    assert 'refresh_token' in data
    
    # Verify user was created
    app = client.application
    with app.app_context():
        user = User.query.filter_by(username='newuser').first()
        assert user is not None
        assert user.email == 'newuser@example.com'
        assert user.check_password('Password123!')

def test_user_login(client):
    """Test user login"""
    # Create a user first
    app = client.application
    with app.app_context():
        user = User(
            username='logintest',
            email='login@example.com',
            password='Password123!'
        )
        db.session.add(user)
        db.session.commit()
    
    # Login with the user
    response = client.post(
        '/auth/login',
        json={
            'username': 'logintest',
            'password': 'Password123!'
        }
    )
    
    # Check response
    assert response.status_code == 200
    data = response.get_json()
    assert 'user' in data
    assert 'access_token' in data
    assert 'refresh_token' in data
    assert data['user']['username'] == 'logintest'

def test_invalid_login(client):
    """Test login with invalid credentials"""
    # Create a user first
    app = client.application
    with app.app_context():
        user = User(
            username='badlogin',
            email='badlogin@example.com',
            password='Password123!'
        )
        db.session.add(user)
        db.session.commit()
    
    # Try login with wrong password
    response = client.post(
        '/auth/login',
        json={
            'username': 'badlogin',
            'password': 'WrongPassword123!'
        }
    )
    
    # Check response
    assert response.status_code == 401
    data = response.get_json()
    assert 'error' in data

def test_token_refresh(client):
    """Test token refresh"""
    # Create a user first
    app = client.application
    with app.app_context():
        user = User(
            username='refreshtest',
            email='refresh@example.com',
            password='Password123!'
        )
        db.session.add(user)
        db.session.commit()
    
    # Login to get tokens
    login_response = client.post(
        '/auth/login',
        json={
            'username': 'refreshtest',
            'password': 'Password123!'
        }
    )
    login_data = login_response.get_json()
    refresh_token = login_data['refresh_token']
    
    # Use refresh token to get new access token
    response = client.post(
        '/auth/refresh',
        headers={'Authorization': f'Bearer {refresh_token}'}
    )
    
    # Check response
    assert response.status_code == 200
    data = response.get_json()
    assert 'access_token' in data
    assert data['message'] == 'Token refreshed successfully'

def test_weak_password_registration(client):
    """Test registration with weak password"""
    # Try to register with weak password
    response = client.post(
        '/auth/register',
        json={
            'username': 'weakuser',
            'email': 'weak@example.com',
            'password': 'weak'
        }
    )
    
    # Check response
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data
    # Should mention password requirements
    assert 'Password' in data['error']
    
    # Verify user was not created
    app = client.application
    with app.app_context():
        user = User.query.filter_by(username='weakuser').first()
        assert user is None

def test_duplicate_username_registration(client):
    """Test registration with duplicate username"""
    # Create a user first
    app = client.application
    with app.app_context():
        user = User(
            username='duplicate',
            email='original@example.com',
            password='Password123!'
        )
        db.session.add(user)
        db.session.commit()
    
    # Try to register with same username
    response = client.post(
        '/auth/register',
        json={
            'username': 'duplicate',
            'email': 'another@example.com',
            'password': 'Password123!'
        }
    )
    
    # Check response
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data
    assert 'Username already exists' in data['error']

def test_duplicate_email_registration(client):
    """Test registration with duplicate email"""
    # Create a user first
    app = client.application
    with app.app_context():
        user = User(
            username='emailuser',
            email='duplicate@example.com',
            password='Password123!'
        )
        db.session.add(user)
        db.session.commit()
    
    # Try to register with same email
    response = client.post(
        '/auth/register',
        json={
            'username': 'differentuser',
            'email': 'duplicate@example.com',
            'password': 'Password123!'
        }
    )
    
    # Check response
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data
    assert 'Email already registered' in data['error']