// MongoDB initialization script
// Run using: mongo < database_init.js

// Connect to the database
db = db.getSiblingDB('aonix_test');

// Drop existing collections to start fresh
db.users.drop();
db.vehicle_info.drop();
db.violations.drop();
db.violation_record.drop();
db.settings.drop();
db.violation_pictures.drop();
db.vehicle_licence_plate.drop();

// Create users collection
print("Creating users collection...");
db.createCollection("users");

db.users.insertMany([
  {
    "username": "admin",
    "email": "admin@example.com",
    "password": "admin123",
    "role": "admin", 
    "status": true,
    "createdAt": new Date("2023-10-15T10:00:00Z"),
    "lastLogin": new Date("2023-11-25T15:30:45Z"),
    "is_admin": true
  },
  {
    "username": "user1",
    "email": "user1@example.com",
    "password": "user123",
    "role": "user",
    "status": true,
    "createdAt": new Date("2023-10-16T11:20:00Z"),
    "lastLogin": new Date("2023-11-20T09:15:30Z")
  },
  {
    "username": "inspector1",
    "email": "inspector1@example.com",
    "password": "inspector123",
    "role": "inspector",
    "status": true,
    "createdAt": new Date("2023-10-17T09:45:00Z"),
    "lastLogin": new Date("2023-11-24T14:25:10Z")
  },
  {
    "username": "operator1",
    "email": "operator1@example.com",
    "password": "operator123",
    "role": "operator",
    "status": false,
    "createdAt": new Date("2023-10-18T13:30:00Z"),
    "lastLogin": null
  },
  {
    "username": "manager1",
    "email": "manager1@example.com",
    "password": "manager123",
    "role": "admin",
    "status": true,
    "is_admin": true,
    "createdAt": new Date("2023-10-19T16:15:00Z"),
    "lastLogin": new Date("2023-11-22T11:40:20Z")
  }
]);

// Create vehicle_info collection
print("Creating vehicle_info collection...");
db.createCollection("vehicle_info");

db.vehicle_info.insertMany([
  {
    "Name": "John Doe",
    "Licence Plate": "MH-01-AB-1234",
    "Email": "john.doe@example.com",
    "Mobile Number": "9876543210",
    "Vehicle Type": "Car",
    "Model": "Toyota Camry",
    "Year": 2020,
    "Color": "White",
    "Registration Date": new Date("2020-05-15T00:00:00Z")
  },
  {
    "Name": "Jane Smith",
    "Licence Plate": "MH-02-CD-5678",
    "Email": "jane.smith@example.com",
    "Mobile Number": "8765432109",
    "Vehicle Type": "SUV",
    "Model": "Honda CR-V",
    "Year": 2019,
    "Color": "Silver",
    "Registration Date": new Date("2019-11-23T00:00:00Z")
  },
  {
    "Name": "Robert Johnson",
    "Licence Plate": "MH-03-EF-9012",
    "Email": "robert.j@example.com",
    "Mobile Number": "7654321098",
    "Vehicle Type": "Truck",
    "Model": "Ford F-150",
    "Year": 2021,
    "Color": "Black",
    "Registration Date": new Date("2021-02-10T00:00:00Z")
  },
  {
    "Name": "Emily Davis",
    "Licence Plate": "MH-04-GH-3456",
    "Email": "emily.d@example.com",
    "Mobile Number": "6543210987",
    "Vehicle Type": "Sedan",
    "Model": "Hyundai Elantra",
    "Year": 2018,
    "Color": "Red",
    "Registration Date": new Date("2018-08-05T00:00:00Z")
  },
  {
    "Name": "Michael Wilson",
    "Licence Plate": "MH-05-IJ-7890",
    "Email": "michael.w@example.com",
    "Mobile Number": "5432109876",
    "Vehicle Type": "Hatchback",
    "Model": "Maruti Swift",
    "Year": 2022,
    "Color": "Blue",
    "Registration Date": new Date("2022-01-18T00:00:00Z")
  },
  {
    "Name": "Sarah Thompson",
    "Licence Plate": "MH-06-KL-1234",
    "Email": "sarah.t@example.com",
    "Mobile Number": "4321098765",
    "Vehicle Type": "Minivan",
    "Model": "Toyota Innova",
    "Year": 2021,
    "Color": "Grey",
    "Registration Date": new Date("2021-07-25T00:00:00Z")
  },
  {
    "Name": "David Brown",
    "Licence Plate": "MH-07-MN-5678",
    "Email": "david.b@example.com",
    "Mobile Number": "3210987654",
    "Vehicle Type": "SUV",
    "Model": "Mahindra XUV700",
    "Year": 2023,
    "Color": "White",
    "Registration Date": new Date("2023-03-12T00:00:00Z")
  },
  {
    "Name": "Jessica Wilson",
    "Licence Plate": "MH-08-OP-9012",
    "Email": "jessica.w@example.com",
    "Mobile Number": "2109876543",
    "Vehicle Type": "Sedan",
    "Model": "Honda City",
    "Year": 2020,
    "Color": "Black",
    "Registration Date": new Date("2020-09-30T00:00:00Z")
  }
]);

