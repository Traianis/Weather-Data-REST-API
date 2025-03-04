# Weather Data REST API

This is a REST API for managing weather data, built with Flask and PostgreSQL, and containerized using Docker.

## Features
- Manage **countries** (add, update, delete, list).
- Manage **cities** linked to countries.
- Store and retrieve **temperature records** for cities.
- Uses **PostgreSQL** for data persistence.
- Includes **PgAdmin** for database management.
- Fully containerized with **Docker & Docker Compose**.

---

## Getting Started

### Prerequisites
Make sure you have the following installed on your machine:
- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

### Installation
1. Clone this repository:
   ```bash
   git clone https://github.com/your-username/traianis-weather-data-rest-api.git
   cd traianis-weather-data-rest-api
   ```

2. Build and run the application using Docker:
   ```bash
   sudo docker compose up --build
   ```
   **Note:** Ensure that ports `5432`, `8080`, and `6000` are not in use.

---

## API Endpoints

### 1. Countries
- **Add a country**
  ```http
  POST /api/countries
  ```
  **Request Body:**
  ```json
  {
    "nume": "Romania",
    "lat": 45.9432,
    "lon": 24.9668
  }
  ```
- **Get all countries**
  ```http
  GET /api/countries
  ```
- **Update a country**
  ```http
  PUT /api/countries/{id}
  ```
- **Delete a country**
  ```http
  DELETE /api/countries/{id}
  ```

### 2. Cities
- **Add a city**
  ```http
  POST /api/cities
  ```
- **Get all cities**
  ```http
  GET /api/cities
  ```
- **Get cities by country**
  ```http
  GET /api/cities/country/{id}
  ```

### 3. Temperatures
- **Add a temperature record**
  ```http
  POST /api/temperatures
  ```
- **Get all temperature records**
  ```http
  GET /api/temperatures
  ```
- **Filter temperature records by city**
  ```http
  GET /api/temperatures/cities/{id}
  ```
- **Filter temperature records by country**
  ```http
  GET /api/temperatures/countries/{id}
  ```

---

## Database Setup
The database is initialized automatically by the application. It includes the following tables:
- **Countries (`Tari`)**: Stores country names and coordinates.
- **Cities (`Orase`)**: Stores city names, linked to a country.
- **Temperatures (`Temperaturi`)**: Stores temperature values for cities, along with timestamps.

---

## Running Without Docker
If you prefer running the application manually:

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Set up a PostgreSQL database manually and update the connection details in `api.py`.
3. Run the Flask server:
   ```bash
   python api.py
   ```

---

## Admin Panel (PgAdmin)
To manage the database via **PgAdmin**, open your browser and navigate to:
```
http://localhost:8080
```
Login Credentials:
- **Email:** `admin@test.com`
- **Password:** `admin`

---

## Environment Variables
These values are set in `docker-compose.yml`:
- `POSTGRES_USER=admin`
- `POSTGRES_PASSWORD=admin`
- `POSTGRES_DB=temperatures`

---

## Technologies Used
- **Flask** (Python web framework)
- **PostgreSQL** (Relational database)
- **PgAdmin** (Database management tool)
- **SQLAlchemy** (ORM for database interactions)
- **Docker & Docker Compose** (Containerization)

---

## License
This project is licensed under the MIT License.
