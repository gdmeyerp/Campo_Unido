import heapq
import math
from collections import defaultdict
from .models import Ubicacion, AreaServicio

class RutaOptima:
    """Clase para calcular rutas óptimas entre ubicaciones utilizando el algoritmo de Dijkstra"""
    
    @staticmethod
    def crear_grafo(ubicaciones):
        """
        Crea un grafo a partir de un conjunto de ubicaciones
        Cada ubicación es un nodo en el grafo y las aristas tienen peso igual a la distancia en km
        """
        grafo = defaultdict(list)
        
        # Crear una arista entre cada par de ubicaciones
        for i, ubicacion1 in enumerate(ubicaciones):
            for j, ubicacion2 in enumerate(ubicaciones):
                if i != j:  # Evitar bucles a sí mismo
                    lat1, lon1 = float(ubicacion1.latitud), float(ubicacion1.longitud)
                    lat2, lon2 = float(ubicacion2.latitud), float(ubicacion2.longitud)
                    
                    # Calcular distancia entre ubicaciones
                    distancia = AreaServicio.calcular_distancia(lat1, lon1, lat2, lon2)
                    
                    # Agregar arista al grafo
                    grafo[ubicacion1.id].append((ubicacion2.id, distancia))
        
        return grafo
    
    @staticmethod
    def dijkstra(grafo, inicio, fin):
        """
        Implementación del algoritmo de Dijkstra para encontrar el camino más corto
        
        Args:
            grafo: Un diccionario donde las claves son los IDs de las ubicaciones y 
                  los valores son listas de tuplas (ID destino, distancia)
            inicio: ID de la ubicación inicial
            fin: ID de la ubicación final
            
        Returns:
            Una tupla (distancia_total, camino) donde camino es una lista de IDs de ubicaciones
        """
        # Inicializar estructuras de datos
        distancias = {nodo: float('infinity') for nodo in grafo}
        distancias[inicio] = 0
        pq = [(0, inicio)]  # Cola de prioridad (distancia, nodo)
        previos = {nodo: None for nodo in grafo}
        visitados = set()
        
        while pq:
            # Obtener el nodo con menor distancia
            dist_actual, nodo_actual = heapq.heappop(pq)
            
            # Si ya llegamos al destino, reconstruir el camino y retornar
            if nodo_actual == fin:
                camino = []
                while nodo_actual:
                    camino.append(nodo_actual)
                    nodo_actual = previos[nodo_actual]
                camino.reverse()
                return dist_actual, camino
            
            # Si ya visitamos este nodo, continuar
            if nodo_actual in visitados:
                continue
                
            # Marcar como visitado
            visitados.add(nodo_actual)
            
            # Revisar vecinos
            if nodo_actual in grafo:
                for vecino, peso in grafo[nodo_actual]:
                    if vecino in visitados:
                        continue
                        
                    # Calcular nueva distancia
                    dist_nueva = dist_actual + peso
                    
                    # Si encontramos un camino más corto, actualizar
                    if dist_nueva < distancias[vecino]:
                        distancias[vecino] = dist_nueva
                        previos[vecino] = nodo_actual
                        heapq.heappush(pq, (dist_nueva, vecino))
        
        # Si no hay camino al destino
        return float('infinity'), []
    
    @classmethod
    def encontrar_ruta_optima(cls, origen_id, ubicaciones_ids):
        """
        Encuentra la ruta óptima para visitar todas las ubicaciones partiendo de un origen
        
        Args:
            origen_id: ID de la ubicación de origen
            ubicaciones_ids: Lista de IDs de ubicaciones a visitar
            
        Returns:
            Una tupla (distancia_total, ruta) donde ruta es una lista ordenada de objetos Ubicacion
        """
        # Obtener las ubicaciones
        ubicaciones = list(Ubicacion.objects.filter(id__in=[origen_id] + ubicaciones_ids))
        
        # Verificar que todas tengan coordenadas
        ubicaciones_validas = [u for u in ubicaciones if u.latitud is not None and u.longitud is not None]
        
        if len(ubicaciones_validas) < 2:
            return 0, ubicaciones_validas
            
        # Crear el grafo
        grafo = cls.crear_grafo(ubicaciones_validas)
        
        # Si solo hay 2 ubicaciones (origen y un destino)
        if len(ubicaciones_validas) == 2:
            destino_id = ubicaciones_validas[1].id if ubicaciones_validas[0].id == origen_id else ubicaciones_validas[0].id
            distancia, camino_ids = cls.dijkstra(grafo, origen_id, destino_id)
            
            # Mapear IDs a objetos Ubicacion
            id_a_ubicacion = {u.id: u for u in ubicaciones_validas}
            camino = [id_a_ubicacion[id] for id in camino_ids]
            
            return distancia, camino
            
        # Algoritmo para visitar múltiples ubicaciones (similar al problema del viajante)
        # Este es un problema NP-hard, por lo que usaremos una aproximación simple:
        # Encontrar siempre la ubicación más cercana a la actual
        
        distancia_total = 0
        ruta = [next(u for u in ubicaciones_validas if u.id == origen_id)]
        ubicaciones_restantes = [u for u in ubicaciones_validas if u.id != origen_id]
        
        while ubicaciones_restantes:
            actual = ruta[-1]
            mejor_distancia = float('infinity')
            mejor_ubicacion = None
            
            # Encontrar la ubicación más cercana a la actual
            for ubicacion in ubicaciones_restantes:
                lat1, lon1 = float(actual.latitud), float(actual.longitud)
                lat2, lon2 = float(ubicacion.latitud), float(ubicacion.longitud)
                
                distancia = AreaServicio.calcular_distancia(lat1, lon1, lat2, lon2)
                
                if distancia < mejor_distancia:
                    mejor_distancia = distancia
                    mejor_ubicacion = ubicacion
            
            # Añadir la mejor ubicación a la ruta
            if mejor_ubicacion:
                distancia_total += mejor_distancia
                ruta.append(mejor_ubicacion)
                ubicaciones_restantes.remove(mejor_ubicacion)
        
        return distancia_total, ruta
    
    @classmethod
    def obtener_instrucciones_ruta(cls, ruta):
        """
        Genera instrucciones en texto para seguir una ruta
        
        Args:
            ruta: Lista ordenada de objetos Ubicacion
            
        Returns:
            Lista de instrucciones en formato texto
        """
        if not ruta or len(ruta) < 2:
            return ["No hay suficientes ubicaciones para generar una ruta."]
            
        instrucciones = []
        instrucciones.append(f"Inicio: {ruta[0].nombre} ({ruta[0].direccion})")
        
        for i in range(1, len(ruta)):
            prev = ruta[i-1]
            curr = ruta[i]
            
            lat1, lon1 = float(prev.latitud), float(prev.longitud)
            lat2, lon2 = float(curr.latitud), float(curr.longitud)
            
            distancia = AreaServicio.calcular_distancia(lat1, lon1, lat2, lon2)
            
            # Calcular dirección aproximada (N, S, E, O, etc.)
            direccion = cls._calcular_direccion(lat1, lon1, lat2, lon2)
            
            instrucciones.append(
                f"De {prev.nombre} a {curr.nombre}: Viaje {direccion} por {distancia:.1f} km hasta {curr.direccion}"
            )
            
        instrucciones.append(f"Destino final: {ruta[-1].nombre} ({ruta[-1].direccion})")
        
        return instrucciones
    
    @staticmethod
    def _calcular_direccion(lat1, lon1, lat2, lon2):
        """Calcula la dirección cardinal aproximada entre dos puntos"""
        # Calcular diferencias en coordenadas
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        # Calcular el ángulo en radianes
        angulo = math.atan2(dlon, dlat)
        
        # Convertir a grados
        grados = math.degrees(angulo)
        
        # Ajustar para que esté en el rango [0, 360)
        grados = (grados + 360) % 360
        
        # Mapear a direcciones cardinales
        if 22.5 <= grados < 67.5:
            return "noreste"
        elif 67.5 <= grados < 112.5:
            return "este"
        elif 112.5 <= grados < 157.5:
            return "sureste"
        elif 157.5 <= grados < 202.5:
            return "sur"
        elif 202.5 <= grados < 247.5:
            return "suroeste"
        elif 247.5 <= grados < 292.5:
            return "oeste"
        elif 292.5 <= grados < 337.5:
            return "noroeste"
        else:  # between 337.5 and 22.5
            return "norte" 