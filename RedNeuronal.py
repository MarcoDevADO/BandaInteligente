import cv2
from ultralytics import YOLO
import os

ruta_best = os.path.join("runs", "detect", "train4", "weights", "best.pt")

cap = cv2.VideoCapture(0)  # Cambia 0 por la ruta de tu video si es necesario
cap.set(3,1280)  # Ancho
cap.set(4,720)  # Alto

model = YOLO(ruta_best)

while True:
    ret, frame = cap.read()
    results = model.predict(frame, imgsz=640, conf=0.6)

    if len(results) != 0:
        for ret in results:
            print("DETECTADO")

        annotated_frame = results[0].plot()

    cv2.imshow("Detección", annotated_frame)
    t = cv2.waitKey(5)
    if t == 27:  # Presiona 'Esc' para salir
        break

cap.release()
cv2.destroyAllWindows()