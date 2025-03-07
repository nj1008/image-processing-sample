# -*- coding: utf-8 -*-
"""image-process.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1X21_SNNlbsQeJEt6adAGPKWRqlI4J9xW

Code for image1.jpg
"""

# Import necessary libraries
import cv2
import numpy as np
import matplotlib.pyplot as plt

# Load the image in grayscale mode
image_file = 'image1.jpg'  # Provide the correct path if the image is not in the current directory
grayscale_img = cv2.imread(image_file, cv2.IMREAD_GRAYSCALE)

# Check if the image loaded successfully
if grayscale_img is None:
    print("Error: Image cannot be loaded or found.")
else:
    print("Image successfully loaded.")

# Step 1: Dark regions (Air) - Threshold the darker areas
_, air_mask = cv2.threshold(grayscale_img, 50, 255, cv2.THRESH_BINARY_INV)

# Step 2: Bright solid regions - Threshold the brighter areas
_, bright_mask = cv2.threshold(grayscale_img, 200, 255, cv2.THRESH_BINARY)

# Detect edges for hollow/void identification
edges_detected = cv2.Canny(grayscale_img, 100, 200)

# Step 3: Solid areas with hollows - Use contours to identify hollow areas
contours, _ = cv2.findContours(edges_detected, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
hollowed_area_mask = np.zeros_like(grayscale_img)
for contour in contours:
    if cv2.contourArea(contour) > 50:  # Remove small noise
        cv2.drawContours(hollowed_area_mask, [contour], -1, 255, thickness=-1)

# Step 4: Non-hollow solid areas - Bright regions excluding hollowed areas
non_hollow_area_mask = cv2.bitwise_and(bright_mask, cv2.bitwise_not(hollowed_area_mask))

# Calculate area percentages for different regions
total_pixels = grayscale_img.size
air_region_pixels = np.sum(air_mask > 0)
hollowed_area_pixels = np.sum(hollowed_area_mask > 0)
non_hollow_area_pixels = np.sum(non_hollow_area_mask > 0)
void_area_pixels = total_pixels - (air_region_pixels + hollowed_area_pixels + non_hollow_area_pixels)

air_area_percentage = air_region_pixels / total_pixels * 100
hollow_area_percentage = void_area_pixels / total_pixels * 100
hollowed_area_percentage = hollowed_area_pixels / total_pixels * 100
non_hollow_area_percentage = non_hollow_area_pixels / total_pixels * 100

# Display the results visually
fig, axes = plt.subplots(1, 4, figsize=(20, 5))

axes[0].imshow(air_mask, cmap='gray')
axes[0].set_title("Air (Dark) Regions")

axes[1].imshow(hollowed_area_mask, cmap='gray')
axes[1].set_title("Hollowed-Solid Regions")

axes[2].imshow(non_hollow_area_mask, cmap='gray')
axes[2].set_title("Non-Hollow-Solid Regions")

axes[3].imshow(edges_detected, cmap='gray')
axes[3].set_title("Detected Hollow/Voids")

# Hide axes for clarity
for ax in axes:
    ax.axis('off')

plt.tight_layout()
plt.show()

# Print the area percentages
print("Area Percentages (%):")
print(f"Air (Dark) Regions: {air_area_percentage:.2f}%")
print(f"Void Regions: {hollow_area_percentage:.2f}%")
print(f"Hollowed-Solid Regions: {hollowed_area_percentage:.2f}%")
print(f"Non-Hollow-Solid Regions: {non_hollow_area_percentage:.2f}%")

"""Code for image2.jpg"""

import cv2
import numpy as np
import matplotlib.pyplot as plt

def detect_particles_and_area_ratio(image_path):
    # Read the image
    img = cv2.imread(image_path)

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Apply blurring to reduce noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Perform edge detection using Canny
    edges = cv2.Canny(blurred, 50, 150)

    # Detect circles using HoughCircles
    circles = cv2.HoughCircles(
        blurred,
        cv2.HOUGH_GRADIENT,
        dp=1.2,  # Adjust the inverse ratio of the accumulator resolution to the image resolution
        minDist=20,  # Minimum distance between detected centers
        param1=50,  # Higher value to reduce false positives
        param2=30,  # Lower value increases sensitivity to detecting more circles
        minRadius=5,  # Minimum radius of the circles to detect
        maxRadius=50  # Maximum radius of the circles to detect
    )

    # Initialize variables for areas
    circular_area = 0
    non_circular_area = 0

    # Initialize counters for circular and non-circular particles
    num_circles = 0
    num_non_circles = 0

    # Initialize a list to store diameters
    diameters = []

    # If circles are detected, process and count them
    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")

        for (x, y, r) in circles:
            # Calculate the area for circular particles
            circular_area += np.pi * (r ** 2)
            diameters.append(2 * r)

            # Draw the circle and center on the image
            cv2.circle(img, (x, y), r, (0, 255, 0), 2)
            cv2.circle(img, (x, y), 2, (0, 0, 255), 3)

            # Increment the circle count
            num_circles += 1

    # Perform contour analysis for non-circular particles (if applicable)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        # Calculate area and perimeter
        area = cv2.contourArea(contour)
        perimeter = cv2.arcLength(contour, True)

        # Calculate circularity
        if perimeter == 0:
            circularity = 0
        else:
            circularity = 4 * np.pi * area / (perimeter ** 2)

        # If the circularity is below threshold, classify as non-circular
        if circularity < 0.8:
            non_circular_area += area
            num_non_circles += 1
            # Draw the contour as red for non-circular particles
            cv2.drawContours(img, [contour], -1, (0, 0, 255), 2)

    # Calculate area ratios based on particle areas
    total_particle_area = circular_area + non_circular_area  # Sum of circular and non-circular areas
    circular_area_ratio = (circular_area / total_particle_area) * 100 if total_particle_area > 0 else 0
    non_circular_area_ratio = (non_circular_area / total_particle_area) * 100 if total_particle_area > 0 else 0

    # Calculate average diameter and standard deviation
    if diameters:
        avg_diameter = np.mean(diameters)
        std_dev_diameter = np.std(diameters)
    else:
        avg_diameter = 0
        std_dev_diameter = 0

    # Display the results
    print("Number of circular particles:", num_circles)
    print("Number of non-circular particles:", num_non_circles)
    print(f"Circular area ratio: {circular_area_ratio:.2f}%")
    print(f"Non-circular area ratio: {non_circular_area_ratio:.2f}%")
    print(f"Average diameter of circles: {avg_diameter:.2f} pixels")
    print(f"Standard deviation of diameter: {std_dev_diameter:.2f} pixels")

    # Show the image with detected particles
    plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    plt.title("Detected Particles (Circular: Green, Non-Circular: Red)")
    plt.axis('off')
    plt.show()

# Example usage
image_path = "image2.jpg"
detect_particles_and_area_ratio(image_path)