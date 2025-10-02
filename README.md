# House Checking App - Industrial Inspection System

## Overview

The House Checking App is a comprehensive industrial inspection system designed for automated quality control of metal parts. The system performs computer vision-based analysis to detect part presence, measure hole diameters, assess weld seam lengths, and identify weld spatter defects.

## Features

- **Automated Part Detection**: Identifies presence of metal parts in the inspection area
- **Hole Measurement**: Detects and measures circular holes with diameter calculations
- **Weld Seam Analysis**: Measures weld seam lengths between holes
- **Spatter Detection**: Identifies and counts weld spatter instances
- **Real-time Processing**: Processes images and provides immediate feedback
- **Data Logging**: Saves measurement data to CSV files with timestamp tracking
- **Image Annotation**: Creates annotated images with measurement overlays
- **Non-overwrite File Management**: Implements safe file naming to prevent data loss

## Project Structure

```
HouseCheckingApp/
├── main.py                     # Main application and Inspector class
├── config.py                   # Configuration settings and parameters
├── camera/
│   ├── __init__.py
│   └── camera_controller.py    # Camera operations and test image generation
├── image_processing/
│   ├── __init__.py
│   ├── detection.py            # Computer vision algorithms
│   └── calibration.py          # Camera calibration utilities
├── ui/
│   ├── __init__.py
│   └── main_window.py         # GUI interface (placeholder for PyQt)
├── utils/
│   ├── __init__.py
│   ├── file_utils.py          # File management utilities
│   └── logger.py              # Logging system
├── resources/                  # Resource files and assets
└── README.md                  # This file
```

## Installation

### Prerequisites

- Python 3.8 or higher
- OpenCV (cv2)
- NumPy
- Pandas
- IPython (for Jupyter notebook compatibility)

### Install Dependencies

```bash
pip install opencv-python numpy pandas ipython
```

### Optional Dependencies (for future GUI development)

```bash
pip install PyQt5 matplotlib plotly
```

## Usage

### Basic Usage

```python
from main import Inspector

# Create inspector instance
inspector = Inspector(user="operator_name", order_number="749274")

# Process a test image
import cv2
img = cv2.imread("test_part.jpg")
result = inspector.process_and_save(img, part_number="1234", cam_id=1)

print(f"Status: {result['status']}")
print(f"Measurements: {result['measurements']}")
```

### Running the Demo

Execute the main script to run the demonstration:

```bash
python main.py
```

This will:
1. Create synthetic test images with various defect scenarios
2. Process each image through the inspection pipeline
3. Save annotated results and measurement data
4. Display processing statistics

### Console Interface

Run the console interface for interactive operation:

```bash
python ui/main_window.py
```

Available commands:
- Start new inspection session
- Process test images  
- View statistics
- Camera preview
- Settings configuration

### Test Image Generation

Generate synthetic test parts with different defect conditions:

```python
from camera.camera_controller import CameraController

camera = CameraController()

# Normal part
normal_img = camera.generate_test_part()

# Part with defects
defective_img = camera.generate_test_part(
    part_missing=False,
    no_welding=False, 
    spatter=True
)
```

## Configuration

The system can be configured through the `config.py` file or environment variables:

### Key Configuration Parameters

```python
# Camera settings
CAMERA_WIDTH = 1920
CAMERA_HEIGHT = 1080
CAMERA_FPS = 30

# Detection thresholds
PART_DETECTION_THRESHOLD = 240.0
MAX_SPATTER_COUNT = 5
EXPECTED_HOLE_COUNT = 4

# Measurement tolerances
HOLE_DIAMETER_MIN = 35.0
HOLE_DIAMETER_MAX = 45.0
```

### Environment Variables

Set environment variables to override default settings:

```bash
export INSPECTION_CAMERA_WIDTH=1920
export INSPECTION_CAMERA_HEIGHT=1080
export INSPECTION_PART_THRESHOLD=240.0
export INSPECTION_MAX_SPATTER=5
export INSPECTION_OUTPUT_DIR="./output"
export INSPECTION_DEBUG=true
```

## Output Files

The system generates several types of output files:

### CSV Data File
```
output/{order_number}/{order_number}.csv
```
Contains measurement data with columns:
- Number, OK/NOK, Order number, Counter, Date, Time
- Value1-12 (hole dimensions and weld lengths)
- User name

