# Tiffany Voorhees OHS Project

## Overview

The **Tiffany Voorhees OHS** project is designed to be a place for Rowley family and friends to track orders for Optimal Health System products. 
This project aims to allow a place for the Rowley family to track master orders and the user orders that make up the master order.

## Project Structure
tiffanyvoorhees_ohs/
├── frontend/ # React app (created with Create React App)
├── main/ # Django app
├── react_build/ # Output folder for React static files
├── tiffanyvoorhees_ohs/ # Core Django
├── venv/ # Python virtual environment (not tracked by Git)
├── .gitignore
├── copy_react_build.py # Script to move React build into Django
├── manage.py # Django CLI entry point
├── README.md

## How to Run the Project Locally

### Prerequisites
- Python 3.10+
- Node.js & npm
- (Recommended) Virtual environment for Python

### Clone the Repo
1. Clone the repository:
   ```bash
   git clone https://github.com/tiffanyvoorhees2500/tiffanyvoorhees_ohs_django_react.git
   ```
2. Navigate to the project directory:
   ```bash
   cd tiffanyvoorhees_ohs
   ```

## Backend (Django)

# Set up virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt  # if you have one
# or manually install as needed:
pip install django

# Run migrations
python manage.py migrate

# Start the server
python manage.py runserver

## Frontend (React)
cd frontend
npm install
npm start


## License

This project currently does **not** have an open-source license.  
All rights reserved.  
You may not use, copy, modify, or distribute this code without explicit permission from the author.

## Contact

For any questions or feedback, please contact Tiffany Voorhees at tiffster2500@gmail.com.