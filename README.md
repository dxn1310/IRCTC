# IRCTC
## Tech Stack Used:
- Python Django
- MySQL
- Rest Framework
- JSON Web Token

## Database Schema:
### Tables - User, Train, Booking

### User:
name : string <br/>
email : string <br/>
password : string <br/>

### Train:
name : string <br/>
source : string <br/>
destination : string <br/>
seats_avaliable : int <br/>

### Booking:
booking_id : int <br/>
name : string <br/>
train_name : string <br/>
seats_number : int <br/>
booking_time : Date

## API Endpoints:
### User Authentication:
- api/register (POST)
  - Adds a new user to user table
  - Request {name, email, password}
  - Response {user}
- api/login (POST)
  - To login with username and password
  - Request {username, password}
  - Response {jwt token}
- api/user (GET)
  - To display user details
  - Response {user}
- api/logout (POST)
  - To logout user
  - Response {message}

### Trains
- api/add_train (POST)
  - To add new train
  - Access only to admins
  - Request {name, soure, destination, seats}
  - Response {message}
- api/train/get_train (GET)
  - To get train details
  - Request {train_name}
  - Response {train}
- api/train/get_seat_availability (GET)
  - To get list of trains between source and destination
  - Request {source, destination}
  - Response {trains[]}

### Booking
- api/book_seat (POST)
  - To book a train seat
  - Request {train_name}
  - Response {message}
- api/get_booking (GET)
  - To get train seat booking details
  - Request {booking_id}
  - Response {booking}

## Installation and running the server
- Start virtual environment
- Install the required libraries with `pip install -r requirements.txt`
- Start MySQL server to connect database and tables
