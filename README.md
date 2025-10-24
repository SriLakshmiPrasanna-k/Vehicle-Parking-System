# Vehicle Parking Management System

A comprehensive Flask-based parking management application designed for 4-wheeler parking with admin controls and user booking functionality.

## Features

### Admin Features
- **Admin Dashboard**: Complete overview of all parking lots and system statistics
- **Parking Lot Management**: Create, edit, and delete parking lots
- **Real-time Monitoring**: View all active reservations and spot status
- **User Management**: View all registered users and their booking history
- **Analytics**: Visual charts showing occupancy rates and system usage

### User Features
- **User Registration & Login**: Secure account creation and authentication
- **Parking Booking**: Browse available lots and book spots automatically
- **Active Session Management**: Monitor current parking sessions with real-time cost calculation
- **Booking History**: View past reservations and total spending
- **Personal Analytics**: Charts showing booking patterns and spending trends

### System Features
- **Automatic Spot Assignment**: First-available spot allocation
- **Real-time Cost Calculation**: Hourly pricing with live updates
- **Responsive Design**: Mobile-friendly Bootstrap interface
- **Dark Theme**: Modern, easy-on-eyes design
- **Data Validation**: Comprehensive form validation and error handling

## Technology Stack

- **Backend**: Flask, SQLAlchemy, Flask-Login, Flask-WTF
- **Frontend**: Jinja2, Bootstrap 5, Font Awesome, Chart.js
- **Database**: SQLite (default) / PostgreSQL (production)
- **Authentication**: Werkzeug password hashing
- **Charts**: Chart.js for data visualization

## Installation & Setup

### Prerequisites
- Python 3.11+
- pip package manager

### Local Development

1. **Clone the project**
   ```bash
   git clone <repository-url>
   cd parking-management-system
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set environment variables** (optional)
   ```bash
   export SESSION_SECRET="your-secret-key-here"
   export DATABASE_URL="sqlite:///parking_app.db"
   ```

4. **Run the application**
   ```bash
   python main.py
   ```

5. **Access the application**
   - Open your browser to `http://localhost:5000`
   - Admin login: username `admin`, password `admin123`
   - Or register as a new user to test booking functionality

### Production Deployment

The application is ready for deployment on platforms like:
- **Replit**: Already configured with gunicorn
- **Heroku**: Add Procfile and set environment variables
- **Railway**: Configure environment and deploy
- **DigitalOcean App Platform**: Use the included configuration

For production, set these environment variables:
- `SESSION_SECRET`: A secure random string
- `DATABASE_URL`: PostgreSQL connection string (optional)

## Project Structure

```
parking-management-system/
├── app.py                 # Flask application factory
├── main.py               # Application entry point
├── models.py             # Database models
├── routes.py             # Application routes
├── forms.py              # WTForms forms
├── utils.py              # Utility functions
├── templates/            # Jinja2 templates
├── static/               # CSS, JS, and assets
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## Database Schema

### Models
- **User**: User accounts with admin/user roles
- **ParkingLot**: Physical parking locations
- **ParkingSpot**: Individual parking spaces
- **Reservation**: Booking records and history

### Key Relationships
- One-to-Many: ParkingLot → ParkingSpot
- One-to-Many: User → Reservation
- One-to-Many: ParkingSpot → Reservation

## API Endpoints

- `GET /api/parking-stats` - Real-time parking statistics (requires login)

## Core Functionalities

### Admin Operations
- Login with pre-created admin account
- Create parking lots with automatic spot generation
- Edit lot details and adjust spot counts
- Delete empty lots
- Monitor all active reservations
- View system-wide analytics

### User Operations
- Register new user accounts
- Browse available parking lots
- Book parking spots (automatic assignment)
- Release parking spots when leaving
- View personal booking history and statistics

### System Operations
- Automatic database initialization
- Real-time cost calculation
- Spot availability management
- Session management and security

## Default Admin Account

- **Username**: `admin`
- **Password**: `admin123`
- **Role**: Administrator (full access)

## Development Notes

- Database tables are created automatically on first run
- Admin user is created programmatically if not exists
- SQLite is used by default for easy development
- PostgreSQL support available via DATABASE_URL
- All parking spots are auto-generated based on lot capacity
- Real-time updates every 30 seconds on dashboard pages

## Security Features

- Password hashing with Werkzeug
- CSRF protection on all forms
- Session management with Flask-Login
- SQL injection prevention with SQLAlchemy ORM
- Form validation on both client and server side

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## License

This project is created for educational purposes as part of Modern Application Development coursework.

## Support

For issues or questions about the parking management system, please check the code documentation or contact the development team.