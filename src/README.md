# Mergington High School Activities API

A super simple FastAPI application that allows students to view and sign up for extracurricular activities.

## Features

- View all available extracurricular activities
- Sign up for activities
- Manage school announcements (teachers only)

## Getting Started

1. Install the dependencies:

   ```
   pip install fastapi uvicorn pymongo argon2-cffi
   ```

2. Start MongoDB (required for data persistence):

   ```
   mongod --dbpath /path/to/data
   ```

3. Run the application:

   ```
   uvicorn src.app:app --reload
   ```

4. Open your browser and go to:
   - API documentation: http://localhost:8000/docs
   - Alternative documentation: http://localhost:8000/redoc

## API Endpoints

### Activities

| Method | Endpoint                                                          | Description                                                         |
| ------ | ----------------------------------------------------------------- | ------------------------------------------------------------------- |
| GET    | `/activities`                                                     | Get all activities with their details and current participant count |
| POST   | `/activities/{activity_name}/signup?email=student@mergington.edu` | Sign up for an activity                                             |

### Authentication

| Method | Endpoint              | Description                        |
| ------ | --------------------- | ---------------------------------- |
| POST   | `/auth/login`         | Login with teacher credentials     |
| GET    | `/auth/check-session` | Validate an existing user session  |

### Announcements

| Method | Endpoint                      | Description                                              |
| ------ | ----------------------------- | -------------------------------------------------------- |
| GET    | `/announcements/`             | Get active announcements (use `include_inactive=true` for all) |
| GET    | `/announcements/{id}`         | Get a specific announcement by ID                        |
| POST   | `/announcements/`             | Create a new announcement (requires teacher auth)        |
| PUT    | `/announcements/{id}`         | Update an announcement (requires teacher auth)           |
| DELETE | `/announcements/{id}`         | Delete an announcement (requires teacher auth)           |

## Data Model

The application uses MongoDB for data persistence:

1. **Activities** - Uses activity name as identifier:

   - Description
   - Schedule
   - Maximum number of participants allowed
   - List of student emails who are signed up

2. **Teachers** - Uses username as identifier:
   - Display name
   - Hashed password (Argon2)
   - Role (teacher/admin)

3. **Announcements** - Uses ObjectId as identifier:
   - Message content
   - Start date (optional - for scheduling future announcements)
   - Expiration date (required)
   - Created by (teacher username)
   - Created at timestamp
   - Active status (boolean)

## Default Teacher Accounts

| Username  | Password  | Role    |
| --------- | --------- | ------- |
| mrodriguez| art123    | teacher |
| mchen     | chess456  | teacher |
| principal | admin789  | admin   |
