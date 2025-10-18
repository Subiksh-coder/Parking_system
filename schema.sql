-- Table: parking_lot
CREATE TABLE parking_lot (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prime_loc_name TEXT NOT NULL,
    max_no_spots INTEGER NOT NULL,
    price INTEGER NOT NULL,
    pincode INTEGER NOT NULL
);

-- Table: parking_spot
CREATE TABLE parking_spot (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lot_id INTEGER NOT NULL,
    status TEXT CHECK(status IN ('O', 'A')) NOT NULL,
    FOREIGN KEY (lot_id) REFERENCES parking_lot(id)
);

-- Table: users
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    password TEXT NOT NULL
);

-- Table: reserve_spot
CREATE TABLE reserve_spot (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    spot_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    parking_time DATETIME ,
    leave_time DATETIME ,
    vehicle_no TEXT ,
    FOREIGN KEY (spot_id) REFERENCES parking_spot(id),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
    
);

-- Insert initial user
INSERT INTO users (username, password)
VALUES ('Administrator', 'password');