// Create violations collection
print("Creating violations collection...");
db.createCollection("violations");

db.violations.insertMany([
  {
    "License Plate": "MH-01-AB-1234",
    "Name": "John Doe",
    "Violation Date": new Date("2023-11-10T14:35:22Z"),
    "Violation Type": "Speeding",
    "Action Taken": "Warning",
    "Frequency": 1,
    "Speed Limit": 60,
    "Recorded Speed": 75,
    "Location": "Highway 101, Mile 25",
    "Notified": true,
    "Notification Date": new Date("2023-11-10T15:45:10Z")
  },
  {
    "License Plate": "MH-02-CD-5678",
    "Name": "Jane Smith",
    "Violation Date": new Date("2023-11-12T09:20:15Z"),
    "Violation Type": "Red Light",
    "Action Taken": "Fine",
    "Frequency": 2,
    "Location": "Main Street & Oak Avenue",
    "Notified": true,
    "Notification Date": new Date("2023-11-12T10:30:45Z")
  },
  {
    "License Plate": "MH-03-EF-9012",
    "Name": "Robert Johnson",
    "Violation Date": new Date("2023-11-15T17:45:30Z"),
    "Violation Type": "Illegal Parking",
    "Action Taken": "Fine",
    "Frequency": 1,
    "Location": "Central Mall Parking",
    "Notified": true,
    "Notification Date": new Date("2023-11-15T18:50:20Z")
  },
  {
    "License Plate": "MH-04-GH-3456",
    "Name": "Emily Davis",
    "Violation Date": new Date("2023-11-18T11:15:40Z"),
    "Violation Type": "No Seat Belt",
    "Action Taken": "Warning",
    "Frequency": 1,
    "Location": "River Road",
    "Notified": false,
    "Notification Date": null
  },
  {
    "License Plate": "MH-05-IJ-7890",
    "Name": "Michael Wilson",
    "Violation Date": new Date("2023-11-20T08:05:25Z"),
    "Violation Type": "Speeding",
    "Action Taken": "Fine",
    "Frequency": 3,
    "Speed Limit": 40,
    "Recorded Speed": 68,
    "Location": "School Zone, Elementary School",
    "Notified": true,
    "Notification Date": new Date("2023-11-20T09:10:15Z")
  },
  {
    "License Plate": "MH-06-KL-1234",
    "Name": "Sarah Thompson",
    "Violation Date": new Date("2023-11-22T16:30:10Z"),
    "Violation Type": "Wrong Way",
    "Action Taken": "Fine",
    "Frequency": 1,
    "Location": "One Way Street, Downtown",
    "Notified": true,
    "Notification Date": new Date("2023-11-22T17:35:55Z")
  },
  {
    "License Plate": "MH-01-AB-1234",
    "Name": "John Doe",
    "Violation Date": new Date("2023-11-24T12:40:50Z"),
    "Violation Type": "Speeding",
    "Action Taken": "Fine",
    "Frequency": 2,
    "Speed Limit": 50,
    "Recorded Speed": 72,
    "Location": "Broadway Avenue",
    "Notified": false,
    "Notification Date": null
  },
  {
    "License Plate": "MH-07-MN-5678",
    "Name": "David Brown",
    "Violation Date": new Date("2023-11-25T19:55:30Z"),
    "Violation Type": "No Helmet",
    "Action Taken": "Warning",
    "Frequency": 1,
    "Location": "College Road",
    "Notified": true,
    "Notification Date": new Date("2023-11-25T20:45:10Z")
  }
]);

