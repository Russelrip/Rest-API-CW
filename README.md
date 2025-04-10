# Countries API Middleware Service

A secure API middleware service that interfaces with RestCountries.com, providing filtered country information with complete authentication and API key management.

## Features

- **RestCountries.com Integration**: Retrieve essential country information including names, currencies, capitals, languages, and flags
- **Secure Authentication**: Complete user registration and login system
- **API Key Management**: Generate, view, and revoke API keys
- **Security Measures**: Password hashing, secure session management, and input validation
- **Database Management**: SQLite database with proper 3NF design
- **API Usage Tracking**: Track and monitor API key usage

## Technology Stack

- **Backend**: Python 3.9 with Flask
- **Database**: SQLite with SQLAlchemy ORM
- **Authentication**: JWT tokens with bcrypt password hashing
- **Containerization**: Docker

## Installation

### Manual Installation

1. Clone the repository:
```
git clone https://github.com/Russelrip/REST-API-CW.git
cd REST-API-CW
```

2. Install dependencies:
```
pip install -r requirements.txt
```

3. Run the application:
```
python run.py
```

4. Access the application at http://localhost:5000

## API Endpoints

### Authentication Endpoints

- `POST /auth/register` - Register a new user
- `POST /auth/login` - Login and receive access token
- `POST /auth/refresh` - Refresh access token

### User Management Endpoints

- `GET /user/profile` - Get user profile
- `GET /user/api-keys` - Get all API keys for the user
- `POST /user/api-keys` - Create a new API key
- `DELETE /user/api-keys/{key_id}` - Revoke an API key

### Country Data Endpoints

- `GET /api/v1/countries` - Get all countries
- `GET /api/v1/countries/{name}` - Get country by name
- `GET /api/v1/countries/currency/{code}` - Get countries by currency
- `GET /api/v1/countries/language/{code}` - Get countries by language
- `GET /api/v1/countries/region/{region}` - Get countries by region

## Testing

Run tests using pytest:

```
pytest
```

## Security Features

- Password hashing with bcrypt
- JWT for secure API authentication
- API key validation
- Input validation and sanitization
- CSRF protection
- Secure session management
- Rate limiting

## Database Structure

The database follows 3NF design with the following tables:

1. **Users**: Stores user account information
2. **API_Keys**: Tracks API keys and their status
