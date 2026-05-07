from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError, ConnectionFailure
from bson.objectid import ObjectId
from datetime import datetime, timedelta
from typing import Optional, List, Dict

class GestorTareas:
    def __init__(self, uri: str = 'mongodb://127.0.0.1:27017/'):
        """Inicializar conexión a MongoDB usando la base de datos específica"""
        try:
            self.cliente = MongoClient(uri, serverSelectionTimeoutMS=5000)
            self.cliente.admin.command('ping')
            
            # Mantenemos el nombre de la base de datos original para la sesión
            self.db = self.cliente['24308060610016']
            self.usuarios = self.db['usuarios']
            self.tareas = self.db['tareas']
            
            # Crear índices necesarios
            self._crear_indices()
            print("✅ Conectado a MongoDB - BD: 24308060610016")
        except ConnectionFailure:
            print("❌ Error: No se pudo conectar a MongoDB")
            raise

    def _crear_indices(self):
        """Crear índices para mejorar rendimiento"""
        self.usuarios.create_index("email", unique=True)
        self.tareas.create_index([("usuario_id", 1), ("fecha_creacion", -1)])
        self.tareas.create_index("estado")

    # --- MÉTODOS DE SESIÓN (SIN CAMBIOS EN LÓGICA) ---
    def crear_usuario(self, user, email, secreto):
        """Crear usuario respetando los campos originales: user, email, secreto"""
        try:
            self.usuarios.insert_one({
                "user": user,
                "email": email,
                "secreto": secreto,
                "fecha_registro": datetime.now()
            })
            return True
        except Exception as e:
            print(f"❌ Error al crear: {e}")
            return False

    def obtener_usuario_por_email(self, email):
        """Obtener usuario por email para el login"""
        return self.usuarios.find_one({"email": email})

    def obtener_usuario(self, usuario_id: str) -> Optional[Dict]:
        """Obtener usuario por ID (necesario para validación de tareas)"""
        try:
            usuario = self.usuarios.find_one({"_id": ObjectId(usuario_id)})
            if usuario:
                usuario['_id'] = str(usuario['_id'])
            return usuario
        except Exception:
            return None

    # --- MÉTODOS DE TAREAS ---
    def crear_tarea(self, usuario_id: str, titulo: str, fecha_calendario: str, descripcion: str = "") -> Optional[str]:
        """Crear tarea vinculada a usuario_id y a la fecha_display del calendario"""
        if not self.obtener_usuario(usuario_id):
            print(f"❌ Error: Usuario {usuario_id} no existe")
            return None
        
        tarea = {
            "usuario_id": ObjectId(usuario_id),
            "titulo": titulo,
            "descripcion": descripcion,
            "fecha_display": fecha_calendario, # Campo clave para el filtro por día
            "estado": "pendiente",
            "fecha_creacion": datetime.now(),
            "fecha_limite": datetime.now() + timedelta(days=7),
            "completada": False,
            "etiquetas": []
        }
        
        resultado = self.tareas.insert_one(tarea)
        return str(resultado.inserted_id)

    def obtener_tareas_usuario(self, usuario_id: str, estado: Optional[str] = None) -> List[Dict]:
        """Obtener tareas filtradas por usuario y opcionalmente por estado"""
        filtro = {"usuario_id": ObjectId(usuario_id)}
        if estado:
            filtro["estado"] = estado
        
        tareas = self.tareas.find(filtro).sort("fecha_creacion", -1)
        resultado = []
        for t in tareas:
            t['_id'] = str(t['_id'])
            t['usuario_id'] = str(t['usuario_id'])
            resultado.append(t)
        return resultado

    def actualizar_estado_tarea(self, tarea_id: str, nuevo_estado: str) -> bool:
        """Actualizar el estado (pendiente, en proceso, terminado)"""
        estados_validos = ["pendiente", "en proceso", "terminado", "cancelada"]
        if nuevo_estado not in estados_validos:
            return False
        
        resultado = self.tareas.update_one(
            {"_id": ObjectId(tarea_id)},
            {
                "$set": {
                    "estado": nuevo_estado,
                    "completada": nuevo_estado == "terminado",
                    "fecha_actualizacion": datetime.now()
                }
            }
        )
        return resultado.modified_count > 0

    def eliminar_tarea(self, tarea_id: str) -> bool:
        """Eliminar una tarea físicamente de la BD"""
        resultado = self.tareas.delete_one({"_id": ObjectId(tarea_id)})
        return resultado.deleted_count > 0

    def estadisticas_usuario(self, usuario_id: str) -> Dict:
        """Obtener estadísticas agregadas por usuario"""
        pipeline = [
            {"$match": {"usuario_id": ObjectId(usuario_id)}},
            {"$group": {
                "_id": "$estado",
                "cantidad": {"$sum": 1},
                "fecha_ultima": {"$max": "$fecha_creacion"}
            }},
            {"$sort": {"_id": 1}}
        ]
        
        resultados = list(self.tareas.aggregate(pipeline))
        estadisticas = {"total": 0, "por_estado": {}, "ultima_actividad": None}
        
        for r in resultados:
            estado = r['_id']
            cantidad = r['cantidad']
            estadisticas["por_estado"][estado] = cantidad
            estadisticas["total"] += cantidad
            if not estadisticas["ultima_actividad"] or r['fecha_ultima'] > estadisticas["ultima_actividad"]:
                estadisticas["ultima_actividad"] = r['fecha_ultima']
        
        return estadisticas

    def cerrar_conexion(self):
        """Cerrar conexión a MongoDB"""
        if self.cliente:
            self.cliente.close()
            print("🔌 Conexión cerrada")
    