// Create violation_record collection
print("Creating violation_record collection...");
db.createCollection("violation_record");

db.violation_record.insertMany([
  {
    "License Plate": "MH-01-AB-1234",
    "Violation Type": "Speeding",
    "Violation Date": new Date("2023-11-10T14:35:22Z"),
    "Zone": "Highway 101",
    "Location": "Highway 101, Mile 25",
    "Speed Limit": 60,
    "Recorded Speed": 75,
    "Evidence": "cam_01_20231110_143522.jpg",
    "Officer": "John Smith",
    "Notes": "Vehicle was observed traveling significantly above the speed limit in moderate traffic."
  },
  {
    "License Plate": "MH-02-CD-5678",
    "Violation Type": "Red Light",
    "Violation Date": new Date("2023-11-12T09:20:15Z"),
    "Zone": "Main Street",
    "Location": "Main Street & Oak Avenue",
    "Evidence": "cam_03_20231112_092015.jpg",
    "Officer": "Robert Johnson",
    "Notes": "Vehicle proceeded through intersection after signal had turned red."
  },
  {
    "License Plate": "MH-03-EF-9012",
    "Violation Type": "Illegal Parking",
    "Violation Date": new Date("2023-11-15T17:45:30Z"),
    "Zone": "Central Mall",
    "Location": "Central Mall Parking",
    "Evidence": "officer_cam_20231115_174530.jpg",
    "Officer": "Emily Parker",
    "Notes": "Vehicle parked in handicapped spot without proper permit."
  },
  {
    "License Plate": "MH-04-GH-3456",
    "Violation Type": "No Seat Belt",
    "Violation Date": new Date("2023-11-18T11:15:40Z"),
    "Zone": "River Road",
    "Location": "River Road",
    "Evidence": "cam_05_20231118_111540.jpg",
    "Officer": "Michael Wilson",
    "Notes": "Driver observed without seatbelt during routine patrol."
  },
  {
    "License Plate": "MH-05-IJ-7890",
    "Violation Type": "Speeding",
    "Violation Date": new Date("2023-11-20T08:05:25Z"),
    "Zone": "School Zone",
    "Location": "School Zone, Elementary School",
    "Speed Limit": 40,
    "Recorded Speed": 68,
    "Evidence": "cam_02_20231120_080525.jpg",
    "Officer": "Sarah Thompson",
    "Notes": "Vehicle exceeding speed limit in school zone during morning drop-off hours."
  },
  {
    "License Plate": "MH-06-KL-1234",
    "Violation Type": "Wrong Way",
    "Violation Date": new Date("2023-11-22T16:30:10Z"),
    "Zone": "Downtown",
    "Location": "One Way Street, Downtown",
    "Evidence": "cam_04_20231122_163010.jpg",
    "Officer": "David Brown",
    "Notes": "Vehicle traveling in wrong direction on clearly marked one-way street."
  },
  {
    "License Plate": "MH-01-AB-1234",
    "Violation Type": "Speeding",
    "Violation Date": new Date("2023-11-24T12:40:50Z"),
    "Zone": "Broadway Avenue",
    "Location": "Broadway Avenue",
    "Speed Limit": 50,
    "Recorded Speed": 72,
    "Evidence": "cam_06_20231124_124050.jpg",
    "Officer": "Jessica Wilson",
    "Notes": "Second speeding violation this month for this vehicle."
  },
  {
    "License Plate": "MH-07-MN-5678",
    "Violation Type": "No Helmet",
    "Violation Date": new Date("2023-11-25T19:55:30Z"),
    "Zone": "College Road",
    "Location": "College Road",
    "Evidence": "cam_07_20231125_195530.jpg",
    "Officer": "Thomas Anderson",
    "Notes": "Rider observed without helmet during evening patrol."
  },
  {
    "License Plate": "MH-08-OP-9012",
    "Violation Type": "Speeding",
    "Violation Date": new Date("2023-11-26T07:15:40Z"),
    "Zone": "Highway 101",
    "Location": "Highway 101, Mile 32",
    "Speed Limit": 60,
    "Recorded Speed": 82,
    "Evidence": "cam_01_20231126_071540.jpg",
    "Officer": "John Smith",
    "Notes": "Vehicle speeding in light traffic conditions."
  },
  {
    "License Plate": "MH-02-CD-5678",
    "Violation Type": "No Stop",
    "Violation Date": new Date("2023-11-28T15:25:20Z"),
    "Zone": "Residential Area",
    "Location": "Pine Street & Maple Avenue",
    "Evidence": "cam_08_20231128_152520.jpg",
    "Officer": "Amanda Lee",
    "Notes": "Vehicle failed to stop at stop sign in residential area."
  }
]);

