"""
Detection algorithms for industrial inspection.

This module contains computer vision routines for detecting part presence,
measuring hole diameters, measuring weld seam lengths, and detecting
weld spatter in metal parts.
"""

import cv2
import numpy as np
from typing import List, Tuple, Dict


def detect_part_presence(gray: np.ndarray, mean_threshold: float = 240.0) -> bool:
    """
    Return True if a part (grey region) is present, otherwise False.
    
    Args:
        gray: Grayscale input image
        mean_threshold: Threshold for mean pixel value to determine part presence
        
    Returns:
        True if part is detected, False otherwise
    """
    mean_val = float(gray.mean())
    return mean_val < mean_threshold


def detect_holes(gray: np.ndarray) -> List[Tuple[Tuple[int, int], float, float]]:
    """
    Detect circular holes via the Hough Circle Transform.
    
    Args:
        gray: Grayscale input image
        
    Returns:
        List of tuples containing ((x, y), width, height) for each detected hole
    """
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    circles = cv2.HoughCircles(
        blurred, cv2.HOUGH_GRADIENT,
        dp=1.0, minDist=50,
        param1=50, param2=20,
        minRadius=10, maxRadius=40
    )
    
    holes: List[Tuple[Tuple[int, int], float, float]] = []
    if circles is not None:
        circles = np.uint16(np.around(circles))
        for circle in circles[0, :]:
            x, y, r = circle
            diameter = float(r * 2)
            holes.append(((int(x), int(y)), diameter, diameter))
    
    return holes


