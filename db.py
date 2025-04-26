import mysql.connector
import datetime
from datetime import datetime

class DBManager:
    def __init__(self):
        self.conn = None
        try:
            self.conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="312614",
                database="sistema_vision",
                connection_timeout=3  # ⏱️ Esto evita que se quede colgado
            )
            self.cursor = self.conn.cursor()
            print("✅ Conectado a la base de datos")
        except mysql.connector.Error as e:
            print("❌ Error al conectar a la base de datos:", e)

    def obtener_lotes(self):
        """Devuelve una lista de lotes únicos desde la tabla 'piezas'"""
        lotes = []
        if self.conn:
            try:
                cursor = self.conn.cursor()
                cursor.execute("SELECT DISTINCT lote FROM registro_piezas")
                lotes = [str(row[0]) for row in cursor.fetchall()]
                cursor.close()
            except mysql.connector.Error as e:
                print("❌ Error al consultar lotes:", e)
        else:
            print("⚠️ No hay conexión a la base de datos.")
        return lotes
    
    def obtener_validos_y_no_validos_por_lote(self, lote_actual):
        query = """
            SELECT 
            SUM(CASE WHEN valido = 1 THEN 1 ELSE 0 END) AS total_validos,
            SUM(CASE WHEN valido = 0 THEN 1 ELSE 0 END) AS total_no_validos
        FROM registro_piezas
        WHERE lote = %s
        """
        cursor = self.conn.cursor()
        cursor.execute(query, (lote_actual,))
        resultado = cursor.fetchone()
        cursor.close()
        return resultado
    
    def insertar_objeto(self, ancho, largo, valido, fecha, lote):
        """Inserta un nuevo objeto en la base de datos"""
        query = "INSERT INTO registro_piezas (ancho, largo, valido, fecha,lote) VALUES (%s, %s, %s, %s, %s)"
        valores = (ancho, largo, valido, fecha, lote)
        self.cursor.execute(query, valores)
        self.conn.commit()
        print("✅ Objeto insertado en la base de datos")
    
    def cerrar_conexion(self):
        if self.conn:
            self.conn.close()