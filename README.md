
# Finance Management System

A Django-based invoice management system for managing clients, invoices, and generating PDFs for overdue invoices.

## Features

- Add clients and invoices through the frontend
- Generate PDF invoices and store them in directories named after clients
- Sort invoices by client name, amount, and status
- Send reminder emails for overdue invoices
- Download invoices as PDFs from the frontend
- Role-based access control (Admin and User roles)

## Installation

Clone the repository:

git clone https://github.com/EldarasPetrokas/Finance_Management.git

Navigate to the project directory:

cd Finance_Management

Create a virtual environment:

python -m venv venv

Activate the virtual environment:

On Windows:
venv\Scripts\activate

On macOS/Linux:
source venv/bin/activate

Install the required dependencies:
pip install -r requirements.txt

Create a superuser to access the admin panel:
python manage.py createsuperuser
Run the server:

python manage.py runserver
Open http://127.0.0.1:8000 in your browser to access the app.


## Usage

Adding Clients and Invoices: Navigate to the admin panel to create clients and invoices. You can also add invoices and clients through the frontend.
Generating Invoices: When adding an invoice, a PDF will be generated automatically and saved to the invoices/ directory.
Sending Email Reminders: If an invoice is overdue, you can send an email reminder from the invoice detail page.
Downloading PDFs: You can download generated invoices as PDFs from both the invoice list and the invoice detail page.