def detect_spatter(gray: np.ndarray) -> int:
    """
    Detect number of small dark blobs indicating weld spatter.
    
    Args:
        gray: Grayscale input image
        
    Returns:
        Number of spatter instances detected
    """
    _, thresh = cv2.threshold(gray, 220, 255, cv2.THRESH_BINARY_INV)
    kernel = np.ones((3, 3), np.uint8)
    cleaned = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=2)
    
    contours, _ = cv2.findContours(cleaned, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    spatter_count = 0
    
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if 3 < area < 100:  # Filter by area to identify spatter
            spatter_count += 1
            
    return spatter_count


def calculate_seam_lengths(holes: List[Tuple[Tuple[int, int], float, float]]) -> Tuple[float, float, float, float]:
    """
    Calculate weld seam lengths from hole positions.
    
    Args:
        holes: List of detected holes with positions and diameters
        
    Returns:
        Tuple of (top_length, bottom_length, left_length, right_length)
    """
    if len(holes) < 4:
        return 0.0, 0.0, 0.0, 0.0
    
    # Sort holes by position to identify top/bottom rows and left/right columns
    holes_by_y = sorted(holes, key=lambda h: h[0][1])
    top_row = sorted(holes_by_y[:2], key=lambda h: h[0][0])
    bottom_row = sorted(holes_by_y[2:4], key=lambda h: h[0][0])
    
    # Calculate radii
    rad_top_left = top_row[0][1] / 2.0
    rad_top_right = top_row[1][1] / 2.0
    rad_bot_left = bottom_row[0][1] / 2.0
    rad_bot_right = bottom_row[1][1] / 2.0
    
    def distance(p1, p2):
        return float(np.hypot(p2[0] - p1[0], p2[1] - p1[1]))
    
    # Calculate seam lengths (distance between hole centers minus radii)
    len_top = distance(top_row[0][0], top_row[1][0]) - (rad_top_left + rad_top_right)
    len_bottom = distance(bottom_row[0][0], bottom_row[1][0]) - (rad_bot_left + rad_bot_right)
    len_left = distance(top_row[0][0], bottom_row[0][0]) - (rad_top_left + rad_bot_left)
    len_right = distance(top_row[1][0], bottom_row[1][0]) - (rad_top_right + rad_bot_right)
    
    return len_top, len_bottom, len_left, len_right


def annotate_image(img: np.ndarray, holes: List[Tuple[Tuple[int, int], float, float]], 
                  seam_lengths: Tuple[float, float, float, float], 
                  spatter_count: int, status: str) -> np.ndarray:
    """
    Annotate image with measurement overlays and status indicators.
    
    Args:
        img: Input image to annotate
        holes: List of detected holes
        seam_lengths: Tuple of seam lengths (top, bottom, left, right)
        spatter_count: Number of detected spatter instances
        status: Overall status ("OK" or "NOK")
        
    Returns:
        Annotated image
    """
    annotated = img.copy()
    
    # Draw holes with diameter labels
    for hole in holes:
        centre, width, _ = hole
        cv2.circle(annotated, centre, int(width/2), (0, 255, 0), 2)
        cv2.putText(
            annotated, f"D: {width:.2f}",
            (centre[0] - 40, centre[1] - 10),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1
        )
    
    # Draw seam measurements if we have enough holes
    if len(holes) >= 4:
        len_top, len_bottom, len_left, len_right = seam_lengths
        
        holes_by_y = sorted(holes, key=lambda h: h[0][1])
        top_row = sorted(holes_by_y[:2], key=lambda h: h[0][0])
        bottom_row = sorted(holes_by_y[2:4], key=lambda h: h[0][0])
        
        rad_top_left = top_row[0][1] / 2.0
        rad_top_right = top_row[1][1] / 2.0
        rad_bot_left = bottom_row[0][1] / 2.0
        rad_bot_right = bottom_row[1][1] / 2.0
        
        # Draw top seam
        p1_top = (int(top_row[0][0][0] + rad_top_left), int(top_row[0][0][1]))
        p2_top = (int(top_row[1][0][0] - rad_top_right), int(top_row[1][0][1]))
        cv2.line(annotated, p1_top, p2_top, (0, 255, 0), 2)
        mid_top = (int((p1_top[0] + p2_top[0]) / 2), int(p1_top[1] - 10))
        cv2.putText(annotated, f"{len_top:.2f}", mid_top, cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, (0, 255, 0), 1)
        
        # Draw bottom seam
        p1_bot = (int(bottom_row[0][0][0] + rad_bot_left), int(bottom_row[0][0][1]))
        p2_bot = (int(bottom_row[1][0][0] - rad_bot_right), int(bottom_row[1][0][1]))
        cv2.line(annotated, p1_bot, p2_bot, (0, 255, 0), 2)
        mid_bot = (int((p1_bot[0] + p2_bot[0]) / 2), int(p1_bot[1] + 15))
        cv2.putText(annotated, f"{len_bottom:.2f}", mid_bot, cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, (0, 255, 0), 1)
        
        # Draw left seam
        p1_left = (int(top_row[0][0][0]), int(top_row[0][0][1] + rad_top_left))
        p2_left = (int(bottom_row[0][0][0]), int(bottom_row[0][0][1] - rad_bot_left))
        cv2.line(annotated, p1_left, p2_left, (0, 255, 0), 2)
        mid_left = (int(p1_left[0] - 50), int((p1_left[1] + p2_left[1]) / 2))
        cv2.putText(annotated, f"{len_left:.2f}", mid_left, cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, (0, 255, 0), 1)
        
        # Draw right seam
        p1_right = (int(top_row[1][0][0]), int(top_row[1][0][1] + rad_top_right))
        p2_right = (int(bottom_row[1][0][0]), int(bottom_row[1][0][1] - rad_bot_right))
        cv2.line(annotated, p1_right, p2_right, (0, 255, 0), 2)
        mid_right = (int(p1_right[0] + 10), int((p1_right[1] + p2_right[1]) / 2))
        cv2.putText(annotated, f"{len_right:.2f}", mid_right, cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, (0, 255, 0), 1)
    
    # Add status and defect annotations
    color = (0, 0, 255) if status == "NOK" else (0, 255, 0)
    y_offset = 30
    
    if status == "NOK":
        if len(holes) < 4:
            cv2.putText(annotated, "Hole Missing", (20, y_offset), cv2.FONT_HERSHEY_SIMPLEX,
                        1.0, (0, 0, 255), 2)
            y_offset += 30
        
        if spatter_count > 5:
            cv2.putText(annotated, f"Spatter: {spatter_count}", (20, y_offset), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)
            y_offset += 30
    
    return annotated