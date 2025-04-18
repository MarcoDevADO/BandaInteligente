from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import serial, time, cv2, os
from ultralytics import YOLO
from db import DBManager

ruta_best = os.path.join("runs", "detect", "train4", "weights", "best.pt")
model = YOLO(ruta_best)

class MainApp(QMainWindow):
    def __init__(self, parent=None, *args):
        super(MainApp, self).__init__(parent=parent)
        self.setFixedSize(800, 600)
        self.setWindowTitle("ArdControl")
        # Conexión con Arduino
        try:
            self.arduino = serial.Serial('COM5', 9600, timeout=1)
            time.sleep(2)
            print("Conectado al Arduino")
        except:
            self.arduino = None
            print("⚠️ No se pudo conectar al Arduino")

        # QLabel para mostrar la cámara
        self.cameraLabel = QLabel()
        self.cameraLabel.setFixedSize(640, 360)
        self.cameraLabel.setStyleSheet("background-color: black")

        # Botones
        self.PowerButton = QPushButton("Power")
        self.OffButton = QPushButton("OFF")
        self.ServoButton = QPushButton("Servo")
        self.comboLotes = QComboBox()
        self.comboLotes.setFixedHeight(30)

        self.PowerButton.clicked.connect(self.BandaPower)
        self.ServoButton.clicked.connect(self.Servo)
        self.OffButton.clicked.connect(self.offbanda)

        # Layout horizontal para botones
        botones_layout = QHBoxLayout()
        botones_layout.addWidget(self.PowerButton)
        botones_layout.addWidget(self.OffButton)
        botones_layout.addWidget(self.ServoButton)
        

        # Layout principal
        layout = QGridLayout()
        layout.addWidget(self.cameraLabel, 0, 0)
        layout.addLayout(botones_layout, 1, 0)
        layout.addWidget(self.comboLotes, 2, 0)

        # Set layout en widget central
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Iniciar cámara
        self.cap = cv2.VideoCapture(0)
        self.cap.set(3, 1280)
        self.cap.set(4, 720)

        # Timer para actualizar la imagen cada 30 ms
        self.timer = QTimer()
        self.timer.timeout.connect(self.redneural)
        self.timer.start(30)

        self.db = DBManager()
        self.llenar_lista_desde_db()

    def BandaPower(self):
        if self.arduino:
            self.arduino.write(b"RELE_ON\n")
            print("🔌 Relé encendido")

    def offbanda(self):
        if self.arduino:
            self.arduino.write(b"RELE_OFF\n")
            print("🔌 Relé apagado")

    def Servo(self):
        if self.arduino:
            self.arduino.write(b"SERVO_ON\n")
            print("🔧 Servo a 180°")

    def llenar_lista_desde_db(self):
        """Llena el QListWidget con los lotes desde DB"""
        self.comboLotes.clear()
        lotes = self.db.obtener_lotes()
        for lote in lotes:
            self.comboLotes.addItem(lote)

    def redneural(self):
        ret, frame = self.cap.read()
        if not ret:
            return

        results = model.predict(frame, imgsz=640, conf=0.6)
        annotated_frame = results[0].plot()

        # Convertir a QImage para mostrar en QLabel
        rgb_image = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_image).scaled(self.cameraLabel.size(), Qt.KeepAspectRatio)
        self.cameraLabel.setPixmap(pixmap)

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = MainApp()
    print("🔌 Aplicación ArdControl iniciada")
    window.show()
    sys.exit(app.exec_())