// Create settings collection
print("Creating settings collection...");
db.createCollection("settings");

db.settings.insertOne({
  "max_speed": 60,
  "notification_template": "Dear {owner_name},\n\nYour vehicle with license plate {license_plate} has been involved in a {violation_type} violation on {violation_date} at {violation_time}.\n\nLocation: {location}\nFrequency: {frequency}\n\nPlease drive safely.\n\nRegards,\nTraffic Management System",
  "email_settings": {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "smtp_username": "traffic.notification@example.com",
    "smtp_password": "examplepassword123"
  },
  "updated_at": new Date("2023-11-15T10:30:00Z"),
  "system_settings": {
    "violation_retention_days": 365,
    "automatic_notification": true,
    "daily_report_enabled": true,
    "report_recipients": ["admin@example.com", "manager@example.com"]
  },
  "speed_thresholds": {
    "residential": 30,
    "school_zone": 20,
    "highway": 65,
    "downtown": 40
  }
});

// Create violation_pictures collection
print("Creating violation_pictures collection...");
db.createCollection("violation_pictures");

db.violation_pictures.insertMany([
  {
    "file_path": "violations/cam_01_20231110_143522.jpg",
    "processed": true,
    "timestamp": new Date("2023-11-10T14:35:22Z")
  },
  {
    "file_path": "violations/cam_03_20231112_092015.jpg",
    "processed": true,
    "timestamp": new Date("2023-11-12T09:20:15Z")
  },
  {
    "file_path": "violations/officer_cam_20231115_174530.jpg",
    "processed": true,
    "timestamp": new Date("2023-11-15T17:45:30Z")
  },
  {
    "file_path": "violations/cam_05_20231118_111540.jpg",
    "processed": true,
    "timestamp": new Date("2023-11-18T11:15:40Z")
  },
  {
    "file_path": "violations/cam_02_20231120_080525.jpg",
    "processed": true,
    "timestamp": new Date("2023-11-20T08:05:25Z")
  },
  {
    "file_path": "violations/cam_04_20231122_163010.jpg",
    "processed": true,
    "timestamp": new Date("2023-11-22T16:30:10Z")
  },
  {
    "file_path": "violations/cam_06_20231124_124050.jpg",
    "processed": true,
    "timestamp": new Date("2023-11-24T12:40:50Z")
  },
  {
    "file_path": "violations/cam_07_20231125_195530.jpg",
    "processed": true,
    "timestamp": new Date("2023-11-25T19:55:30Z")
  },
  {
    "file_path": "violations/cam_01_20231126_071540.jpg",
    "processed": true,
    "timestamp": new Date("2023-11-26T07:15:40Z")
  },
  {
    "file_path": "violations/cam_08_20231128_152520.jpg",
    "processed": true,
    "timestamp": new Date("2023-11-28T15:25:20Z")
  },
  {
    "file_path": "violations/cam_09_20231129_103045.jpg",
    "processed": false,
    "timestamp": new Date("2023-11-29T10:30:45Z")
  }
]);

// Create vehicle_licence_plate collection
print("Creating vehicle_licence_plate collection...");
db.createCollection("vehicle_licence_plate");

