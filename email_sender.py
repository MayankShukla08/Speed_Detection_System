from typing import List, Dict
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
import time
import os
import re

class ViolationEmailSender:
    def __init__(self, smtp_server: str, smtp_port: int, sender_email: str, sender_password: str, email_subject: str = None, email_template: str = None):
        """
        Initialize the email sender with SMTP settings
        
        Args:
            smtp_server: SMTP server address (e.g., 'smtp.gmail.com')
            smtp_port: SMTP port (e.g., 587 for TLS)
            sender_email: Email address to send from
            sender_password: Password or app-specific password for the email account
            email_subject: Custom email subject (optional)
            email_template: Custom email template (optional)
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.email_subject = email_subject or "Speed Violation Notice"
        self.email_template = email_template
        self.logger = self._setup_logger()
        
        # Validate that the sender email is the one with credentials
        self._validate_sender_credentials()

    def _setup_logger(self) -> logging.Logger:
        """Set up logging configuration"""
        logger = logging.getLogger('ViolationEmailSender')
        logger.setLevel(logging.INFO)
        
        # Check if handler already exists to avoid duplicate handlers
        if not logger.handlers:
            # Create logs directory if it doesn't exist
            os.makedirs('logs', exist_ok=True)
            handler = logging.FileHandler('logs/email_sender.log')
            handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
            logger.addHandler(handler)
        
        return logger

    def _validate_sender_credentials(self):
        """Validate sender email credentials by attempting to login"""
        try:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            server.quit()
            self.logger.info(f"Successfully validated credentials for {self.sender_email}")
        except Exception as e:
            error_msg = f"Failed to validate sender email credentials: {str(e)}"
            self.logger.error(error_msg)
            raise ValueError(error_msg)

    def _parse_template(self, template: str, violation_data: Dict) -> str:
        """
        Parse template with more flexible placeholder handling
        
        This method supports both {placeholder} and {{placeholder}} formats
        and provides fallback values for missing keys
        """
        if not template:
            return self._create_default_message(violation_data)
            
        # First, try the standard format method
        try:
            return template.format(**violation_data)
        except KeyError as e:
            self.logger.warning(f"Missing key in template: {e}, trying fallback method")
            
            # Fallback to custom replacement with default values
            result = template
            
            # Find all placeholders in the format {placeholder}
            placeholders = re.findall(r'\{([^}]+)\}', template)
            
            for placeholder in placeholders:
                value = violation_data.get(placeholder, f"[{placeholder}]")
                result = result.replace(f"{{{placeholder}}}", str(value))
                
            return result

    def _create_default_message(self, violation_data: Dict) -> str:
        """Create a default message when no template is provided"""
        return f"""Dear {violation_data.get('owner_name', 'Vehicle Owner')},

This is to inform you that your vehicle with license plate {violation_data.get('license_plate', 'Unknown')} 
has been involved in a {violation_data.get('violation_type', 'traffic')} violation 
on {violation_data.get('violation_date', 'recent date')} at {violation_data.get('violation_time', '')}.

Location: {violation_data.get('location', 'Not specified')}
Frequency: {violation_data.get('frequency', '1')}

Please ensure compliance with traffic regulations for everyone's safety.

