"""
Parking Space Detection AI System
=================================

This Python script uses computer vision and machine learning to analyze parking lot images
and detect available parking spaces. It processes images from the Flutter app camera feed
and returns the count of occupied and available parking spaces.

Features:
- Real-time parking space detection
- Image preprocessing and enhancement
- Contour detection for parking spaces
- Vehicle detection using color analysis
- RESTful API endpoint for Flutter integration
- Image storage and management

Author: Parking Management Team
Version: 1.0.0
"""

import cv2
import numpy as np
import os
import json
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import logging
from datetime import datetime
import base64
from io import BytesIO
from PIL import Image

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

# Create upload directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Parking space detection parameters
PARKING_SPACE_MIN_AREA = 1000
VEHICLE_DETECTION_THRESHOLD = 0.3
CONTOUR_APPROXIMATION_FACTOR = 0.02

class ParkingSpaceDetector:
    """
    Main class for parking space detection using computer vision techniques.
    """
    
    def __init__(self):
        self.parking_spaces = []
        self.occupied_spaces = 0
        self.available_spaces = 0
        
    def preprocess_image(self, image):
        """
        Preprocess the input image for better detection results.
        
        Args:
            image: Input image (numpy array)
            
        Returns:
            Processed image
        """
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Apply adaptive thresholding
        thresh = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        
        # Morphological operations to clean up the image
        kernel = np.ones((3, 3), np.uint8)
        cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_OPEN, kernel)
        
        return cleaned
    
    def detect_parking_spaces(self, image):
        """
        Detect parking spaces using contour detection.
        
        Args:
            image: Preprocessed image
            
        Returns:
            List of parking space contours
        """
        # Find contours
        contours, _ = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        parking_spaces = []
        
        for contour in contours:
            # Calculate contour area
            area = cv2.contourArea(contour)
            
            # Filter contours by area
            if area > PARKING_SPACE_MIN_AREA:
                # Approximate contour to polygon
                epsilon = CONTOUR_APPROXIMATION_FACTOR * cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, epsilon, True)
                
                # Check if contour has 4 vertices (rectangular shape)
                if len(approx) >= 4:
                    parking_spaces.append(contour)
        
        return parking_spaces
    
    def detect_vehicles(self, image, parking_spaces):
        """
        Detect vehicles in parking spaces using color analysis.
        
        Args:
            image: Original image
            parking_spaces: List of parking space contours
            
        Returns:
            List of occupied parking spaces
        """
        occupied_spaces = []
        
        for i, space in enumerate(parking_spaces):
            # Create mask for parking space
            mask = np.zeros(image.shape[:2], dtype=np.uint8)
            cv2.fillPoly(mask, [space], 255)
            
            # Extract region of interest
            roi = cv2.bitwise_and(image, image, mask=mask)
            
            # Convert to HSV for better color analysis
            hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
            
            # Define color ranges for vehicles (cars are typically dark colors)
            lower_dark = np.array([0, 0, 0])
            upper_dark = np.array([180, 255, 50])
            
            # Create mask for dark objects (vehicles)
            vehicle_mask = cv2.inRange(hsv, lower_dark, upper_dark)
            
            # Calculate percentage of dark pixels
            total_pixels = np.sum(mask > 0)
            vehicle_pixels = np.sum(vehicle_mask > 0)
            
            if total_pixels > 0:
                vehicle_ratio = vehicle_pixels / total_pixels
                
                # If vehicle ratio exceeds threshold, space is occupied
                if vehicle_ratio > VEHICLE_DETECTION_THRESHOLD:
                    occupied_spaces.append(i)
        
        return occupied_spaces
    
    def analyze_parking_lot(self, image_path):
        """
        Main method to analyze parking lot image and return results.
        
        Args:
            image_path: Path to the input image
            
        Returns:
            Dictionary with analysis results
        """
        try:
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError("Could not load image")
            
            # Preprocess image
            processed = self.preprocess_image(image)
            
            # Detect parking spaces
            parking_spaces = self.detect_parking_spaces(processed)
            
            # Detect vehicles
            occupied_spaces = self.detect_vehicles(image, parking_spaces)
            
            # Calculate results
            total_spaces = len(parking_spaces)
            occupied_count = len(occupied_spaces)
            available_count = total_spaces - occupied_count
            
            # Calculate occupancy percentage
            occupancy_rate = (occupied_count / total_spaces * 100) if total_spaces > 0 else 0
            
            # Create result dictionary
            result = {
                'total_spaces': total_spaces,
                'occupied_spaces': occupied_count,
                'available_spaces': available_count,
                'occupancy_rate': round(occupancy_rate, 2),
                'timestamp': datetime.now().isoformat(),
                'image_path': image_path,
                'status': 'success'
            }
            
            logger.info(f"Analysis completed: {occupied_count}/{total_spaces} spaces occupied")
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing image: {str(e)}")
            return {
                'error': str(e),
                'status': 'error',
                'timestamp': datetime.now().isoformat()
            }
    
    def visualize_results(self, image_path, parking_spaces, occupied_spaces):
        """
        Create visualization of detection results.
        
        Args:
            image_path: Path to original image
            parking_spaces: List of parking space contours
            occupied_spaces: List of occupied space indices
            
        Returns:
            Path to visualization image
        """
        image = cv2.imread(image_path)
        
        # Draw all parking spaces
        for i, space in enumerate(parking_spaces):
            color = (0, 0, 255) if i in occupied_spaces else (0, 255, 0)  # Red for occupied, Green for available
            cv2.drawContours(image, [space], -1, color, 2)
            
            # Add text labels
            M = cv2.moments(space)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                status = "OCCUPIED" if i in occupied_spaces else "AVAILABLE"
                cv2.putText(image, status, (cx-50, cy), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        # Save visualization
        viz_path = os.path.join(UPLOAD_FOLDER, f"visualization_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg")
        cv2.imwrite(viz_path, image)
        
        return viz_path

def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/test', methods=['POST'])
def analyze_parking():
    """
    API endpoint for parking space analysis.
    Receives image from Flutter app and returns analysis results.
    """
    try:
        # Check if image is in request
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided', 'status': 'error'}), 400
        
        file = request.files['image']
        
        if file.filename == '':
            return jsonify({'error': 'No image selected', 'status': 'error'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type', 'status': 'error'}), 400
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{filename}"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # Analyze parking lot
        detector = ParkingSpaceDetector()
        result = detector.analyze_parking_lot(filepath)
        
        if result['status'] == 'success':
            # Return image path for Flutter app
            result['image'] = filepath
            
            # Clean up old files (keep only last 10)
            cleanup_old_files()
            
            return jsonify(result), 200
        else:
            return jsonify(result), 500
            
    except Exception as e:
        logger.error(f"API error: {str(e)}")
        return jsonify({'error': str(e), 'status': 'error'}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    }), 200

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get system statistics."""
    try:
        files = os.listdir(UPLOAD_FOLDER)
        image_files = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        
        return jsonify({
            'total_images_processed': len(image_files),
            'upload_folder_size': sum(os.path.getsize(os.path.join(UPLOAD_FOLDER, f)) for f in image_files),
            'status': 'success'
        }), 200
    except Exception as e:
        return jsonify({'error': str(e), 'status': 'error'}), 500

def cleanup_old_files():
    """Clean up old uploaded files to prevent disk space issues."""
    try:
        files = os.listdir(UPLOAD_FOLDER)
        image_files = [(f, os.path.getmtime(os.path.join(UPLOAD_FOLDER, f))) for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        
        # Sort by modification time (oldest first)
        image_files.sort(key=lambda x: x[1])
        
        # Keep only the 10 most recent files
        if len(image_files) > 10:
            files_to_delete = image_files[:-10]
            for filename, _ in files_to_delete:
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                os.remove(filepath)
                logger.info(f"Deleted old file: {filename}")
                
    except Exception as e:
        logger.error(f"Error cleaning up files: {str(e)}")

if __name__ == '__main__':
    # Create upload directory
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
    # Start Flask application
    logger.info("Starting Parking Space Detection API...")
    app.run(host='0.0.0.0', port=5000, debug=True)
