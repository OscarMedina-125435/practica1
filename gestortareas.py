from pymongo import MongoClient
from datetime import datetime

class GestorTareas:
    def __init__(self, uri="mongodb://localhost:27017/"):
        self.cliente = MongoClient(uri, serverSelectionTimeoutMS=2000)
        self.db = self.cliente['mi_nueva_app']
        self.usuarios = self.db['usuarios']

        self.usuarios.create_index("email", unique=True)

    def crear_usuario(self, user, email, secreto):
        try:
            self.usuarios.insert_one({
                "user": user,
                "email": email,
                "secreto": secreto,
                "fecha_registro": datetime.now()
            })
            return True
        except Exception as e:
            print(f"Error al crear: {e}")
            return False

    def obtener_usuario_por_email(self, email):
        return self.usuarios.find_one({"email": email})