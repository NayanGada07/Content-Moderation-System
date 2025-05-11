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
            
            # Debug the structure of detections
            logger.debug(f"Detection result structure: {detections}")
            
            # Initialize scores
            nudity_score = 0
            sexy_score = 0
            
            # Define categories for classification
            nude_classes = [
                'FEMALE_GENITALIA_EXPOSED', 'MALE_GENITALIA_EXPOSED', 
                'FEMALE_BREAST_EXPOSED', 'BUTTOCKS_EXPOSED', 
                'ANUS_EXPOSED', 'FEET_EXPOSED'
            ]
            
            sexy_classes = [
                'FEMALE_BREAST_COVERED', 'BUTTOCKS_COVERED',
                'BELLY_EXPOSED', 'FEMALE_GENITALIA_COVERED',
                'MALE_GENITALIA_COVERED', 'ARMPITS_EXPOSED'
            ]
            
            # Safe classes don't contribute to nudity
            safe_classes = [
                'FACE_FEMALE', 'FACE_MALE', 'FEET_COVERED',
                'BELLY_COVERED', 'ARMPITS_COVERED'
            ]
            
            # Check if any detections exist
            if detections and isinstance(detections, list) and len(detections) > 0:
                detection_count = len(detections)
                logger.debug(f"Found {detection_count} detections")
                
                # Just for debugging - log the keys in the first detection
                if detection_count > 0 and isinstance(detections[0], dict):
                    logger.debug(f"Detection keys: {list(detections[0].keys())}")
                
                # Process each detection
                nude_hits = 0
                nude_score_sum = 0
                sexy_hits = 0
                sexy_score_sum = 0
                
                for detection in detections:
                    if 'class' in detection and 'score' in detection:
                        cls = detection['class']
                        score = detection['score']
                        
                        if cls in nude_classes:
                            nude_hits += 1
                            nude_score_sum += score
                            logger.debug(f"Found nude element: {cls} with score {score}")
                        elif cls in sexy_classes:
                            sexy_hits += 1
                            sexy_score_sum += score
                            logger.debug(f"Found sexy element: {cls} with score {score}")
                        else:
                            logger.debug(f"Found other element: {cls} with score {score}")
                
                # Calculate final scores
                if nude_hits > 0:
                    nudity_score = (nude_score_sum / nude_hits) * 100
                    nudity_score = min(100, nudity_score) 
                
                if sexy_hits > 0:
                    sexy_score = (sexy_score_sum / sexy_hits) * 50  # Reduce the impact of sexy content
                    sexy_score = min(80, sexy_score)  # Cap at 80% for sexy
                
                # If we have no nude elements but have sexy elements, reduce the overall nudity score
                if nude_hits == 0 and sexy_hits > 0:
                    nudity_score = sexy_score * 0.4  # Sexy content contributes little to nudity if no nudity detected
            else:
                # No detections, assume image is safe
                logger.info("No detections found in image")
                detection_count = 1  # Avoid division by zero
                nudity_score = 0
                sexy_score = 0
                
            logger.info(f"Calculated nudity score: {nudity_score:.2f}%, sexy score: {sexy_score:.2f}%")
            
            # Calculate safe score as inverse of nudity and sexy scores
            safe_score = max(0, 100 - nudity_score - sexy_score)
            
            # Get nudity level description
            nudity_level = self._get_nudity_level(nudity_score)
            
            # Format detections for serialization - ensure all values are JSON serializable
            serializable_detections = []
            if isinstance(detections, list):
                for d in detections:
                    if isinstance(d, dict):
                        # Convert any non-serializable values to strings
                        sd = {}
                        for k, v in d.items():
                            if isinstance(v, (str, int, float, bool, type(None))):
                                sd[k] = v
                            else:
                                sd[k] = str(v)
                        serializable_detections.append(sd)
                    else:
                        serializable_detections.append(str(d))
            
            response = {
                'safe_score': round(safe_score, 2),
                'nudity_score': round(nudity_score, 2),
                'nudity_level': nudity_level,
                'sexy_score': round(sexy_score, 2),
                'image': encoded_img
            }
            
            # Only include detections if we have them
            if serializable_detections:
                response['detections'] = serializable_detections
            
            return response
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
