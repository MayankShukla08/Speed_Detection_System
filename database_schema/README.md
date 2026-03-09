# AONIX - Traffic Management System Database Schema

This directory contains the MongoDB database schema for the Traffic Management System application. The application uses MongoDB as its database, with the following collections.

## Database: `aonix_test`

### Collections Overview

1. **users**
   - Stores user account information for administrators, operators, and other system users.
   - Key fields: username, email, password, role, status

2. **vehicle_info**
   - Contains registered vehicle information.
   - Key fields: Name (owner), Licence Plate, Email, Mobile Number

3. **violations**
   - Stores traffic violation data that has been processed and confirmed.
   - Key fields: License Plate, Violation Type, Violation Date, Action Taken, Frequency

4. **violation_record**
   - Contains detailed records of all violations, including those that may not have been processed yet.
   - Key fields: License Plate, Violation Type, Violation Date, Zone, Evidence

5. **settings**
   - Stores system-wide configuration settings.
   - Key fields: notification_template, max_speed, email_settings

6. **violation_pictures**
   - Stores metadata about violation evidence images.
   - Key fields: file_path, processed, timestamp

7. **vehicle_licence_plate**
   - Maps detected license plates to violation images.
   - Key fields: license_plate, image_path, violation_id, confidence_score

## Field Types and Descriptions

### users
- `_id`: ObjectId - Unique identifier
- `username`: String - User's display name
- `email`: String - User's email address (used for login)
- `password`: String - User's password (should be hashed in production)
- `role`: String - User role (admin, user, inspector, operator)
- `status`: Boolean - Whether the user account is active
- `is_admin`: Boolean - Whether the user has admin privileges
- `createdAt`: Date - When the account was created
- `lastLogin`: Date - When the user last logged in

### vehicle_info
- `_id`: ObjectId - Unique identifier
- `Name`: String - Vehicle owner's name
- `Licence Plate`: String - Vehicle license plate number
- `Email`: String - Owner's email address
- `Mobile Number`: String - Owner's contact number
- `Vehicle Type`: String - Type of vehicle (Car, SUV, Truck, etc.)
- `Model`: String - Vehicle model
- `Year`: Number - Manufacturing year
- `Color`: String - Vehicle color
- `Registration Date`: Date - When the vehicle was registered

### violations
- `_id`: ObjectId - Unique identifier
- `License Plate`: String - Vehicle license plate number
- `Name`: String - Driver/owner name
- `Violation Date`: Date - When the violation occurred
- `Violation Type`: String - Type of violation (Speeding, Red Light, etc.)
- `Action Taken`: String - Enforcement action (Warning, Fine)
- `Frequency`: Number - Number of times this violation has occurred
- `Speed Limit`: Number - Posted speed limit (for speeding violations)
- `Recorded Speed`: Number - Detected vehicle speed (for speeding violations)
- `Location`: String - Where the violation occurred
- `Notified`: Boolean - Whether the owner has been notified
- `Notification Date`: Date - When the notification was sent

### violation_record
- `_id`: ObjectId - Unique identifier
- `License Plate`: String - Vehicle license plate number
- `Violation Type`: String - Type of violation
- `Violation Date`: Date - When the violation occurred
- `Zone`: String - Traffic zone where violation occurred
- `Location`: String - Specific location
- `Speed Limit`: Number - Posted speed limit (optional)
- `Recorded Speed`: Number - Detected vehicle speed (optional)
- `Evidence`: String - Filename of photo evidence
- `Officer`: String - Officer who recorded or validated the violation
- `Notes`: String - Additional details about the violation

### settings
- `_id`: ObjectId - Unique identifier
- `max_speed`: Number - Global maximum speed limit
- `notification_template`: String - Email template for violation notifications
- `email_settings`: Object - SMTP server configuration
  - `smtp_server`: String - SMTP server address
  - `smtp_port`: Number - SMTP port
  - `smtp_username`: String - SMTP username
  - `smtp_password`: String - SMTP password
- `updated_at`: Date - When settings were last updated
- `system_settings`: Object - Additional system configuration
- `speed_thresholds`: Object - Speed limits for different zones

### violation_pictures
- `_id`: ObjectId - Unique identifier
- `file_path`: String - Path to the violation image
- `processed`: Boolean - Whether the image has been processed
- `timestamp`: Date - When the image was captured

### vehicle_licence_plate
- `_id`: ObjectId - Unique identifier
- `license_plate`: String - Detected license plate number
- `image_path`: String - Path to the source image
- `violation_id`: ObjectId - Reference to violation_pictures collection
- `timestamp`: Date - When the license plate was detected
- `confidence_score`: Number - Confidence level of license plate detection

## Relationships

1. Vehicle violations are linked to vehicle info by License Plate
2. violation_record entries may become violations after processing
3. violation_pictures stores images that are referenced in violation_record
4. vehicle_licence_plate links detected plates to violation images

## Sample Usage

To import this sample data into MongoDB:

```bash
# For each collection file
mongoimport --db aonix_test --collection users --file users.json --jsonArray
mongoimport --db aonix_test --collection vehicle_info --file vehicle_info.json --jsonArray
...
``` 