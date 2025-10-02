"""
Main Industrial Inspection Application

This module contains the core Inspector class that orchestrates the inspection
workflow, including image processing, measurement recording, and file management.
"""

import cv2
import numpy as np
import pandas as pd
import os
import datetime
from typing import List, Tuple, Dict, Optional

from image_processing.detection import (
    detect_part_presence, 
    detect_holes, 
    detect_spatter,
    calculate_seam_lengths,
    annotate_image
)
from camera.camera_controller import CameraController
from utils.file_utils import get_next_filename, ensure_directory_exists
from utils.logger import setup_logger
from config import Config


class Inspector:
    """
    Encapsulates the inspection workflow: counters, CSV writing and image saving.
    
    This class handles the complete inspection process from image acquisition
    through analysis to result storage and reporting.
    """
    
    def __init__(self, user: str, order_number: str, output_dir: str = ".") -> None:
        """
        Initialize the Inspector with user and order information.
        
        Args:
            user: Username of the operator
            order_number: Production order number
            output_dir: Base directory for output files
        """
        self.user = user
        self.order_number = order_number
        self.ok_counter = 0
        self.nok_counter = 0
        
        # Set up output directory structure
        self.order_dir = os.path.join(output_dir, order_number)
        ensure_directory_exists(self.order_dir)
        
        # Initialize CSV file for measurements
        self.csv_path = os.path.join(self.order_dir, f"{order_number}.csv")
        self._initialize_csv()
        
        # Set up logging
        self.logger = setup_logger(self.order_dir)
        
        # Initialize camera controller
        self.camera = CameraController()
        
        self.logger.info(f"Inspector initialized for order {order_number} by user {user}")
    
    def _initialize_csv(self) -> None:
        """Initialize CSV file with headers if it doesn't exist."""
        if not os.path.exists(self.csv_path):
            header = (
                ["Number", "OK/NOK", "Ordernumber", "Counter", "Date", "Time"]
                + [f"Value{i}" for i in range(1, 13)]
                + ["User"]
            )
            pd.DataFrame(columns=header).to_csv(self.csv_path, index=False)
    
    def process_and_save(self, img: np.ndarray, part_number: str, cam_id: int = 1) -> Dict:
        """
        Analyse an image, update counters, annotate and save results.
        
        Args:
            img: Input image to process
            part_number: Part identification number
            cam_id: Camera ID (default: 1)
            
        Returns:
            Dictionary containing processing results and measurements
        """
        # Convert to grayscale for analysis
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Initialize processing results
        result = {
            'part_number': part_number,
            'cam_id': cam_id,
            'status': 'OK',
            'measurements': [0.0] * 12,
            'defects': [],
            'timestamp': datetime.datetime.now()
        }
        
        # Check if part is present
        part_present = detect_part_presence(gray, Config.PART_DETECTION_THRESHOLD)
        
        if not part_present:
            result['status'] = 'NOK'
            result['defects'].append('Part Missing')
            self.logger.warning(f"Part {part_number}: Part missing detected")
        else:
            # Detect holes and measure diameters
            holes = detect_holes(gray)
            holes = sorted(holes, key=lambda h: h[0][0])  # Sort by x-coordinate
            
            # Record hole measurements
            for idx, hole in enumerate(holes[:4]):  # Maximum 4 holes expected
                _, width, height = hole
                if idx < 2:
                    # Top row holes
                    result['measurements'][idx * 2] = width
                    result['measurements'][idx * 2 + 1] = height
                else:
                    # Bottom row holes
                    result['measurements'][6 + (idx - 2) * 2] = width
                    result['measurements'][6 + (idx - 2) * 2 + 1] = height
            
            # Check for missing holes
            if len(holes) < Config.EXPECTED_HOLE_COUNT:
                result['status'] = 'NOK'
                result['defects'].append(f'Missing holes: expected {Config.EXPECTED_HOLE_COUNT}, found {len(holes)}')
                self.logger.warning(f"Part {part_number}: Missing holes detected")
            
            # Calculate weld seam lengths
            if len(holes) >= 4:
                seam_lengths = calculate_seam_lengths(holes)
                len_top, len_bottom, len_left, len_right = seam_lengths
                
                result['measurements'][4] = len_top     # Top seam
                result['measurements'][5] = len_bottom  # Bottom seam
                result['measurements'][10] = len_left   # Left seam
                result['measurements'][11] = len_right  # Right seam
            else:
                result['status'] = 'NOK'
                result['defects'].append('Insufficient holes for weld measurement')
                seam_lengths = (0.0, 0.0, 0.0, 0.0)
            
            # Detect weld spatter
            spatter_count = detect_spatter(gray)
            if spatter_count > Config.MAX_SPATTER_COUNT:
                result['status'] = 'NOK'
                result['defects'].append(f'Excessive spatter: {spatter_count} detected')
                self.logger.warning(f"Part {part_number}: Excessive spatter detected ({spatter_count})")
        
        # Create annotated image
        if part_present and len(holes) >= 4:
            annotated = annotate_image(img, holes, seam_lengths, spatter_count, result['status'])
        else:
            annotated = img.copy()
            # Add defect annotations
            y_offset = 30
            for defect in result['defects']:
                cv2.putText(annotated, defect, (20, y_offset), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)
                y_offset += 30
        
        # Update counters and save results
        if result['status'] == 'OK':
            self.ok_counter += 1
            counter_val = self.ok_counter
        else:
            self.nok_counter += 1
            counter_val = self.nok_counter
        
        # Save annotated image
        output_path = get_next_filename(
            self.order_dir, result['status'], self.order_number, 
            part_number, counter_val, cam_id
        )
        cv2.imwrite(output_path, annotated)
        result['image_path'] = output_path
        
        # Save measurement data to CSV
        self._save_to_csv(result, counter_val)
        
        # Log processing summary
        self.logger.info(f"Processed part {part_number} (CAM{cam_id}) -> Status: {result['status']}")
        if result['defects']:
            self.logger.info(f"Defects: {', '.join(result['defects'])}")
        
        return result
    
    def _save_to_csv(self, result: Dict, counter_val: int) -> None:
        """
        Save measurement results to CSV file.
        
        Args:
            result: Processing result dictionary
            counter_val: Counter value for this measurement
        """
        # Load existing CSV data
        df_existing = pd.read_csv(self.csv_path)
        next_number = df_existing.shape[0] + 1
        
        # Create new row
        now = result['timestamp']
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H:%M:%S")
        
        row = {
            "Number": next_number,
            "OK/NOK": result['status'],
            "Ordernumber": self.order_number,
            "Counter": counter_val,
            "Date": date_str,
            "Time": time_str,
        }
        
        # Add measurement values
        for i, val in enumerate(result['measurements'], start=1):
            try:
                row[f"Value{i}"] = round(float(val), 2)
            except (ValueError, TypeError):
                row[f"Value{i}"] = 0.0
        
        row["User"] = self.user
        
        # Append to CSV
        df_new = pd.concat([df_existing, pd.DataFrame([row])], ignore_index=True)
        df_new.to_csv(self.csv_path, index=False)
    
    def get_statistics(self) -> Dict:
        """
        Get current inspection statistics.
        
        Returns:
            Dictionary containing OK/NOK counts and rates
        """
        total = self.ok_counter + self.nok_counter
        return {
            'total_parts': total,
            'ok_parts': self.ok_counter,
            'nok_parts': self.nok_counter,
            'ok_rate': (self.ok_counter / total * 100) if total > 0 else 0.0,
            'nok_rate': (self.nok_counter / total * 100) if total > 0 else 0.0
        }
    
    def capture_and_process(self, part_number: str, cam_id: int = 1) -> Dict:
        """
        Capture image from camera and process it.
        
        Args:
            part_number: Part identification number
            cam_id: Camera ID
            
        Returns:
            Processing result dictionary
        """
        img = self.camera.capture_image()
        if img is not None:
            return self.process_and_save(img, part_number, cam_id)
        else:
            self.logger.error(f"Failed to capture image for part {part_number}")
            return {'status': 'ERROR', 'message': 'Image capture failed'}


