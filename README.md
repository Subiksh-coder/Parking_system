Description

There should be an admin user by default and other users should have to register before login.
Parking lots has to be created by admin and other users can park and release their vehicles.
The amount the user has to pay depends on the parking lot and the amount of time the vehicle was parked in.


Technologies used
Flask extensions: Flask , render_template , request , redirect , session. Used for redirecting , displaying HTML template , getting data from forms in HTML and session for managing login
Database: used .sqlite file for database for storing login , parking , user details  and sqlite3 module in python to manipulate it 
Frontend: used HTML and used CSS for styling and jinja2 for proper display of data
Modules in python:  datetime for formatting date , matplotlib for giving summary , sqlite3 



DB Schema Design
Parking_lot: id ,INTEGER,PRIMARY KEY AUTOINCREMENT.used for uniquely identifying parking lots.
                      prime_loc_name,TEXT,NOT NULL. This Is the name of a parking lot which can’t be null.
                      max_no_spots,INTEGER,NOTNULL. This is the number of spots in a particular parking lot.
                      price,INTEGER,NOT NULL. this the price per hour for a parking spot in a lot .cant be null
                      pincode,INTEGER,NOT NULL. It is the pincode of parking lot and is not null for a location

parking_spot : id,INTEGER,PRIMARY KEY,AUTOINCREMENT. Used to represent a spot uniquely
                      lot_id,INTEGER,NOT NULL. Id of the lot in which this spot is present
                      status TEXT,CHECK(status IN ('O', 'A')) NOT NULL. Status of the parking
                      FOREIGN KEY (lot_id) REFERENCES parking_lot(id)

users : user_id,INTEGER,PRIMARY KEY,AUTOINCREMENT. Represents a user uniquely
                      username TEXT,NOT NULL.
                      password TEXT NOT NULL

reserve_spot : id,INTEGER,PRIMARY KEY,AUTOINCREMENT. Just for reference purpose
                      spot_id,INTEGER,NOT NULL. References id in table parking_spot
                      user_id,INTEGER,NOT NULL. References user_id in table users
                      parking_time,DATETIME . To store the time of parking in format yyyy-mm-dd H-M-S
                      leave_time,DATETIME . to store leaving time and can be null when vehicle not released
                      vehicle_no,TEXT . To store vehicle number of parked vehicle 
                      FOREIGN KEY (spot_id) REFERENCES parking_spot(id),
                      FOREIGN KEY (user_id) REFERENCES users(user_id)



                      



Architecture and Features

In the root folder of the project there are 2 subfolders which are static and templates. In the static folder the CSS files and images are stored .The templates folder has all the html files required for the web application. There is a file named schema.sql which contains the schema for the specified database. The init_db file is used to create a database file named database.sqlite using the schema in schema.sql. The app.py is the main app which operates and interacts with the web app.

An admin user is already present by default without registering. Admin can create parking lots and give the name, pincode and number of spots in the lot. Admin can delete a lot given that there are no occupied slots in the lot. the number of spots in the lot can be edited after adding. The edited value cannot go below the number of occupied spots in the lot. There is a summary page which shows the amount collected from each of the parking lots which was occupied at least once.
A user who wants to park should have registered with the app once and login to continue. They have the feature to search for parking lots with either pincode or location name. The search gives a list of matched names or pincode from which they can book and the search shows only the spot which has the lowest parking slot id from that lot. Users can book the parking spot by giving their vehicle number. Users can see a summary which shows the amount of time parked in all previously parked lots.