Best regards,
Traffic Management System"""

    def _create_email_message(self, violation_data: Dict) -> str:
        """
        Create email content from template and violation data
        """
        if self.email_template:
            return self._parse_template(self.email_template, violation_data)
        else:
            return self._create_default_message(violation_data)

    def send_single_violation(self, violation_data: Dict) -> bool:
        """
        Send a single violation email
        
        Args:
            violation_data: Dictionary containing violation details
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        server = None
        try:
            if not all(key in violation_data for key in ['owner_email', 'owner_name', 'license_plate', 'speed_limit', 'recorded_speed', 'violation_date', 'violation_time', 'location']):
                self.logger.error(f"Missing required data in violation: {violation_data}")
                return False

            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.sender_email, self.sender_password)

            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = violation_data['owner_email']
            msg['Subject'] = f"{self.email_subject} - {violation_data['license_plate']}"

            email_body = self._create_email_message(violation_data)
            msg.attach(MIMEText(email_body, 'plain'))

            server.send_message(msg)
            self.logger.info(f"Successfully sent email to {violation_data['owner_email']}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to send email to {violation_data['owner_email']}: {str(e)}")
            return False
        finally:
            if server:
                server.quit()

    def send_bulk_violations(self, violations: List[Dict]) -> Dict[str, List]:
        successful = []
        failed = []
        
        if not violations:
            self.logger.warning("No violations to send")
            return {'successful': successful, 'failed': failed}
            
        self.logger.info(f"Attempting to send {len(violations)} violation emails")
        
        # Group emails by recipient to avoid sending multiple emails to the same person
        recipient_groups = {}
        for violation in violations:
            if 'owner_email' not in violation:
                self.logger.error(f"Missing owner_email in violation: {violation}")
                failed.append(violation.get('license_plate', 'Unknown'))
                continue
                
            email = violation['owner_email']
            if email not in recipient_groups:
                recipient_groups[email] = []
            recipient_groups[email].append(violation)
        
        try:
            # Connect to SMTP server
            self.logger.info(f"Connecting to SMTP server {self.smtp_server}:{self.smtp_port}")
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.set_debuglevel(1)  # Enable debug output
            server.starttls()
            
            # Login
            self.logger.info(f"Logging in as {self.sender_email}")
            server.login(self.sender_email, self.sender_password)
            
            # Process each recipient
            for recipient, recipient_violations in recipient_groups.items():
                try:
                    self.logger.info(f"Preparing email for {recipient} with {len(recipient_violations)} violations")
                    
                    # Create message
                    msg = MIMEMultipart()
                    msg['From'] = self.sender_email
                    msg['To'] = recipient
                    
                    # If multiple violations, use a summary subject
                    if len(recipient_violations) > 1:
                        msg['Subject'] = f"{self.email_subject} - Multiple Violations ({len(recipient_violations)})"
                    else:
                        msg['Subject'] = f"{self.email_subject} - {recipient_violations[0].get('license_plate', 'Unknown')}"
                    
                    # Create body - for multiple violations, combine them
                    if len(recipient_violations) > 1:
                        email_body = f"Dear {recipient_violations[0].get('owner_name', 'Vehicle Owner')},\n\n"
                        email_body += f"This is to inform you about {len(recipient_violations)} traffic violations:\n\n"
                        
                        for i, violation in enumerate(recipient_violations, 1):
                            email_body += f"Violation #{i}:\n"
                            email_body += f"- License Plate: {violation.get('license_plate', 'Unknown')}\n"
                            email_body += f"- Type: {violation.get('violation_type', 'Traffic violation')}\n"
                            email_body += f"- Date: {violation.get('violation_date', 'Unknown')} {violation.get('violation_time', '')}\n"
                            email_body += f"- Location: {violation.get('location', 'Not specified')}\n\n"
                            
                        email_body += "Please ensure compliance with traffic regulations for everyone's safety.\n\n"
                        email_body += "Best regards,\nTraffic Management System"
                    else:
                        # Single violation - use the template
                        email_body = self._create_email_message(recipient_violations[0])
                    
                    msg.attach(MIMEText(email_body, 'plain'))
                    
                    # Send message
                    self.logger.info(f"Sending email to {recipient}")
                    server.send_message(msg)
                    
                    # Add small delay to avoid rate limiting
                    time.sleep(1)
                    
                    successful.append(recipient)
                    self.logger.info(f"Successfully sent email to {recipient}")
                    
                except Exception as e:
                    failed.append(recipient)
                    self.logger.error(f"Failed to send email to {recipient}: {str(e)}")
            
            # Close connection
            server.quit()
            self.logger.info("SMTP connection closed")
            
        except Exception as e:
            self.logger.error(f"SMTP connection error: {str(e)}")
            # If we couldn't even connect, all remaining emails failed
            for email in recipient_groups.keys():
                if email not in successful and email not in failed:
                    failed.append(email)
        
        self.logger.info(f"Email sending complete. Success: {len(successful)}, Failed: {len(failed)}")
        return {'successful': successful, 'failed': failed}

# Example usage:
if __name__ == "__main__":
    # Example with custom email subject and template
    email_sender = ViolationEmailSender(
        smtp_server='smtp.gmail.com',
        smtp_port=587,
        sender_email='shuklamayank015@gmail.com',
        sender_password='wtro mydp ojlv pibm',  # Use app-specific password
        email_subject="Speed Violation Alert",
        email_template="""Dear {owner_name},

We noticed your vehicle ({license_plate}) exceeded the speed limit.

Details:
- Date: {violation_date}
- Time: {violation_time}
- Location: {location}
- Speed Limit: {speed_limit} km/h
- Your Speed: {recorded_speed} km/h

Please drive safely!

Regards,
Traffic Monitoring Team"""
    )

    # Example of sending a single violation
    single_violation = {
        'owner_email': 'violator1@example.com',
        'owner_name': 'John Doe',
        'license_plate': 'ABC123',
        'speed_limit': 60,
        'recorded_speed': 75,
        'violation_date': '2024-02-27',
        'violation_time': '14:30',
        'location': 'Main Street'
    }

    success = email_sender.send_single_violation(single_violation)
    print(f"Single email sent successfully: {success}")

    # Example of sending bulk violations
    violations = [
        single_violation,
        {
            'owner_email': 'violator2@example.com',
            'owner_name': 'Jane Smith',
            'license_plate': 'XYZ789',
            'speed_limit': 60,
            'recorded_speed': 80,
            'violation_date': '2024-02-27',
            'violation_time': '15:45',
            'location': 'Highway 101'
        }
    ]

    result = email_sender.send_bulk_violations(violations)
    print(f"Successfully sent: {len(result['successful'])} emails")
    print(f"Failed to send: {len(result['failed'])} emails")
