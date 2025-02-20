# Identity_Reconciliation- 
This project is a Django-based API that implements an Identify Contact endpoint. It allows identifying primary and secondary contact information based on email and phone numbers.

 Project Setup
 1. Clone the Repository
 git clone https://github.com/YOUR_USERNAME/Identity_Reconciliation.git
 cd Identity_Reconciliation

 2.Create a Virtual Environment
  python -m venv .venv
 .venv\Scripts\activate  # Windows
  source .venv/bin/activate  # Mac/Linux

 3.Install Dependencies
   pip install -r requirements.txt

  4.Set Environment Variables
   DATABASE_URL=postgres://username:password@hostname:port/database_name

  5.Apply Migrations
  python manage.py migrate

  6. Run the Development Server
     python manage.py runserver

  Endpoint - Identify Contact
  URL:POST /contacts/identify/

  Example Request Using Postman:
   Method: POST
   URL: https://identity-reconciliation-3-d0eu.onrender.com/contacts/identify/
   







  