// Insert some data, create ObjectIds for references
let pic1 = db.violation_pictures.findOne({"file_path": "violations/cam_01_20231110_143522.jpg"})._id;
let pic2 = db.violation_pictures.findOne({"file_path": "violations/cam_03_20231112_092015.jpg"})._id;
let pic3 = db.violation_pictures.findOne({"file_path": "violations/officer_cam_20231115_174530.jpg"})._id;
let pic4 = db.violation_pictures.findOne({"file_path": "violations/cam_05_20231118_111540.jpg"})._id;
let pic5 = db.violation_pictures.findOne({"file_path": "violations/cam_02_20231120_080525.jpg"})._id;
let pic6 = db.violation_pictures.findOne({"file_path": "violations/cam_04_20231122_163010.jpg"})._id;
let pic7 = db.violation_pictures.findOne({"file_path": "violations/cam_06_20231124_124050.jpg"})._id;
let pic8 = db.violation_pictures.findOne({"file_path": "violations/cam_07_20231125_195530.jpg"})._id;
let pic9 = db.violation_pictures.findOne({"file_path": "violations/cam_01_20231126_071540.jpg"})._id;
let pic10 = db.violation_pictures.findOne({"file_path": "violations/cam_08_20231128_152520.jpg"})._id;

db.vehicle_licence_plate.insertMany([
  {
    "license_plate": "MH-01-AB-1234",
    "image_path": "violations/cam_01_20231110_143522.jpg",
    "violation_id": pic1,
    "timestamp": new Date("2023-11-10T14:35:30Z"),
    "confidence_score": 0.98
  },
  {
    "license_plate": "MH-02-CD-5678",
    "image_path": "violations/cam_03_20231112_092015.jpg",
    "violation_id": pic2,
    "timestamp": new Date("2023-11-12T09:20:25Z"),
    "confidence_score": 0.95
  },
  {
    "license_plate": "MH-03-EF-9012",
    "image_path": "violations/officer_cam_20231115_174530.jpg",
    "violation_id": pic3,
    "timestamp": new Date("2023-11-15T17:45:40Z"),
    "confidence_score": 0.99
  },
  {
    "license_plate": "MH-04-GH-3456",
    "image_path": "violations/cam_05_20231118_111540.jpg",
    "violation_id": pic4,
    "timestamp": new Date("2023-11-18T11:15:55Z"),
    "confidence_score": 0.94
  },
  {
    "license_plate": "MH-05-IJ-7890",
    "image_path": "violations/cam_02_20231120_080525.jpg",
    "violation_id": pic5,
    "timestamp": new Date("2023-11-20T08:05:35Z"),
    "confidence_score": 0.97
  },
  {
    "license_plate": "MH-06-KL-1234",
    "image_path": "violations/cam_04_20231122_163010.jpg",
    "violation_id": pic6,
    "timestamp": new Date("2023-11-22T16:30:25Z"),
    "confidence_score": 0.96
  },
  {
    "license_plate": "MH-01-AB-1234",
    "image_path": "violations/cam_06_20231124_124050.jpg",
    "violation_id": pic7,
    "timestamp": new Date("2023-11-24T12:41:05Z"),
    "confidence_score": 0.97
  },
  {
    "license_plate": "MH-07-MN-5678",
    "image_path": "violations/cam_07_20231125_195530.jpg",
    "violation_id": pic8,
    "timestamp": new Date("2023-11-25T19:55:45Z"),
    "confidence_score": 0.93
  },
  {
    "license_plate": "MH-08-OP-9012",
    "image_path": "violations/cam_01_20231126_071540.jpg",
    "violation_id": pic9,
    "timestamp": new Date("2023-11-26T07:15:55Z"),
    "confidence_score": 0.98
  },
  {
    "license_plate": "MH-02-CD-5678",
    "image_path": "violations/cam_08_20231128_152520.jpg",
    "violation_id": pic10,
    "timestamp": new Date("2023-11-28T15:25:35Z"),
    "confidence_score": 0.96
  }
]);

// Create indexes for better performance
db.users.createIndex({ "email": 1 }, { unique: true });
db.vehicle_info.createIndex({ "Licence Plate": 1 }, { unique: true });
db.violations.createIndex({ "License Plate": 1, "Violation Date": 1 });
db.violation_record.createIndex({ "License Plate": 1 });
db.violation_record.createIndex({ "Violation Date": 1 });
db.violation_record.createIndex({ "Zone": 1 });
db.violation_pictures.createIndex({ "file_path": 1 }, { unique: true });
db.vehicle_licence_plate.createIndex({ "license_plate": 1 });
db.vehicle_licence_plate.createIndex({ "violation_id": 1 });

print("Database initialization complete!"); 