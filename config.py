import os
import base64

MISTRAL_API_KEY = "X1VXNj0dxcY7qkfQ6gkIjo9zN2t1YSCa"  # Directly set the API key
MONGODB_URI = "mongodb://localhost:27017/"
VIOLATIONS_FOLDER = "violations" 

def encode_image(image_path):
    """Encode the image to base64."""
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except FileNotFoundError:
        print(f"Error: The file {image_path} was not found.")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None 