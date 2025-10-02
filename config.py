"""
Configuration settings for the Industrial Inspection System.

This module contains all configuration parameters, thresholds, and settings
used throughout the inspection application.
"""

import os


class Config:
    """
    Configuration class containing all application settings.
    """
    
    # === Application Information ===
    APP_NAME = "House Checking App - Industrial Inspection System"
    APP_VERSION = "1.0.0"
    APP_DESCRIPTION = (
        "Automated industrial inspection system for metal parts with "
        "hole detection, weld seam measurement, and spatter detection"
    )
    
    # === Camera Settings ===
    CAMERA_WIDTH = 1920
    CAMERA_HEIGHT = 1080
    CAMERA_FPS = 30
    CAMERA_TIMEOUT = 5.0  # seconds
    
    # === Image Processing Parameters ===
    # Part detection
    PART_DETECTION_THRESHOLD = 240.0  # Mean pixel value threshold for part presence
    
    # Hole detection
    EXPECTED_HOLE_COUNT = 4
    MIN_HOLE_RADIUS = 10
    MAX_HOLE_RADIUS = 40
    HOLE_DETECTION_PARAM1 = 50  # Upper threshold for edge detection
    HOLE_DETECTION_PARAM2 = 20  # Accumulator threshold for center detection
    MIN_DISTANCE_BETWEEN_HOLES = 50  # Minimum distance between hole centers
    
    # Spatter detection
    MAX_SPATTER_COUNT = 5  # Maximum allowed spatter instances
    SPATTER_BINARY_THRESHOLD = 220  # Threshold for binary image creation
    MIN_SPATTER_AREA = 3  # Minimum area for spatter blob
    MAX_SPATTER_AREA = 100  # Maximum area for spatter blob
    
    # Measurement tolerances (in pixels or measurement units)
    HOLE_DIAMETER_MIN = 35.0
    HOLE_DIAMETER_MAX = 45.0
    WELD_SEAM_LENGTH_MIN = 80.0
    WELD_SEAM_LENGTH_MAX = 120.0
    
    # === File and Directory Settings ===
    DEFAULT_OUTPUT_DIR = "output"
    LOG_DIR = "logs"
    BACKUP_DIR = "backup"
    
    # File naming
    IMAGE_FORMAT = "jpg"
    CSV_FILENAME_TEMPLATE = "{order_number}.csv"
    IMAGE_FILENAME_TEMPLATE = "{status}_{order_number}_{part_number}Count{counter}_CAM{cam_id}.{format}"
    
    # File management
    MAX_FILES_PER_DIRECTORY = 1000  # Clean old files when exceeded
    LOG_ROTATION_SIZE = 10 * 1024 * 1024  # 10MB
    LOG_BACKUP_COUNT = 5
    
    # === CSV Export Settings ===
    CSV_HEADERS = [
        "Number", "OK/NOK", "Ordernumber", "Counter", "Date", "Time",
        "Value1", "Value2", "Value3", "Value4", "Value5", "Value6",
        "Value7", "Value8", "Value9", "Value10", "Value11", "Value12",
        "User"
    ]
    
    # Measurement value mapping (what each Value1-12 represents)
    MEASUREMENT_MAPPING = {
        "Value1": "Hole 1 Width",
        "Value2": "Hole 1 Height", 
        "Value3": "Hole 2 Width",
        "Value4": "Hole 2 Height",
        "Value5": "Top Weld Length",
        "Value6": "Bottom Weld Length",
        "Value7": "Hole 3 Width",
        "Value8": "Hole 3 Height",
        "Value9": "Hole 4 Width", 
        "Value10": "Hole 4 Height",
        "Value11": "Left Weld Length",
        "Value12": "Right Weld Length"
    }
    
    # === UI Settings ===
    WINDOW_TITLE = "Industrial Inspection System"
    WINDOW_WIDTH = 1200
    WINDOW_HEIGHT = 800
    
    # Colors (BGR format for OpenCV)
    COLOR_OK = (0, 255, 0)      # Green
    COLOR_NOK = (0, 0, 255)     # Red
    COLOR_WARNING = (0, 165, 255)  # Orange
    COLOR_INFO = (255, 255, 0)     # Cyan
    
    # Annotation settings
    FONT_SCALE = 0.5
    FONT_THICKNESS = 1
    LINE_THICKNESS = 2
    
    # === Quality Control Thresholds ===
    QUALITY_THRESHOLDS = {
        "hole_diameter_tolerance": 2.0,  # +/- pixels
        "weld_length_tolerance": 5.0,    # +/- pixels
        "circularity_threshold": 0.7,    # Minimum circularity for holes
        "minimum_weld_continuity": 0.8   # Minimum weld seam continuity
    }
    
    # === Performance Settings ===
    # Processing timeouts
    IMAGE_PROCESSING_TIMEOUT = 10.0  # seconds
    CAMERA_CAPTURE_TIMEOUT = 5.0     # seconds
    
    # Memory management
    MAX_IMAGES_IN_MEMORY = 10
    IMAGE_CACHE_SIZE_MB = 100
    
    # === Debugging and Development ===
    DEBUG_MODE = False
    SAVE_DEBUG_IMAGES = False
    SHOW_PROCESSING_STEPS = False
    VERBOSE_LOGGING = False
    
    # Test image generation settings
    TEST_IMAGE_SIZE = (600, 400)
    TEST_PART_MARGIN = 40
    TEST_HOLE_RADIUS = 20
    TEST_WELD_THICKNESS = 5
    
    # === System Paths ===
    @classmethod
    def get_output_directory(cls, order_number: str) -> str:
        """Get output directory path for a specific order."""
        return os.path.join(cls.DEFAULT_OUTPUT_DIR, order_number)
    
    @classmethod
    def get_log_directory(cls) -> str:
        """Get log directory path."""
        return cls.LOG_DIR
    
    @classmethod
    def get_backup_directory(cls) -> str:
        """Get backup directory path.""" 
        return cls.BACKUP_DIR
    
    # === Environment Variables Override ===
    @classmethod
    def load_from_environment(cls):
        """Load configuration values from environment variables if available."""
        # Camera settings
        cls.CAMERA_WIDTH = int(os.getenv('INSPECTION_CAMERA_WIDTH', cls.CAMERA_WIDTH))
        cls.CAMERA_HEIGHT = int(os.getenv('INSPECTION_CAMERA_HEIGHT', cls.CAMERA_HEIGHT))
        cls.CAMERA_FPS = int(os.getenv('INSPECTION_CAMERA_FPS', cls.CAMERA_FPS))
        
        # Thresholds
        cls.PART_DETECTION_THRESHOLD = float(os.getenv('INSPECTION_PART_THRESHOLD', cls.PART_DETECTION_THRESHOLD))
        cls.MAX_SPATTER_COUNT = int(os.getenv('INSPECTION_MAX_SPATTER', cls.MAX_SPATTER_COUNT))
        
        # Directories
        cls.DEFAULT_OUTPUT_DIR = os.getenv('INSPECTION_OUTPUT_DIR', cls.DEFAULT_OUTPUT_DIR)
        cls.LOG_DIR = os.getenv('INSPECTION_LOG_DIR', cls.LOG_DIR)
        
        # Debug mode
        cls.DEBUG_MODE = os.getenv('INSPECTION_DEBUG', 'false').lower() == 'true'
        cls.VERBOSE_LOGGING = os.getenv('INSPECTION_VERBOSE', 'false').lower() == 'true'
    
    # === Validation ===
    @classmethod
    def validate_configuration(cls) -> list:
        """
        Validate configuration settings and return list of issues found.
        
        Returns:
            List of configuration issues (empty if all valid)
        """
        issues = []
        
        # Check camera settings
        if cls.CAMERA_WIDTH <= 0 or cls.CAMERA_HEIGHT <= 0:
            issues.append("Invalid camera resolution settings")
        
        if cls.CAMERA_FPS <= 0 or cls.CAMERA_FPS > 120:
            issues.append("Invalid camera FPS setting")
        
        # Check thresholds
        if cls.PART_DETECTION_THRESHOLD <= 0 or cls.PART_DETECTION_THRESHOLD > 255:
            issues.append("Invalid part detection threshold")
        
        if cls.MAX_SPATTER_COUNT < 0:
            issues.append("Invalid maximum spatter count")
        
        # Check hole detection parameters
        if cls.MIN_HOLE_RADIUS >= cls.MAX_HOLE_RADIUS:
            issues.append("Invalid hole radius range")
        
        # Check measurement tolerances
        if cls.HOLE_DIAMETER_MIN >= cls.HOLE_DIAMETER_MAX:
            issues.append("Invalid hole diameter tolerance range")
        
        return issues


# Load environment variables on import
Config.load_from_environment()