from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="AlumiPromo - Vidrios y Aluminios")

# ==========================================
# 1. CLASES DEL SISTEMA (Paradigma OO)
# ==========================================

class Cliente:
    def __init__(self, nombre: str, telefono: str, categoria: str):
        # Regla de Fiabilidad (Ficha 3): validar 10 dígitos numéricos
        if not telefono.isdigit() or len(telefono) != 10:
            raise ValueError("El teléfono debe tener exactamente 10 dígitos numéricos.")
        self.nombre = nombre
        self.telefono = telefono
        self.categoria = categoria.lower().strip()

class Promocion:
    def __init__(self, titulo: str, descuento: int, categoria_objetivo: str):
        self.titulo = titulo
        self.descuento = descuento
        self.categoria_objetivo = categoria_objetivo.lower().strip()

class MensajePromocional:
    @staticmethod
    def generar(cliente: Cliente, promo: Promocion) -> dict:
        texto = (
            f"¡Hola {cliente.nombre}! En Vidrios y Aluminios tenemos '{promo.titulo}': "
            f"{promo.descuento}% de descuento en {promo.categoria_objetivo}. ¡Escríbenos!"
        )
        return {
            "cliente": cliente.nombre,
            "telefono": cliente.telefono,
            "mensaje_listo": texto
        }

class AgendaClientes:
    def __init__(self):
        # Contactos precargados en memoria para probar de inmediato
        self.clientes: List[Cliente] = [
            Cliente("Juan Pérez", "3009876543", "ventanas de aluminio"),
            Cliente("María López", "3112345678", "canceles de baño"),
        ]

    def agregar(self, cliente: Cliente):
        self.clientes.append(cliente)

    def filtrar_por_categoria(self, categoria: Optional[str] = None) -> List[Cliente]:
        if not categoria:
            return self.clientes
        busqueda = categoria.lower().strip()
        return [c for c in self.clientes if busqueda in c.categoria]

agenda = AgendaClientes()

# ==========================================
# 2. MODELOS DE DATOS PARA FASTAPI
# ==========================================

class ClienteEntrada(BaseModel):
    nombre: str
    telefono: str
    categoria: str

class PromocionEntrada(BaseModel):
    titulo: str
    descuento: int
    categoria_objetivo: str

# ==========================================
# 3. RUTAS (ENDPOINTS) DEL PROTOTIPO
# ==========================================

@app.post("/clientes", summary="Guardar un nuevo contacto")
def registrar_cliente(datos: ClienteEntrada):
    try:
        nuevo = Cliente(datos.nombre, datos.telefono, datos.categoria)
        agenda.agregar(nuevo)
        return {"estado": "Guardado", "cliente": vars(nuevo)}
    except ValueError as error:
        # Bloquea datos erróneos sin que el sistema se cierre
        raise HTTPException(status_code=400, detail=str(error))

@app.get("/clientes", summary="Ver todos o filtrar por categoría")
def listar_clientes(categoria: Optional[str] = None):
    encontrados = agenda.filtrar_por_categoria(categoria)
    return {
        "total": len(encontrados),
        "clientes": [vars(c) for c in encontrados]
    }

@app.post("/generar-mensajes", summary="Filtrar y armar mensajes promocionales")
def generar_campana(datos: PromocionEntrada):
    promo = Promocion(datos.titulo, datos.descuento, datos.categoria_objetivo)
    filtrados = agenda.filtrar_por_categoria(promo.categoria_objetivo)
    mensajes = [MensajePromocional.generar(c, promo) for c in filtrados]
    return {
        "promocion": promo.titulo,
        "total_destinatarios": len(mensajes),
        "resultados": mensajes
    }