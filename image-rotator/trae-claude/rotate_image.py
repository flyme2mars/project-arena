import cv2
import numpy as np
import argparse

def rotate_image(image, angle):
    # Get image dimensions
    height, width = image.shape[:2]
    # Calculate the center of rotation
    center = (width // 2, height // 2)
    
    # Create rotation matrix
    rotation_matrix = cv2.getRotationMatrix2D(center, -angle, 1.0)  # Negative angle for clockwise rotation
    
    # Perform rotation while maintaining original dimensions
    rotated = cv2.warpAffine(image, rotation_matrix, (width, height),
                            flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT,
                            borderValue=(0, 0, 0))  # Black background
    return rotated

def create_rotating_video(input_image_path, output_video_path, duration=10, fps=30):
    # Read the input image
    image = cv2.imread(input_image_path, cv2.IMREAD_UNCHANGED)
    
    if image is None:
        raise ValueError(f"Could not read image from {input_image_path}")
    
    # If image has an alpha channel, convert it to RGB with black background
    if image.shape[-1] == 4:
        alpha = image[:, :, 3] / 255.0
        image_rgb = image[:, :, :3]
        black_background = np.zeros_like(image_rgb)
        image = (alpha[:, :, np.newaxis] * image_rgb + 
                (1 - alpha[:, :, np.newaxis]) * black_background).astype(np.uint8)
    
    # Calculate total frames
    total_frames = int(duration * fps)
    
    # Create video writer with H.264 codec
    fourcc = cv2.VideoWriter_fourcc(*'avc1')
    video = cv2.VideoWriter(output_video_path, fourcc, fps, 
                           (image.shape[1], image.shape[0]))
    
    if not video.isOpened():
        # Fallback to MP4V codec if H.264 is not available
        video.release()
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        video = cv2.VideoWriter(output_video_path, fourcc, fps,
                               (image.shape[1], image.shape[0]))
    
    # Create accelerating rotation
    # Use exponential function for acceleration with higher exponent for faster acceleration
    t = np.linspace(0, 1, total_frames)
    angles = 2160 * (np.exp(4 * t) - 1) / (np.exp(4) - 1)  # Accelerating 6 full rotations with steeper curve
    
    # Generate and write frames
    for angle in angles:
        rotated_frame = rotate_image(image, angle)
        video.write(rotated_frame)
    
    # Release video writer
    video.release()

def main():
    parser = argparse.ArgumentParser(description='Create a rotating video from an image')
    parser.add_argument('input_image', help='Path to input PNG image')
    parser.add_argument('output_video', help='Path to output video file')
    args = parser.parse_args()
    
    create_rotating_video(args.input_image, args.output_video)
    print(f"Video created successfully at {args.output_video}")

if __name__ == '__main__':
    main()