from ultralytics import YOLO
import os

# Definir la ruta base (donde está este script, por ejemplo)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Ruta al modelo
model_path = os.path.join(BASE_DIR, 'models', 'yolov8n.pt')

# Ruta al data.yaml
data_yaml_path = os.path.join(BASE_DIR, 'datasets', 'dataTrain', 'data.yaml')

# Carga del modelo
model = YOLO(model_path)

def main():
    # Entrenamiento
    model.train(
        data=data_yaml_path,
        epochs=50,
        batch=64,
        imgsz=640,
        device='cpu'  # Cambiar a 'cuda' si tenés GPU
    )

if __name__ == '__main__':
    main()