import mysql.connector

class DBManager:
    def __init__(self):
        self.conn = None
        try:
            self.conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="312614",
                database="gestion_piezas",
                connection_timeout=3  # ⏱️ Esto evita que se quede colgado
            )
            print("✅ Conectado a la base de datos")
        except mysql.connector.Error as e:
            print("❌ Error al conectar a la base de datos:", e)

    def obtener_lotes(self):
        """Devuelve una lista de lotes únicos desde la tabla 'piezas'"""
        lotes = []
        if self.conn:
            try:
                cursor = self.conn.cursor()
                cursor.execute("SELECT DISTINCT numero_lote FROM piezas")
                lotes = [str(row[0]) for row in cursor.fetchall()]
                cursor.close()
            except mysql.connector.Error as e:
                print("❌ Error al consultar lotes:", e)
        else:
            print("⚠️ No hay conexión a la base de datos.")
        return lotes

    def cerrar_conexion(self):
        if self.conn:
            self.conn.close()
