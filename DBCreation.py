from pymongo import MongoClient
from bson.objectid import ObjectId

client = MongoClient('localhost', 27017)#make sure had ra9m correct mlli tfta7 compass

db = client.location_voitures

users = db.users

users.insert_one({'name': 'John', 'email': 'John123@gmail.com', 'password': '123', 'role': 'admin', 'state': 'active', 'created_at': '2024-04-01'})
users.insert_one({'name': 'Jane', 'email': 'Jane123@gmail.com', 'password': '123', 'role': 'manager', 'state': 'active', 'created_at': '2024-04-02'})
users.insert_one({'name': 'Alice', 'email': 'Alice123@gmail.com', 'password': '123', 'role': 'manager', 'state': 'active', 'created_at': '2024-04-03'})
users.insert_one({'name': 'Bob', 'email': 'Bob123@gmail.com', 'password': '123', 'role': 'manager', 'state': 'active', 'created_at': '2024-04-04'})
users.insert_one({'name': 'Eva', 'email': 'Eva123@gmail.com', 'password': '123', 'role': 'manager', 'state': 'active', 'created_at': '2024-04-05'})

print('Users added successfully')

clients = db.clients

clients.insert_one({ 'name': 'Alice Johnson', 'CIN':'AB123456', 'email': 'alice.johnson@gmail.com', 'phone': '07 34 56 78 90', 'address': '123 Main Street, City','state': 'active'})
clients.insert_one({ 'name': 'Bob Williams', 'CIN': 'CD789012', 'email': 'bob.williams@gmail.com', 'phone': '07 45 67 89 01', 'address': '456 Elm Street, Town','state': 'active'})
clients.insert_one({ 'name': 'Charlie Brown', 'CIN': 'EF345678', 'email': 'charlie.brown@gmail.com', 'phone': '07 56 78 90 12', 'address': '789 Oak Avenue, Village','state': 'active'})
clients.insert_one({ 'name': 'David Miller', 'CIN': 'GH901234', 'email': 'david.miller@gmail.com', 'phone': '07 67 89 01 23', 'address': '321 Maple Drive, County','state': 'active'})
clients.insert_one({ 'name': 'Ella Martinez', 'CIN': 'IJ567890', 'email': 'ella.martinez@gmail.com', 'phone': '07 78 90 12 34', 'address': '654 Pine Road, State','state': 'active'})

print('Clients added successfully')

cars = db.cars

cars.insert_one({ 'brand': 'Toyota', 'model': 'Corolla', 'year': 2019, 'color': 'White', 'mileage': 5000, 'price': 20000, 'status': 'available', 'image': 'car-2.jpg' ,'state': 'active'})
cars.insert_one({ 'brand': 'Toyota', 'model': 'Camry', 'year': 2018, 'color': 'Black', 'mileage': 6000, 'price': 25000, 'status': 'available', 'image': 'car-6.jpg' ,'state': 'active'})
cars.insert_one({ 'brand': 'Toyota', 'model': 'RAV4', 'year': 2017, 'color': 'Red', 'mileage': 7000, 'price': 30000, 'status': 'available', 'image': 'car-8.jpg','state': 'active'})
cars.insert_one({ 'brand': 'Toyota', 'model': 'Highlander', 'year': 2016, 'color': 'Blue', 'mileage': 8000, 'price': 35000, 'status': 'available', 'image': 'car-10.jpg','state': 'active'})
cars.insert_one({ 'brand': 'Toyota', 'model': 'Land Cruiser', 'year': 2015, 'color': 'Green', 'mileage': 9000, 'price': 40000, 'status': 'available', 'image': 'image_3.jpg','state': 'active'})

print('Cars added successfully')



reservations = db.reservations

reservations.insert_one({'car_id':'6643a82b8dc778fbad202c57' ,'client_id': '6643a82b8dc778fbad202c52','reservation_date': '2024-04-01' ,'start_date': '2024-04-10', 'end_date': '2024-04-20', 'status': 'validée'})
reservations.insert_one({ 'car_id':'6643a82b8dc778fbad202c57' ,'client_id': '6643a82b8dc778fbad202c52','reservation_date': '2024-04-01', 'start_date': '2024-04-10', 'end_date': '2024-04-20', 'status': 'refusée', 'reason': 'car not available'})
reservations.insert_one({ 'car_id':'6643a82b8dc778fbad202c57' ,'client_id': '6643a82b8dc778fbad202c52','reservation_date': '2024-04-03', 'start_date': '2024-04-14', 'end_date': '2024-04-24', 'status': 'validée'})
reservations.insert_one({ 'car_id':'6643a82b8dc778fbad202c57' ,'client_id': '6643a82b8dc778fbad202c52', 'reservation_date': '2024-04-04', 'start_date': '2024-04-16', 'end_date': '2024-04-26', 'status': 'refusée', 'reason': 'car not available'})
reservations.insert_one({ 'car_id':'6643a82b8dc778fbad202c57' ,'client_id': '6643a82b8dc778fbad202c52','reservation_date': '2024-04-05', 'start_date': '2024-04-18', 'end_date': '2024-04-28', 'status': 'en attente'})

print('Reservations added successfully')