def main():
    """
    Main function demonstrating the inspection workflow.
    """
    # Create inspector instance
    inspector = Inspector(user="Bob", order_number="749274")
    
    # Generate and process test images
    test_scenarios = [
        ("1568", {}),  # Normal part
        ("1569", {"part_missing": True, "spatter": True}),  # Missing part with spatter
        ("1570", {"part_missing": True}),  # Missing part
        ("1571", {"no_welding": True}),  # No welding
        ("1572", {"spatter": True}),  # Spatter only
        ("1573", {"part_missing": True, "no_welding": True, "spatter": True})  # All defects
    ]
    
    for part_number, defects in test_scenarios:
        # Generate test image
        img = inspector.camera.generate_test_part(**defects)
        
        # Process and save
        result = inspector.process_and_save(img, part_number, cam_id=1)
        
        print(f"Processed part {part_number}:")
        print(f"  Status: {result['status']}")
        print(f"  Defects: {', '.join(result['defects']) if result['defects'] else 'None'}")
        print(f"  Image saved: {result['image_path']}")
        print()
    
    # Display final statistics
    stats = inspector.get_statistics()
    print("Final Statistics:")
    print(f"  Total parts: {stats['total_parts']}")
    print(f"  OK parts: {stats['ok_parts']} ({stats['ok_rate']:.1f}%)")
    print(f"  NOK parts: {stats['nok_parts']} ({stats['nok_rate']:.1f}%)")


if __name__ == "__main__":
    main()