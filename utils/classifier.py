import os
import numpy as np
import cv2
from PIL import Image
import logging
import io
import base64
from nudenet import NudeDetector

logger = logging.getLogger(__name__)

class NudityClassifier:
    """Class to handle nudity classification using NudeNet."""
    
    def __init__(self):
        """Initialize the NudeNet detector."""
        try:
            logger.info("Initializing NudeNet detector...")
            self.classifier = NudeDetector()
            logger.info("NudeNet detector initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize NudeNet detector: {str(e)}")
            raise
    
    def classify_image(self, file_stream):
        """
        Classify an image for nudity content.
        
        Args:
            file_stream: The uploaded file stream
        
        Returns:
            dict: Dictionary containing classification results
        """
        try:
            # Read image from file stream
            img_bytes = file_stream.read()
            
            # Save the image temporarily
            temp_path = "temp_image.jpg"
            with open(temp_path, "wb") as f:
                f.write(img_bytes)
            
            # Detect nudity in the image
            logger.info("Detecting nudity in image...")
            detections = self.classifier.detect(temp_path)
            
            # Get base64 of the image for display
            with open(temp_path, "rb") as img_file:
                encoded_img = base64.b64encode(img_file.read()).decode('utf-8')
            
            # Remove temporary file
            if os.path.exists(temp_path):
                os.remove(temp_path)
            
            # Calculate scores based on detections
            # Extract nudity related labels
            nude_labels = ['FEMALE_GENITALIA_EXPOSED', 'MALE_GENITALIA_EXPOSED', 'FEMALE_BREAST_EXPOSED', 
                         'BUTTOCKS_EXPOSED', 'ANUS_EXPOSED', 'FEET_EXPOSED', 'ARMPITS_EXPOSED']
            sexy_labels = ['FEMALE_BREAST_COVERED', 'BUTTOCKS_COVERED', 'STOMACH_COVERED', 'INTIMATE_CLOTHING']
            
            # Initialize scores
            nudity_score = 0
            sexy_score = 0
            detection_count = max(1, len(detections))
            
            # Calculate scores based on detected objects
            for detection in detections:
                if detection['label'] in nude_labels:
                    nudity_score += detection['score']
                elif detection['label'] in sexy_labels:
                    sexy_score += detection['score']
            
            # Normalize scores to 0-100 range
            nudity_score = min(100, (nudity_score / detection_count) * 100)
            sexy_score = min(100, (sexy_score / detection_count) * 100)
            safe_score = max(0, 100 - nudity_score - sexy_score)
            
            # Get nudity level description
            nudity_level = self._get_nudity_level(nudity_score)
            
            return {
                'safe_score': round(safe_score, 2),
                'nudity_score': round(nudity_score, 2),
                'nudity_level': nudity_level,
                'sexy_score': round(sexy_score, 2),
                'image': encoded_img,
                'detections': detections  # Include the raw detections for debugging
            }
        except Exception as e:
            logger.exception(f"Error in classify_image: {str(e)}")
            raise
    
    def _get_nudity_level(self, nudity_score):
        """
        Get a descriptive level for the nudity score.
        
        Args:
            nudity_score (float): Nudity score from 0-100
            
        Returns:
            str: Descriptive nudity level
        """
        if nudity_score < 15:
            return "Safe"
        elif nudity_score < 40:
            return "Low"
        elif nudity_score < 70:
            return "Moderate"
        elif nudity_score < 90:
            return "High"
        else:
            return "Extreme"