### Annotated Images
```
output/{order_number}/{status}_{order_number}_{part_number}Count{counter}_CAM{cam_id}.jpg
```
Images with measurement overlays and defect annotations.

### Log Files
```
logs/inspection_{date}.log
```
System logs with processing details and error messages.

## Measurement System

The system provides 12 measurement values per part:

| Value | Description |
|-------|-------------|
| Value1 | Hole 1 Width |
| Value2 | Hole 1 Height |
| Value3 | Hole 2 Width |
| Value4 | Hole 2 Height |
| Value5 | Top Weld Length |
| Value6 | Bottom Weld Length |
| Value7 | Hole 3 Width |
| Value8 | Hole 3 Height |
| Value9 | Hole 4 Width |
| Value10 | Hole 4 Height |
| Value11 | Left Weld Length |
| Value12 | Right Weld Length |

## API Reference

### Inspector Class

Main class for inspection operations:

```python
inspector = Inspector(user="name", order_number="12345", output_dir="./output")

# Process single image
result = inspector.process_and_save(image, part_number="1234")

# Capture and process from camera  
result = inspector.capture_and_process(part_number="1234")

# Get session statistics
stats = inspector.get_statistics()
```

### Detection Functions

Computer vision functions for part analysis:

```python
from image_processing.detection import (
    detect_part_presence,
    detect_holes, 
    detect_spatter,
    calculate_seam_lengths,
    annotate_image
)

# Detect if part is present
part_present = detect_part_presence(gray_image)

# Find holes
holes = detect_holes(gray_image)

# Count spatter
spatter_count = detect_spatter(gray_image)
```

## Quality Control

The system implements several quality checks:

### OK/NOK Criteria

A part is marked as **NOK** (Not OK) if:
- Part is missing from inspection area
- Fewer than 4 holes detected
- Excessive weld spatter (>5 instances)
- Holes outside diameter tolerances
- Weld seams outside length tolerances

### Measurement Accuracy

- Hole detection using Hough Circle Transform
- Sub-pixel accuracy for measurements
- Calibration support for real-world units
- Configurable tolerance thresholds

## Development

### Adding New Detection Algorithms

1. Implement detection function in `image_processing/detection.py`
2. Add configuration parameters to `config.py`  
3. Integrate with Inspector class in `main.py`
4. Add appropriate logging and error handling

### Extending the GUI

The current implementation includes a placeholder GUI structure. To implement the full PyQt interface:

1. Install PyQt5: `pip install PyQt5`
2. Implement the GUI classes in `ui/main_window.py`
3. Connect GUI events to Inspector methods
4. Add real-time camera display and controls

### Camera Integration

To integrate with physical cameras:

1. Update `CameraController.connect()` method
2. Configure camera-specific settings
3. Add camera calibration procedures
4. Implement trigger and synchronization logic

## Testing

### Unit Tests

Run unit tests for individual components:

```bash
python -m pytest tests/
```

### Integration Tests

Test the complete inspection workflow:

```bash
python tests/test_integration.py
```

### Performance Testing

Measure processing performance:

```bash
python tests/test_performance.py
```

## Troubleshooting

### Common Issues

**Camera Connection Failed**
- Check camera device ID in configuration
- Verify camera permissions and drivers
- Test with system falls back to synthetic images

**Image Processing Errors**
- Ensure proper lighting conditions
- Check image quality and focus
- Verify part positioning within frame
- Adjust detection thresholds in config

**File Permission Errors**
- Check write permissions for output directory
- Ensure sufficient disk space
- Verify file naming doesn't conflict with OS restrictions

### Debug Mode

Enable debug mode for detailed logging:

```python
from config import Config
Config.DEBUG_MODE = True
Config.VERBOSE_LOGGING = True
```

Or set environment variable:
```bash
export INSPECTION_DEBUG=true
export INSPECTION_VERBOSE=true
```

## License

This project is proprietary software developed for industrial inspection applications.

## Support

For technical support and questions:
- Check the troubleshooting section above
- Review log files in the `logs/` directory  
- Contact the development team with detailed error descriptions

## Version History

### Version 1.0.0
- Initial release with core inspection functionality
- Synthetic test image generation
- CSV data logging and image annotation
- Console-based interface
- Configurable detection parameters

### Planned Features
- Full PyQt GUI implementation
- Live camera integration
- Advanced calibration tools
- Statistical analysis dashboard
- Network connectivity for data export
- Multi-camera support