🎬 ReelTime – Movie Reservation System

ReelTime is a web-based movie reservation system built with a Django backend and a React frontend. The platform provides users with a seamless experience to browse movie schedules, book tickets, and select seats in real time. An admin panel allows administrators to manage movies, showtimes, seats, and user bookings efficiently.

🚀 Features
🔑 Authentication

User registration and login with secure authentication

Session-based or token-based access control

🎥 Movie Schedules & Booking

Browse available movies and showtimes

Select preferred showtime and book tickets

🪑 Interactive Seat Selection

Real-time seat availability updates

Intuitive seat map for booking

⚙️ Admin Panel

Add, update, and remove movies

Manage showtimes and schedules

Configure seat layouts and availability

Monitor and manage user bookings

🗄️ Database Integration

Stores user information, movies, showtimes, and reservations

Ensures consistency between frontend and backend data

🛠️ Tech Stack

Frontend: React, TailwindCSS / Material-UI (customizable)
Backend: Django (Django REST Framework for APIs)
Database: PostgreSQL / MySQL / SQLite (development)
Authentication: Django Auth


📂 Project Structure
ReelTime/
│── backend/           # Django project (API + Admin)
│   ├── movies/        # Movies, schedules, bookings apps
│   ├── users/         # Authentication & user management
│   ├── settings.py    # Django settings
│
│── frontend/          # React app
│   ├── src/
│   │   ├── components/ # Reusable UI components
│   │   ├── pages/      # Login, Movies, Booking, Admin
│   │   ├── services/   # API calls
│   │   └── App.js
│
│── docs/              # Documentation
│── README.md

⚡ Installation & Setup
🔹 Prerequisites

Python 3.10+

Node.js 16+

PostgreSQL (or SQLite for dev)

🔹 Backend Setup (Django)
cd backend
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver

🔹 Frontend Setup (React)
cd frontend
npm install
npm start


The React app will run on http://localhost:3000 and the Django API on http://localhost:8000.

📖 User Guide
👤 For Users

Register or log in to your account

Browse movies and showtimes

Select your movie and schedule

Choose seats using the interactive seat map

Confirm and pay for your booking (payment integration optional)

View booking history in your profile

👨‍💼 For Admins

Log in with admin credentials

Access the Admin Dashboard

Add new movies, edit details, and set showtimes

Configure seat availability and layouts

Manage user bookings and monitor activity

🗒️ Future Enhancements

Online payment gateway integration (Stripe/PayPal)

Push/email notifications for booking confirmation

Mobile app (React Native) support

Advanced analytics dashboard for admins

🤝 Contributing

Fork the repository

Create your feature branch (git checkout -b feature-name)

Commit changes (git commit -m "Add feature")

Push to branch (git push origin feature-name)

Open a Pull Request

📜 License

This project was created by Project Management Team G2 and Development Team G6 as part of our coursework.
