# Parking Space Detection AI System

## 🚗 Overview

This AI-powered parking space detection system uses computer vision and machine learning to analyze parking lot images in real-time. It automatically detects available and occupied parking spaces, providing accurate occupancy data for parking management applications.

## ✨ Features

- **Real-time Analysis**: Process parking lot images instantly
- **High Accuracy**: Advanced computer vision algorithms for precise detection
- **RESTful API**: Easy integration with mobile and web applications
- **Image Processing**: Automatic image enhancement and preprocessing
- **Visualization**: Generate annotated images showing detection results
- **Scalable**: Handle multiple concurrent requests
- **Logging**: Comprehensive logging for monitoring and debugging

## 🛠️ Technology Stack

- **Python 3.8+**
- **OpenCV**: Computer vision and image processing
- **Flask**: Web framework for API endpoints
- **NumPy**: Numerical computing
- **PIL/Pillow**: Image manipulation
- **Scikit-image**: Advanced image processing

## 📋 Prerequisites

- Python 3.8 or higher
- pip package manager
- Camera or image source for testing

## 🚀 Installation

1. **Clone the repository:**
```bash
git clone https://github.com/abdoemad23/parking-management-app.git
cd parking-management-app
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Create upload directory:**
```bash
mkdir uploads
```

## 🎯 Usage

### Starting the Server

```bash
python ai_code.py
```

The API will be available at: `http://localhost:5000`

### API Endpoints

#### 1. Analyze Parking Lot
**POST** `/api/test`

Upload an image for parking space analysis.

**Request:**
- Content-Type: `multipart/form-data`
- Field: `image` (file)

**Response:**
```json
{
  "total_spaces": 25,
  "occupied_spaces": 18,
  "available_spaces": 7,
  "occupancy_rate": 72.0,
  "timestamp": "2024-01-15T10:30:00",
  "image": "/path/to/uploaded/image.jpg",
  "status": "success"
}
```

#### 2. Health Check
**GET** `/api/health`

Check if the service is running.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00",
  "version": "1.0.0"
}
```

#### 3. System Statistics
**GET** `/api/stats`

Get system statistics and performance metrics.

**Response:**
```json
{
  "total_images_processed": 150,
  "upload_folder_size": 52428800,
  "status": "success"
}
```

## 🔧 Configuration

### Detection Parameters

You can adjust these parameters in `ai_code.py`:

```python
PARKING_SPACE_MIN_AREA = 1000          # Minimum area for parking space
VEHICLE_DETECTION_THRESHOLD = 0.3      # Vehicle detection sensitivity
CONTOUR_APPROXIMATION_FACTOR = 0.02    # Contour approximation accuracy
```

### Server Configuration

```python
# In ai_code.py
app.run(host='0.0.0.0', port=5000, debug=True)
```

## 📊 How It Works

### 1. Image Preprocessing
- Convert to grayscale
- Apply Gaussian blur for noise reduction
- Adaptive thresholding for better contrast
- Morphological operations for cleanup

### 2. Parking Space Detection
- Find contours in the processed image
- Filter contours by area and shape
- Approximate contours to polygons
- Identify rectangular parking spaces

### 3. Vehicle Detection
- Create masks for each parking space
- Extract regions of interest
- Analyze color patterns (HSV color space)
- Detect dark objects (vehicles) using thresholding

### 4. Results Processing
- Calculate occupancy statistics
- Generate visualization images
- Return structured JSON response

## 🧪 Testing

### Manual Testing with cURL

```bash
# Test image upload
curl -X POST -F "image=@test_parking_lot.jpg" http://localhost:5000/api/test

# Health check
curl http://localhost:5000/api/health

# Get statistics
curl http://localhost:5000/api/stats
```

### Python Testing Script

```python
import requests

# Test the API
url = "http://localhost:5000/api/test"
files = {"image": open("test_image.jpg", "rb")}
response = requests.post(url, files=files)
print(response.json())
```

## 📈 Performance Optimization

### Image Processing
- Automatic image compression
- Efficient memory usage
- Batch processing capabilities

### File Management
- Automatic cleanup of old files
- Configurable retention policy
- Disk space monitoring

## 🔒 Security Considerations

- File type validation
- Secure filename handling
- File size limits
- Input sanitization

## 🐛 Troubleshooting

### Common Issues

1. **"Could not load image" error:**
   - Check file format (supports: PNG, JPG, JPEG, GIF, BMP)
   - Verify file is not corrupted
   - Ensure file size is under 16MB

2. **Low detection accuracy:**
   - Adjust `VEHICLE_DETECTION_THRESHOLD` parameter
   - Improve image quality and lighting
   - Ensure parking spaces are clearly defined

3. **Server not starting:**
   - Check if port 5000 is available
   - Verify all dependencies are installed
   - Check Python version compatibility

## 📝 Logging

The system provides comprehensive logging:

- **INFO**: General operation logs
- **ERROR**: Error handling and debugging
- **DEBUG**: Detailed processing information

Logs include:
- Image processing steps
- Detection results
- API request/response details
- Error messages and stack traces

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Contact the development team
- Check the documentation

## 🔄 Version History

- **v1.0.0**: Initial release with basic parking space detection
- **v1.1.0**: Added visualization and improved accuracy
- **v1.2.0**: Enhanced API endpoints and error handling

---

**Developed by**: Parking Management Team  
**Last Updated**: January 2024  
**Repository**: [GitHub](https://github.com/abdoemad23/parking-management-app)
