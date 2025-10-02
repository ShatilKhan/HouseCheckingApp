"""
Camera calibration utilities for industrial inspection.

This module provides functionality for camera calibration and coordinate
transformations for accurate measurements.
"""

import cv2
import numpy as np
from typing import Optional, Tuple, List


class CameraCalibrator:
    """
    Camera calibration class for handling camera matrix and distortion correction.
    """
    
    def __init__(self):
        self.camera_matrix: Optional[np.ndarray] = None
        self.distortion_coeffs: Optional[np.ndarray] = None
        self.calibrated = False
    
    def calibrate_from_chessboard(self, images: List[np.ndarray], 
                                 pattern_size: Tuple[int, int] = (9, 6),
                                 square_size: float = 1.0) -> bool:
        """
        Calibrate camera using chessboard pattern images.
        
        Args:
            images: List of calibration images
            pattern_size: Chessboard pattern size (corners_x, corners_y)
            square_size: Size of chessboard squares in real units
            
        Returns:
            True if calibration successful, False otherwise
        """
        # Prepare object points
        objp = np.zeros((pattern_size[0] * pattern_size[1], 3), np.float32)
        objp[:, :2] = np.mgrid[0:pattern_size[0], 0:pattern_size[1]].T.reshape(-1, 2)
        objp *= square_size
        
        # Arrays to store object points and image points
        objpoints = []  # 3d points in real world space
        imgpoints = []  # 2d points in image plane
        
        for img in images:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img
            
            # Find chessboard corners
            ret, corners = cv2.findChessboardCorners(gray, pattern_size, None)
            
            if ret:
                objpoints.append(objp)
                
                # Refine corner positions
                criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
                corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
                imgpoints.append(corners2)
        
        if len(objpoints) > 0:
            # Calibrate camera
            ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(
                objpoints, imgpoints, gray.shape[::-1], None, None
            )
            
            if ret:
                self.camera_matrix = mtx
                self.distortion_coeffs = dist
                self.calibrated = True
                return True
        
        return False
    
    def undistort_image(self, img: np.ndarray) -> np.ndarray:
        """
        Correct image distortion using calibration parameters.
        
        Args:
            img: Input distorted image
            
        Returns:
            Undistorted image
        """
        if not self.calibrated:
            return img
        
        return cv2.undistort(img, self.camera_matrix, self.distortion_coeffs)
    
    def pixels_to_mm(self, pixel_distance: float, reference_distance_mm: float, 
                     reference_distance_px: float) -> float:
        """
        Convert pixel measurements to millimeters using a reference measurement.
        
        Args:
            pixel_distance: Distance in pixels to convert
            reference_distance_mm: Known distance in millimeters
            reference_distance_px: Corresponding distance in pixels
            
        Returns:
            Distance in millimeters
        """
        scale_factor = reference_distance_mm / reference_distance_px
        return pixel_distance * scale_factor
    
    def save_calibration(self, filename: str) -> bool:
        """
        Save calibration parameters to file.
        
        Args:
            filename: Path to save calibration data
            
        Returns:
            True if successful, False otherwise
        """
        if not self.calibrated:
            return False
        
        try:
            np.savez(filename, 
                    camera_matrix=self.camera_matrix,
                    distortion_coeffs=self.distortion_coeffs)
            return True
        except Exception:
            return False
    
    def load_calibration(self, filename: str) -> bool:
        """
        Load calibration parameters from file.
        
        Args:
            filename: Path to calibration data file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            data = np.load(filename)
            self.camera_matrix = data['camera_matrix']
            self.distortion_coeffs = data['distortion_coeffs']
            self.calibrated = True
            return True
        except Exception:
            return False