# Finance Management System

A Django-based Finance Management System for generating and managing invoices.

## Features
- Invoice generation and storage
- SQLite database integration
- User authentication
- Admin panel for managing finances

## Installation

### Prerequisites
- Python 3.x
- Django

### Setup Instructions
1. Clone the repository:
   git clone https://github.com/EldarasPetrokas/Finance_Management.git
   cd Finance_Management
2. Create a virtual environment:
   python -m venv venv
   On Mac use: source venv/bin/activate
   On Windows use: venv\Scripts\activate
3. Install dependencies:
   pip install -r requirements.txt
4. Apply database migrations:
   python manage.py migrate
5. Run the development server:
   python manage.py runserver

## Usage
- Access the application at http://127.0.0.1:8000/
- Manage users, invoices and clients via the admin panel (/admin/)

## Contributing
Feel free to submit pull requests or report issues.


