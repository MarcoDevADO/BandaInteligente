from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import serial, time, cv2, os
from ultralytics import YOLO
import serial.tools.list_ports
from db import DBManager
import pyqtgraph as pg
import datetime
from datetime import datetime
import time

#ruta del modelo YOLOv8
#Asegúrate de que la ruta sea correcta y que el modelo esté disponible
ruta_best = os.path.join("best.pt")
model = YOLO(ruta_best)

class MainApp(QMainWindow):
    def __init__(self, parent=None, *args):
        super(MainApp, self).__init__(parent=parent)
        self.setWindowTitle("ArdControl")
        self.deley = time.time()
        # Conexión con Arduino
        self.selected_com = None
        self.selected_camera_index = 0

        # ComboBox para seleccionar puerto COM
        self.comboCOMs = QComboBox()
        self.comboCOMs.addItems(self.obtener_puertos_com())
        self.comboCOMs.currentTextChanged.connect(self.actualizar_puerto_com)

        # ComboBox para seleccionar cámara
        self.comboCamaras = QComboBox()
        camaras = self.obtener_camaras_disponibles()
        self.comboCamaras.addItems([f"Cam {i}" for i in camaras])
        self.comboCamaras.currentIndexChanged.connect(lambda index: self.actualizar_indice_camara(camaras[index]))

        # QLabel para mostrar la cámara
        self.cameraLabel = QLabel()
        self.cameraLabel.setFixedSize(640, 360)
        self.cameraLabel.setStyleSheet("background-color: black")

        # Botones con sus funciones
        self.DerechaButton = QPushButton("LADO 1 ►")
        self.IzquierdaButton = QPushButton("LADO 2 ◄")
        self.BotonConecArd = QPushButton("Conectar con Arduino")
        self.BotonConecCam = QPushButton("Conectar con Camara")
        self.BotonServo = QPushButton("Servo")
        self.DerechaButton.clicked.connect(self.DercPower)
        self.IzquierdaButton.clicked.connect(self.IzquiPower)
        self.BotonConecArd.clicked.connect(self.ConectarArd)
        self.BotonConecCam.clicked.connect(self.ConectarCam)
        self.BotonServo.clicked.connect(self.Servo)

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
        botones_layout.addWidget(self.DerechaButton)
        botones_layout.addWidget(self.IzquierdaButton)
        
        # Etiqueta para mostrar el total
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
        layout.addWidget(self.BotonConecArd, 4, 2)
        layout.addWidget(self.BotonConecCam, 5, 2)
        layout.addWidget(self.checknuevolote, 2, 1)
        layout.addWidget(self.graphWidget, 0, 2)
        layout.addWidget(self.total_label, 1, 2)
        layout.addWidget(QLabel("Puerto COM:"), 4, 0)
        layout.addWidget(self.comboCOMs, 4, 1)
        layout.addWidget(QLabel("Cámara:"), 5, 0)
        layout.addWidget(self.comboCamaras, 5, 1)
        layout.addWidget(self.BotonServo, 3, 2)

        # Set layout en widget central
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

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
        self.graph_timer.start(500)

        # Inicializar la base de datos para obtener los lotes
        self.db = DBManager()
        self.llenar_lista_desde_db()
        
        
        
        self.objeto_actual = None
        self.objeto_visto_anteriormente = None
        self.hilo_espera_sensor = None

    def closeEvent(self, event):
        if self.hilo_espera_sensor and self.hilo_espera_sensor.isRunning():
            self.hilo_espera_sensor.detener()
            self.hilo_espera_sensor.wait()
        event.accept()

    
    def ConectarArd(self):
        if self.comboCOMs.count() > 0:
            self.selected_com = self.comboCOMs.currentText()
            try:
                self.arduino = serial.Serial(self.selected_com, 9600, timeout=1)
                time.sleep(2)
                QMessageBox.information(self, "✅ Conexión exitosa", f"Conectado a {self.selected_com}")
            except:
                self.arduino = None
                QMessageBox.critical(self, "❌ Error de conexión", f"No se pudo conectar a {self.selected_com}")

    def ConectarCam(self):
        if self.comboCamaras.count() > 0:
            self.selected_camera_index = int(self.comboCamaras.currentText().split()[1])
            try:
                self.cap = cv2.VideoCapture(self.selected_camera_index)
                self.cap.set(3, 1280)
                self.cap.set(4, 720)
                QMessageBox.information(self, "✅ Conexión exitosa", f"Conectado a la cámara {self.selected_camera_index}")
            except:
                QMessageBox.critical(self, "❌ Error de conexión", f"No se pudo conectar a la cámara {self.selected_camera_index}")

    def DercPower(self):
            self.enviar_comando("D")
            self.ValorDireccion = "D"

    def IzquiPower(self):
            self.enviar_comando("I")
            self.ValorDireccion = "I"

    def Servo(self):
            self.enviar_comando("SERVO_ON")

    def llenar_lista_desde_db(self):
        """Llena el QListWidget con los lotes desde DB"""
        self.comboLotes.clear()
        lotes = self.db.obtener_lotes()
        for lote in lotes:
            self.comboLotes.addItem(lote)

    def enviar_comando(self, comando):
        if self.arduino and self.arduino.is_open:
            print(f"🔄 Enviando comando: {comando}")
            try:
                self.arduino.write(comando.encode('utf-8') + b"\n")
            except Exception as e:
                QMessageBox.critical(self, "❌ Error", "No hay conexión con el Arduino.")
        else:
            QMessageBox.critical(self, "❌ Error", "Error inesperado")

    def agregar_lote(self):
        nuevo_lote = self.nuevolote.text().strip()

        #Verifica si el LineEdit esta vacio sino es sino agrega el lote
        #y limpia el campo de texto
        if not nuevo_lote:
            QMessageBox.warning(self, "⚠️ Lote vacío", "Por favor ingresa un nombre para el nuevo lote.")
            return

        if nuevo_lote in [self.comboLotes.itemText(i) for i in range(self.comboLotes.count())]:
            QMessageBox.information(self, "ℹ️ Lote existente", f"El lote '{nuevo_lote}' ya está en la lista.")
            return

        # Agregar el nuevo lote al comboBox
        self.comboLotes.addItem(nuevo_lote)
        self.comboLotes.setCurrentText(nuevo_lote)
        self.nuevolote.clear()
        self.checknuevolote.setChecked(False)
        QMessageBox.information(self, "✅ Lote agregado", f"Lote '{nuevo_lote}' agregado exitosamente.")

    def obtener_puertos_com(self):
        return [port.device for port in serial.tools.list_ports.comports()]
    
    def actualizar_puerto_com(self, com):
        self.selected_com = com

    def actualizar_indice_camara(self, index):
        self.selected_camera_index = index

    def obtener_camaras_disponibles(self,max_camaras=5):
        disponibles = []
        for i in range(max_camaras):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                disponibles.append(i)
                cap.release()
        return disponibles

    def actualizar_grafica(self):
        lote_actual = self.comboLotes.currentText()
        if not lote_actual:
            return

        resultado = self.db.obtener_validos_y_no_validos_por_lote(lote_actual)
        
        # Verifica si el resultado es válido
        if resultado:
            try:
                validos, no_validos = map(float, resultado)
            except:
                return
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

    def pixeles_a_cm(pixeles):
        tamaño_en_pixeles = 160
        tamaño_real_cm = 8
        cm_por_pixel = tamaño_real_cm / tamaño_en_pixeles
        return pixeles * cm_por_pixel
    
    def iniciar_espera_sensor_ir(self):
        if self.arduino and self.arduino.is_open:
            # Detiene hilo anterior si aún está corriendo
            if self.hilo_espera_sensor and self.hilo_espera_sensor.isRunning():
                self.hilo_espera_sensor.detener()
                self.hilo_espera_sensor.wait()

            # Limpia el buffer serial para evitar lecturas antiguas
            self.arduino.reset_input_buffer()

            # Crea y lanza un nuevo hilo
            self.hilo_espera_sensor = EsperaSensorThread(self.arduino)
            self.hilo_espera_sensor.deteccion.connect(self.accion_tras_deteccion_sensor)
            self.hilo_espera_sensor.start()
            print("🔵 Esperando detección del sensor IR...")
        else:
            print("❌ Arduino no está conectado.")


    def accion_tras_deteccion_sensor(self):
        print("🟢 Activando servo tras detección IR")
        QTimer.singleShot(1000,lambda:self.enviar_comando("SERVO_ON"))
        self.enviar_comando("LED_OFF")


    
    def obtencion_datos(self,results):
        if results[0].boxes and len(results[0].boxes) > 0 and time.time() - self.deley > 6:
            # Obtener los nombres y clases de los objetos detectados
            nombres_detectados = results[0].names
            clases_detectadas = results[0].boxes.cls.tolist()
            clases_detectadas = [int(c) for c in clases_detectadas]
            nombres = [nombres_detectados[c] for c in clases_detectadas]
            boxes = results[0].boxes.xyxy.tolist()
            lote_actual = self.comboLotes.currentText()

            #bucle para guardar los objetos detectados en la base de datos
            for i, box in enumerate(boxes):
                # Obtener el nombre y las dimensiones del objeto
                nombre = nombres[i]
                x1, y1, x2, y2 = box
                ancho = float(x2 - x1)
                largo = float(y2 - y1)
                nombre = nombres[i]

                # Convertir de píxeles a centímetros
                ancho_cm = ancho #self.pixeles_a_cm(ancho)
                largo_cm = largo #self.pixeles_a_cm(largo)
                # Guardar en la base de datos
                valido = True if nombre == "good" else False
                self.db.insertar_objeto(ancho=ancho_cm, largo=largo_cm, valido=valido,fecha=datetime.now() ,lote=lote_actual)

                if nombre == "bad":
                    self.enviar_comando("LED_F")
                    #QTimer.singleShot(4000, lambda: self.Servo())
                    self.iniciar_espera_sensor_ir()
                    QTimer.singleShot(2000, lambda: self.enviar_comando("LED_OFF"))
                    
                if nombre == "good":
                    self.enviar_comando("LED_T")
                    QTimer.singleShot(2000, lambda: self.enviar_comando("LED_OFF"))

                QTimer.singleShot(2000, lambda: self.enviar_comando(self.ValorDireccion))
                self.deley = time.time()  # Actualizar deley después de cada detección

    def redneural(self):
        
        # Verifica si la cámara está abierta
        if not hasattr(self, 'cap') or not self.cap.isOpened():
            return
        
        # Lee un frame de la cámara
        ret, frame = self.cap.read()

        # Si no se puede leer el frame, retorna
        if not ret:
            return
        
        # Redimensiona el frame a 640x640
        results = model.predict(frame, imgsz=640, conf=0.6)
        annotated_frame = results[0].plot()
        self.obtencion_datos(results)

        # Convertir a QImage para mostrar en QLabel
        rgb_image = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_image).scaled(self.cameraLabel.size(), Qt.KeepAspectRatio)
        self.cameraLabel.setPixmap(pixmap)

class EsperaSensorThread(QThread):
    deteccion = pyqtSignal()

    def __init__(self, arduino):
        super().__init__()
        self.arduino = arduino
        self.running = True

    def run(self):
        while self.running:
            if self.arduino.in_waiting > 0:
                linea = self.arduino.readline().decode(errors="ignore").strip()
                print(f"📥 Línea recibida del Arduino: {linea}")
                if not self.running:
                    break
                if linea == "DETECCION_IR":
                    print("🟢 Sensor IR detectó algo")
                    self.deteccion.emit()
                    break


    def detener(self):
        self.running = False


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = MainApp()
    print("🔌 Aplicación ArdControl iniciada")
    window.show()
    sys.exit(app.exec_())