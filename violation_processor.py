import os
import time
import base64
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pymongo import MongoClient
from mistralai import Mistral
from datetime import datetime
from config import MISTRAL_API_KEY, MONGODB_URI, VIOLATIONS_FOLDER

class ViolationImageHandler(FileSystemEventHandler):
    def __init__(self, mongodb_uri, mistral_api_key):
        # Initialize MongoDB connection
        self.client = MongoClient(mongodb_uri)
        self.db = self.client['aonix_test']
        
        # Initialize Mistral client
        self.mistral_client = Mistral(api_key=mistral_api_key)
        self.model = "pixtral-12b-2409"

    def on_created(self, event):
        if event.is_directory:
            return
        
        if any(event.src_path.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png']):
            self.process_new_image(event.src_path)

    def encode_image(self, image_path):
        """Encode the image to base64."""
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except FileNotFoundError:
            print(f"Error: The file {image_path} was not found.")
            return None
        except Exception as e:
            print(f"Error encoding image {image_path}: {str(e)}")
            return None

    def process_new_image(self, image_path):
        try:
            # 1. Save file path to violation_pictures collection
            violation_doc = {
                'file_path': image_path,
                'processed': False,
                'timestamp': datetime.now()
            }
            
            result = self.db.violation_pictures.insert_one(violation_doc)
            
            # 2. Process the image to extract license plate
            base64_image = self.encode_image(image_path)
            if not base64_image:
                raise Exception("Failed to encode image")

            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Please extract and return only the license plate number from this image. Return just the number/text, nothing else."
                        },
                        {
                            "type": "image_url",
                            "image_url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    ]
                }
            ]

            # Get response from Mistral
            chat_response = self.mistral_client.chat.complete(
                model=self.model,
                messages=messages
            )
            
            license_plate = chat_response.choices[0].message.content.strip()
            
            # 3. Save license plate to vehicle_licence_plate collection
            license_doc = {
                'license_plate': license_plate,
                'image_path': image_path,
                'violation_id': result.inserted_id,
                'timestamp': datetime.now()
            }
            
            self.db.vehicle_licence_plate.insert_one(license_doc)
            
            # Update violation_pictures document as processed
            self.db.violation_pictures.update_one(
                {'_id': result.inserted_id},
                {'$set': {'processed': True}}
            )
            
            print(f"Processed image: {image_path}")
            print(f"Detected license plate: {license_plate}")
            
        except Exception as e:
            print(f"Error processing image {image_path}: {str(e)}")

def main():
    if not MISTRAL_API_KEY:
        raise ValueError("MISTRAL_API_KEY not configured in config.py")
    
    # Create violations folder if it doesn't exist
    os.makedirs(VIOLATIONS_FOLDER, exist_ok=True)
    
    # Initialize event handler and observer
    event_handler = ViolationImageHandler(MONGODB_URI, MISTRAL_API_KEY)
    observer = Observer()
    observer.schedule(event_handler, VIOLATIONS_FOLDER, recursive=False)
    observer.start()
    
    print(f"Monitoring {VIOLATIONS_FOLDER} for new images...")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\nStopping monitoring...")
    
    observer.join()

if __name__ == "__main__":
    main() 