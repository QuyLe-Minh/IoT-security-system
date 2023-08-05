import requests
import cv2
import numpy as np
IP_ADDRESS = "172.20.10.4"  # Replace with your ESP32-CAM IP address
while True:
    try:
        # Send an HTTP GET request to the ESP32-CAM server to get the camera image
        response = requests.get(f"http://{IP_ADDRESS}/capture")
        
        # Convert the response content to a NumPy array
        img_array = np.frombuffer(response.content, dtype=np.uint8)
        
        # Decode the image using OpenCV
        img = cv2.imdecode(img_array, flags=cv2.IMREAD_COLOR)
        
        # Display the image
        cv2.imshow("ESP32-CAM Feed", img)
        
        # Check for the 'q' key press to exit the loop and close the window
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        
    except Exception as e:
        print(f"Error: {e}")

# Release resources and close the window
cv2.destroyAllWindows()
