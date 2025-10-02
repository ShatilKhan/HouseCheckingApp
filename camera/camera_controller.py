"""
Camera controller for industrial inspection system.

This module handles camera operations including live capture and synthetic
test image generation for demonstration purposes.
"""

import cv2
import numpy as np
from typing import Tuple, Optional
import time

from config import Config


class CameraController:
    """
    Controller for camera operations and test image generation.
    
    Handles both live camera capture and synthetic image generation
    for testing and demonstration purposes.
    """
    
    def __init__(self, camera_id: int = 0):
        """
        Initialize camera controller.
        
        Args:
            camera_id: Camera device ID (0 for default camera)
        """
        self.camera_id = camera_id
        self.cap = None
        self.is_connected = False
        
    def connect(self) -> bool:
        """
        Connect to camera device.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            self.cap = cv2.VideoCapture(self.camera_id)
            if self.cap.isOpened():
                # Set camera properties
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, Config.CAMERA_WIDTH)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, Config.CAMERA_HEIGHT)
                self.cap.set(cv2.CAP_PROP_FPS, Config.CAMERA_FPS)
                
                self.is_connected = True
                return True
        except Exception as e:
            print(f"Failed to connect to camera: {e}")
        
        return False
    
    def disconnect(self) -> None:
        """Disconnect from camera device."""
        if self.cap is not None:
            self.cap.release()
            self.is_connected = False
    
    def capture_image(self) -> Optional[np.ndarray]:
        """
        Capture a single image from camera.
        
        Returns:
            Captured image as numpy array, None if capture failed
        """
        if not self.is_connected:
            if not self.connect():
                # If live camera not available, generate test image
                return self.generate_test_part()
        
        try:
            ret, frame = self.cap.read()
            if ret:
                return frame
        except Exception as e:
            print(f"Error capturing image: {e}")
        
        # Fallback to test image if live capture fails
        return self.generate_test_part()
    
    def generate_test_part(
        self,
        size: Tuple[int, int] = (600, 400),
        part_missing: bool = False,
        no_welding: bool = False,
        spatter: bool = False,
    ) -> np.ndarray:
        """
        Generate a synthetic metal part image for demonstration.
        
        Args:
            size: Image dimensions (width, height)
            part_missing: Whether to simulate missing part
            no_welding: Whether to simulate missing welds
            spatter: Whether to add weld spatter
            
        Returns:
            Generated test image
        """
        width, height = size
        
        # Create white background
        img = np.ones((height, width, 3), dtype=np.uint8) * 255
        
        # If part is missing, return background only
        if part_missing:
            return img
        
        # Draw light grey part rectangle
        part_margin = 40
        part_rect = (
            part_margin, 
            part_margin, 
            width - part_margin * 2, 
            height - part_margin * 2
        )
        cv2.rectangle(
            img, 
            (part_rect[0], part_rect[1]),
            (part_rect[0] + part_rect[2], part_rect[1] + part_rect[3]),
            (200, 200, 200), 
            -1
        )
        
        # Define hole positions relative to part rectangle
        hole_radius = 20
        hole_offsets = [
            (int(0.25 * part_rect[2]), int(0.3 * part_rect[3])),  # Top-left
            (int(0.75 * part_rect[2]), int(0.3 * part_rect[3])),  # Top-right
            (int(0.25 * part_rect[2]), int(0.7 * part_rect[3])),  # Bottom-left
            (int(0.75 * part_rect[2]), int(0.7 * part_rect[3])),  # Bottom-right
        ]
        
        # Draw holes (black circles)
        for idx, (dx, dy) in enumerate(hole_offsets):
            center = (part_rect[0] + dx, part_rect[1] + dy)
            cv2.circle(img, center, hole_radius, (0, 0, 0), -1)
        
        # Draw weld seams if required
        if not no_welding:
            weld_thickness = 5
            
            # Calculate weld seam endpoints
            # Top horizontal seam
            p1 = (
                part_rect[0] + hole_offsets[0][0] + hole_radius,
                part_rect[1] + hole_offsets[0][1]
            )
            p2 = (
                part_rect[0] + hole_offsets[1][0] - hole_radius,
                part_rect[1] + hole_offsets[1][1]
            )
            cv2.line(img, p1, p2, (0, 0, 0), weld_thickness)
            
            # Bottom horizontal seam
            p3 = (
                part_rect[0] + hole_offsets[2][0] + hole_radius,
                part_rect[1] + hole_offsets[2][1]
            )
            p4 = (
                part_rect[0] + hole_offsets[3][0] - hole_radius,
                part_rect[1] + hole_offsets[3][1]
            )
            cv2.line(img, p3, p4, (0, 0, 0), weld_thickness)
            
            # Left vertical seam
            p5 = (
                part_rect[0] + hole_offsets[0][0],
                part_rect[1] + hole_offsets[0][1] + hole_radius
            )
            p6 = (
                part_rect[0] + hole_offsets[2][0],
                part_rect[1] + hole_offsets[2][1] - hole_radius
            )
            cv2.line(img, p5, p6, (0, 0, 0), weld_thickness)
            
            # Right vertical seam
            p7 = (
                part_rect[0] + hole_offsets[1][0],
                part_rect[1] + hole_offsets[1][1] + hole_radius
            )
            p8 = (
                part_rect[0] + hole_offsets[3][0],
                part_rect[1] + hole_offsets[3][1] - hole_radius
            )
            cv2.line(img, p7, p8, (0, 0, 0), weld_thickness)
        
        # Add weld spatter (random black dots) if requested
        if spatter:
            rng = np.random.default_rng(int(time.time()))
            spatter_count = rng.integers(20, 80)  # Variable spatter amount
            
            for _ in range(spatter_count):
                # Random position within part area
                x = rng.integers(
                    part_rect[0] + 10, 
                    part_rect[0] + part_rect[2] - 10
                )
                y = rng.integers(
                    part_rect[1] + 10, 
                    part_rect[1] + part_rect[3] - 10
                )
                radius = rng.integers(1, 4)
                cv2.circle(img, (int(x), int(y)), int(radius), (0, 0, 0), -1)
        
        return img
    
    def start_preview(self) -> None:
        """
        Start live camera preview window.
        Press 'q' to quit, 's' to save current frame.
        """
        if not self.connect():
            print("Failed to connect to camera for preview")
            return
        
        print("Camera preview started. Press 'q' to quit, 's' to save frame.")
        
        while True:
            ret, frame = self.cap.read()
            if not ret:
                print("Failed to capture frame")
                break
            
            # Display frame
            cv2.imshow('Camera Preview', frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                # Save current frame
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                filename = f"captured_frame_{timestamp}.jpg"
                cv2.imwrite(filename, frame)
                print(f"Frame saved as {filename}")
        
        cv2.destroyAllWindows()
    
    def __del__(self):
        """Cleanup when object is destroyed."""
        self.disconnect()