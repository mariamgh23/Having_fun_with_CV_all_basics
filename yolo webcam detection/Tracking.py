from ultralytics import YOLO
import cv2
import os

print("=" * 50)
print("YOLOv8 Object Detection Setup")
print("=" * 50)

# Step 1: Clean up corrupted model files
print("\n[1/4] Checking for corrupted model files...")

# Remove from current directory
if os.path.exists('yolov8n.pt'):
    try:
        os.remove('yolov8n.pt')
        print("✓ Removed old model from current directory")
    except Exception as e:
        print(f"⚠ Could not remove local model: {e}")

# Remove from cache
cache_path = os.path.expanduser('~/.ultralytics/weights/yolov8n.pt')
if os.path.exists(cache_path):
    try:
        os.remove(cache_path)
        print("✓ Removed cached model")
    except Exception as e:
        print(f"⚠ Could not remove cached model: {e}")

# Step 2: Download fresh model
print("\n[2/4] Downloading YOLOv8 model...")
try:
    model = YOLO('yolov8n.pt')
    print("✓ Model downloaded and loaded successfully!")
except Exception as e:
    print(f"✗ Error loading model: {e}")
    print("\nPlease manually download from:")
    print("https://github.com/ultralytics/assets/releases/download/v8.3.0/yolov8n.pt")
    exit(1)

# Step 3: Open webcam
print("\n[3/4] Opening webcam...")
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("✗ Error: Could not open webcam")
    print("Please check:")
    print("  - Camera is connected")
    print("  - Camera permissions are granted")
    print("  - No other application is using the camera")
    exit(1)

# Test frame capture
ret, test_frame = cap.read()
if not ret:
    print("✗ Error: Cannot read from webcam")
    cap.release()
    exit(1)

print(f"✓ Webcam opened successfully!")
print(f"  Frame size: {test_frame.shape[1]}x{test_frame.shape[0]}")

# Step 4: Start detection
print("\n[4/4] Starting object detection...")
print("\n" + "=" * 50)
print("CONTROLS:")
print("  - Press 'q' to quit")
print("  - Press 'Esc' to quit")
print("=" * 50 + "\n")

# Create window
cv2.namedWindow("YOLOv8 Object Detection", cv2.WINDOW_NORMAL)

frame_count = 0

try:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("\n✗ Failed to grab frame from webcam")
            break

        frame_count += 1
        
        # Show progress every 30 frames
        if frame_count % 30 == 0:
            print(f"Processing... Frames: {frame_count}", end='\r')

        # Run YOLO detection
        results = model(frame, conf=0.3, verbose=False)
        annotated_frame = results[0].plot()
        
        # Display the frame
        cv2.imshow("YOLOv8 Object Detection", annotated_frame)

        # Handle key presses
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == 27:  # 'q' or 'Esc'
            print("\n\n✓ Stopping detection...")
            break

except KeyboardInterrupt:
    print("\n\n✓ Interrupted by user...")

except Exception as e:
    print(f"\n✗ Error during detection: {e}")

finally:
    # Clean up
    print("\nCleaning up...")
    cap.release()
    cv2.destroyAllWindows()
    cv2.waitKey(1)  # Extra waitKey for cleanup
    print("✓ Done!")
    print(f"Total frames processed: {frame_count}")
    print("\n" + "=" * 50)