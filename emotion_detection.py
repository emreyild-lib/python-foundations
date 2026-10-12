#pip install opencv-python deepface
#pip install tf-keras
#pip uninstall tensorflow
#yy


import cv2
from deepface import DeepFace

# Start webcam
import cv2, time

def open_cam(idx):
    cap = cv2.VideoCapture(idx, cv2.CAP_AVFOUNDATION)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    cap.set(cv2.CAP_PROP_FPS, 30)
    return cap

# try a few indices
for i in [0,1,2]:
    cap = open_cam(i)
    time.sleep(0.5)               # warm-up
    ok, frame = cap.read()
    print("index", i, "backend", cap.getBackendName(), "opened", cap.isOpened(), "read", ok)
    if ok:
        use_idx = i
        break
    cap.release()
else:
    raise SystemExit("No camera delivered frames. Check permissions and busy apps.")

cap = open_cam(use_idx)
for _ in range(10): cap.read()    # extra warm-up

print("Press 'q' to quit.")
while True:
    ok, frame = cap.read()
    if not ok:
        print("Failed to grab frame.")
        break
    cv2.imshow("Camera test", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cap.release(); cv2.destroyAllWindows()

cap = cv2.VideoCapture(0)

print("Press 'q' to quit.")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame.")
        break

    try:
        # Analyze emotions using DeepFace
        result = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False)
        emotion = result[0]['dominant_emotion']

        # Display emotion result on frame
        cv2.putText(frame, f'Emotion: {emotion}', (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    except Exception as e:
        cv2.putText(frame, 'No face detected', (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    # Show the frame
    cv2.imshow("Webcam - Emotion Detection", frame)

    # Exit on pressing 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
