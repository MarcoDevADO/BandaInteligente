from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import serial, time, cv2, os
from ultralytics import YOLO
from db import DBManager
import pyqtgraph as pg
import datetime
from datetime import datetime
import time

#ruta del modelo YOLOv8
#Asegúrate de que la ruta sea correcta y que el modelo esté disponible
ruta_best = os.path.join("runs", "detect", "train4", "weights", "best.pt")
model = YOLO(ruta_best)

class MainApp(QMainWindow):
    def __init__(self, parent=None, *args):
        super(MainApp, self).__init__(parent=parent)
        self.setWindowTitle("ArdControl")
        self.deley = time.time()
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

        # Botones para encender/apagar la banda
        self.PowerButton = QPushButton("Power")
        self.OffButton = QPushButton("OFF")
        self.PowerButton.clicked.connect(self.BandaPower)
        self.OffButton.clicked.connect(self.offbanda)

        #comboBox para seleccionar lotes
        self.comboLotes = QComboBox()

        # Configuración de la gráfica
        self.graphWidget = pg.PlotWidget()
        self.graphWidget.setBackground('w')
        self.graphWidget.setTitle("Registro de piezas por lote")
        self.graphWidget.setLabel('left', 'Cantidad')
        self.graphWidget.setLabel('bottom', 'Tipo')

        #Campo de texto para nuevo lote
        self.nuevolote = QLineEdit()
        self.nuevolote.setEnabled(False)
        self.nuevolote.setStyleSheet("background-color: white")
        self.nuevolote.setPlaceholderText("Nuevo Lote")
        self.nuevolote.setMaxLength(20)

        # CheckBox para agregar nuevo lote
        self.checknuevolote = QCheckBox("Agregar nuevo lote")
        self.checknuevolote.setChecked(False)
        self.checknuevolote.stateChanged.connect(self.nuevolote.setEnabled)

        # Botón para agregar lote
        self.agregarlote = QPushButton("Agregar lote")
        self.agregarlote.clicked.connect(self.agregar_lote)

        # Layout horizontal para botones
        botones_layout = QHBoxLayout()
        botones_layout.addWidget(self.PowerButton)
        botones_layout.addWidget(self.OffButton)

        self.total_label = QLabel()
        self.total_label.setText("Total: 0")
        self.total_label.setStyleSheet("font-size: 20px; font-weight: bold; color: black;")
        self.total_label.setAlignment(Qt.AlignCenter)

        # Layout principal
        layout = QGridLayout()
        layout.addWidget(self.cameraLabel, 0, 0)
        layout.addLayout(botones_layout, 1, 0)
        layout.addWidget(self.comboLotes, 2, 0)
        layout.addWidget(self.nuevolote, 3, 0)
        layout.addWidget(self.agregarlote, 3, 1)
        layout.addWidget(self.checknuevolote, 2, 1)
        layout.addWidget(self.graphWidget, 0, 2)
        layout.addWidget(self.total_label, 1, 2)

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
        self.graphWidget.addLegend()

        # Variables para el gráfico
        self.data_x = list(range(100))
        self.data_y = [0]*100
        self.contador = 0

        # Timer para actualizar la gráfica
        self.graph_timer = QTimer()
        self.graph_timer.timeout.connect(self.actualizar_grafica)
        self.graph_timer.start(500)  # cada medio segundo

        # Inicializar la base de datos para obtener los lotes
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
            print("🔧 Se activo el SERVO")

    def llenar_lista_desde_db(self):
        """Llena el QListWidget con los lotes desde DB"""
        self.comboLotes.clear()
        lotes = self.db.obtener_lotes()
        for lote in lotes:
            self.comboLotes.addItem(lote)

    def agregar_lote(self):
        nuevo_lote = self.nuevolote.text().strip()

        if not nuevo_lote:
            QMessageBox.warning(self, "⚠️ Lote vacío", "Por favor ingresa un nombre para el nuevo lote.")
            return

        if nuevo_lote in [self.comboLotes.itemText(i) for i in range(self.comboLotes.count())]:
            QMessageBox.information(self, "ℹ️ Lote existente", f"El lote '{nuevo_lote}' ya está en la lista.")
            return

        self.comboLotes.addItem(nuevo_lote)
        self.comboLotes.setCurrentText(nuevo_lote)
        self.nuevolote.clear()
        self.checknuevolote.setChecked(False)
        QMessageBox.information(self, "✅ Lote agregado", f"Lote '{nuevo_lote}' agregado exitosamente.")

    def actualizar_grafica(self):
        lote_actual = self.comboLotes.currentText()
        if not lote_actual:
            return

        resultado = self.db.obtener_validos_y_no_validos_por_lote(lote_actual)

        if resultado:
            validos, no_validos = map(float, resultado)
            self.total_label.setText(f"Total: {validos + no_validos}")
            self.graphWidget.setTitle(f"Registro de piezas por lote: {lote_actual}")

            # Limpia cualquier gráfico anterior
            self.graphWidget.clear()

            # Dibuja las barras con etiquetas
            bar_validos = pg.BarGraphItem(x=[1], height=[validos], width=0.4, brush='g')
            bar_no_validos = pg.BarGraphItem(x=[2], height=[no_validos], width=0.4, brush='r')

            # Añadir etiquetas a las barras
            self.graphWidget.addItem(bar_validos)
            self.graphWidget.addItem(bar_no_validos)

            # Ejes con etiquetas personalizadas
            ax = self.graphWidget.getAxis('bottom')
            ax.setTicks([[(1, 'Válidos'), (2, 'No válidos')]])

    def redneural(self):
        ret, frame = self.cap.read()
        if not ret:
            return

        results = model.predict(frame, imgsz=640, conf=0.6)
        annotated_frame = results[0].plot()
        if results[0].boxes and len(results[0].boxes) > 0 and time.time() - self.deley > 5:
            print("🔍 Detectando objetos...")
            nombres_detectados = results[0].names
            clases_detectadas = results[0].boxes.cls.tolist()
            clases_detectadas = [int(c) for c in clases_detectadas]
            nombres = [nombres_detectados[c] for c in clases_detectadas]
            boxes = results[0].boxes.xyxy.tolist()

            lote_actual = self.comboLotes.currentText()

            for i, box in enumerate(boxes):
                print(f"🔍 Objeto detectado: {nombres[i]}")
                x1, y1, x2, y2 = box
                ancho = float(x2 - x1)
                largo = float(y2 - y1)
                nombre = nombres[i]

                valido = True if nombre == "limon" else False
                self.db.insertar_objeto(ancho=ancho, largo=largo, valido=valido,fecha=datetime.now() ,lote=lote_actual)
                print(f"💾 Guardando en DB: {lote_actual}, {nombre}, {ancho}px x {largo}px")
                                      
            if self.arduino:
                # Enviar una señal específica según el tipo de objeto
                for nombre in nombres:
                    if nombre == "limon":
                        self.arduino.write(b"LED_ON\n")
                    if nombre == "nolimon":
                        self.arduino.write(b"LED_OFF\n")
            else:
                if self.arduino:
                    self.arduino.write(b"LED_OFF\n")  # apaga todos los LEDs si no detecta nada

            self.deley = time.time()

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