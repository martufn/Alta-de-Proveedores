# ------------------------------------------------------------
# SIMULADOR DE BOT - ALTA DE PROVEEDORES
# Organizacion Empresarial - TUPaD - UTN
# Empresa: DevSolutions S.R.L. (ficticia)
#
# El programa simula un bot que da de alta proveedores siguiendo el circuito del diagrama BPMN: pide datos, valida, evalua el monto
# y registra el resultado en un archivo CSV.
# ------------------------------------------------------------

import csv                    # libreria para leer y escribir archivos CSV
from datetime import date     # para obtener la fecha de hoy (fecha de alta)
from pathlib import Path      # para manejar la ruta del archivo de forma moderna

# ------------------------------------------------------------
# CONFIGURACION (reglas de negocio)
# Todo lo que podria cambiar lo dejamos junto y arriba, asi se modifica en un solo lugar sin tocar el resto del codigo.
# ------------------------------------------------------------

ARCHIVO = Path("proveedores.csv")     # archivo que hace de base de datos
UMBRAL_APROBACION = 500000            # si el monto anual supera esto, va a aprobacion
OPCION_CANCELAR = "cancelar"          # palabra que escribe el usuario para salir

# Nombres de las columnas del CSV, en el orden en que se van a guardar
CAMPOS_CSV = [
    "cuit",
    "razon_social",
    "rubro",
    "email",
    "monto_estimado_anual",
    "estado",
    "fecha_alta",
]

# Rubros disponibles. La clave (ej: 1) es lo que escribe el usuario y el valor (ej: Hardware) es lo que se guarda en el CSV.
RUBROS = {
    "1": "Hardware",
    "2": "Software/Licencias",
    "3": "Cloud",
    "4": "Consultoria",
    "5": "Insumos de oficina",
}

# Estados donde el proceso termina. Cuando la maquina de estados llega a uno de estos, el bucle principal se detiene.
ESTADOS_FINALES = {"FIN_ALTA", "FIN_RECHAZO", "FIN_CANCELADO"}


# ------------------------------------------------------------
# FUNCIONES AUXILIARES
# ------------------------------------------------------------

def es_cancelacion(texto):
    """Indica si el usuario pidio cancelar el proceso."""
    # .strip() saca espacios y .lower() pasa a minuscula
    return texto.strip().lower() == OPCION_CANCELAR


def pedir_texto(mensaje):
    """Centraliza el ingreso de datos para evitar repetir input().strip()."""
    # Pide el dato y le saca los espacios de los costados de una vez.
    return input(mensaje).strip()


# ------------------------------------------------------------
# FUNCIONES DE LA BASE DE DATOS (persistencia)
# ------------------------------------------------------------

def cuits_registrados():
    """Devuelve un conjunto (set) con todos los CUIT ya cargados."""
    # Si el archivo todavia no existe, no hay CUIT cargados: set vacio.
    if not ARCHIVO.exists():
        return set()

    try:
        # Abrimos el CSV solo para leer.
        with ARCHIVO.open(newline="", encoding="utf-8") as archivo:
            lector = csv.DictReader(archivo)   # lee cada fila como diccionario

            # Si el archivo esta vacio o no tiene la columna "cuit",
            # devolvemos un set vacio para no romper el programa.
            if not lector.fieldnames or "cuit" not in lector.fieldnames:
                return set()

            # Recorremos todas las filas y armamos un set con los CUIT.
            # Usamos un set (no una lista) porque buscar dentro de un set es casi instantaneo, ideal para chequear duplicados despues.
            return {
                fila["cuit"].strip()
                for fila in lector
                if fila.get("cuit")
            }

    except OSError:
        # Si por algun motivo no se puede leer el archivo, evitamos que el programa se caiga y seguimos con un set vacio.
        return set()


def guardar_proveedor(datos):
    """Agrega un proveedor nuevo al final del archivo CSV."""
    # Guardamos si el archivo ya existia antes de abrirlo.
    archivo_existe = ARCHIVO.exists()

    # Se agrega al final sin borrar lo que ya habia.
    with ARCHIVO.open("a", newline="", encoding="utf-8") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=CAMPOS_CSV)

        # Si el archivo es nuevo, primero escribimos la fila de titulos.
        if not archivo_existe:
            escritor.writeheader()

        # Escribimos la fila con los datos del proveedor.
        escritor.writerow(datos)


# ------------------------------------------------------------
# FUNCIONES DE VALIDACION
# Cada una devuelve True (dato correcto) o False (dato incorrecto).
# ------------------------------------------------------------

def cuit_valido(texto):
    """El CUIT es valido si contiene exactamente 11 digitos numericos."""
    texto = texto.strip()
    # .isdigit(): que sean solo numeros; len == 11: que sean 11.
    return texto.isdigit() and len(texto) == 11


def email_valido(texto):
    """Valida un email simple: un solo @ y un punto en el dominio."""
    texto = texto.strip()
    # partition("@") parte el texto en tres pedazos usando el "@":
    #   "ana@mail.com": usuario="ana", separador="@", dominio="mail.com"
    # Si no hay "@", el separador queda vacio.
    usuario, separador, dominio = texto.partition("@")

    # El email es valido si: hubo un "@", hay algo antes y despues de el, y el dominio tiene al menos un punto (ej: .com).
    return (
        separador == "@"
        and usuario != ""
        and dominio != ""
        and "." in dominio
    )


def monto_valido(texto):
    """El monto es valido si es un numero entero positivo."""
    texto = texto.strip()
    # Tiene que ser solo numeros y mayor a cero.
    return texto.isdigit() and int(texto) > 0


# ------------------------------------------------------------
# FUNCIONES DE CADA PASO DEL PROCESO
# Cada funcion pide un dato, lo valida y devuelve el siguiente estado
# al que tiene que ir la maquina de estados.
# ------------------------------------------------------------

def pedir_cuit(datos, cuits_existentes):
    entrada = pedir_texto("Bot: Ingresa el CUIT del proveedor (11 numeros): ")

    # En cualquier paso el usuario puede escribir cancelar.
    if es_cancelacion(entrada):
        return "FIN_CANCELADO"

    # Si el formato esta mal, avisamos y volvemos a pedir el CUIT.
    if not cuit_valido(entrada):
        print("Bot: CUIT invalido. Tienen que ser 11 digitos numericos.\n")
        return "PEDIR_CUIT"

    # Si el CUIT ya estaba cargado, rechazamos (no se permiten duplicados).
    if entrada in cuits_existentes:
        print("Bot: Ese CUIT ya esta registrado. No se permiten duplicados.")
        return "FIN_RECHAZO"

    # Dato correcto: lo guardamos y avanzamos al siguiente paso.
    datos["cuit"] = entrada
    return "PEDIR_RAZON"


def pedir_razon_social(datos):
    entrada = pedir_texto("Bot: Ingresa la razon social (nombre de la empresa): ")

    if es_cancelacion(entrada):
        return "FIN_CANCELADO"

    # La razon social no puede quedar vacia.
    if entrada == "":
        print("Bot: La razon social no puede quedar vacia.\n")
        return "PEDIR_RAZON"

    datos["razon_social"] = entrada
    return "PEDIR_RUBRO"


def pedir_rubro(datos):
    # Mostramos el menu de rubros recorriendo el diccionario RUBROS.
    print("Bot: Elegi el rubro del proveedor:")
    for numero, nombre in RUBROS.items():
        print(f"   {numero}) {nombre}")

    entrada = pedir_texto("Opcion: ")

    if es_cancelacion(entrada):
        return "FIN_CANCELADO"

    # La opcion es valida solo si es una de las claves del diccionario.
    if entrada not in RUBROS:
        print("Bot: Seleccion invalida. Elegi un numero del 1 al 5.\n")
        return "PEDIR_RUBRO"

    # Guardamos el nombre del rubro (no el numero) usando la clave elegida.
    datos["rubro"] = RUBROS[entrada]
    return "PEDIR_EMAIL"


def pedir_email(datos):
    entrada = pedir_texto("Bot: Ingresa el email de contacto: ")

    if es_cancelacion(entrada):
        return "FIN_CANCELADO"

    if not email_valido(entrada):
        print("Bot: Formato de email incorrecto. Acordate de incluir el '@' y un dominio valido.\n")
        return "PEDIR_EMAIL"

    datos["email"] = entrada
    return "PEDIR_MONTO"


def pedir_monto(datos):
    entrada = pedir_texto("Bot: Ingresa el monto estimado anual de contratacion (solo numeros): ")

    if es_cancelacion(entrada):
        return "FIN_CANCELADO"

    if not monto_valido(entrada):
        print("Bot: El monto tiene que ser un numero entero positivo, sin puntos ni comas.\n")
        return "PEDIR_MONTO"

    # Lo guardamos como numero entero (int) para poder compararlo despues.
    datos["monto_estimado_anual"] = int(entrada)
    return "EVALUAR_MONTO"


def evaluar_monto(datos):
    monto = datos["monto_estimado_anual"]

    # Si el monto no supera el umbral, el alta es automatica.
    if monto <= UMBRAL_APROBACION:
        print(f"\nBot: El monto (${monto}) no supera el umbral de ${UMBRAL_APROBACION}. Alta automatica.")
        datos["estado"] = "Activo"
        return "REGISTRAR"

    # Si supera el umbral, necesita la autorizacion del Responsable de Compras.
    print(f"\nBot: El monto (${monto}) supera el umbral de ${UMBRAL_APROBACION}. Requiere autorizacion.")
    return "APROBACION"


def pedir_aprobacion(datos):
    entrada = pedir_texto("Responsable de Compras: ¿Aprobas el alta? (si / no): ").lower()

    if entrada == OPCION_CANCELAR:
        return "FIN_CANCELADO"

    # Si aprueba: proveedor Activo.
    if entrada == "si":
        datos["estado"] = "Activo"
        return "REGISTRAR"

    # Si no aprueba: proveedor Rechazado (igual se deja asentado en el CSV).
    if entrada == "no":
        datos["estado"] = "Rechazado"
        return "REGISTRAR"

    # Cualquier otra respuesta: volvemos a preguntar.
    print("Bot: Por favor, responde 'si' o 'no'.\n")
    return "APROBACION"


def registrar_proveedor(datos):
    # Completamos los ultimos datos antes de guardar.
    datos["fecha_alta"] = str(date.today())              # fecha de hoy como texto
    # Guardamos el monto como numero entero (sin decimales): 100000 -> "100000"
    datos["monto_estimado_anual"] = str(datos["monto_estimado_anual"])

    # Escribimos el proveedor en el archivo CSV.
    guardar_proveedor(datos)

    # El estado final depende de si quedo Activo o Rechazado.
    if datos["estado"] == "Activo":
        return "FIN_ALTA"

    return "FIN_RECHAZO"


def mostrar_resultado_final(estado, datos):
    """Muestra un mensaje distinto segun como termino el proceso."""
    print("\n" + "-" * 55)

    if estado == "FIN_ALTA":
        print("Bot: ¡Proveedor dado de ALTA correctamente!")
        print(f"     Razon social: {datos['razon_social']}")
        print(f"     Estado: {datos['estado']}")
        print("     Registro guardado en el archivo CSV.")

    elif estado == "FIN_RECHAZO":
        print("Bot: La solicitud fue RECHAZADA.")
        # Puede ser un rechazo por duplicado (sin razon social todavia) o un rechazo del Responsable de Compras (con razon social).
        if "razon_social" in datos:
            print(f"     La empresa '{datos['razon_social']}' quedo asentada como Rechazada.")

    elif estado == "FIN_CANCELADO":
        print("Bot: Proceso cancelado por el usuario. No se efectuaron cambios.")

    print("-" * 55)


# ------------------------------------------------------------
# PROGRAMA PRINCIPAL - MAQUINA DE ESTADOS
# ------------------------------------------------------------

def main():
    # Encabezado de bienvenida.
    print("=" * 55)
    print(" BOT DE ALTA DE PROVEEDORES - DevSolutions S.R.L.")
    print("=" * 55)
    print("(escribi 'cancelar' en cualquier momento para salir)\n")

    datos = {}                              # aca se van guardando los datos del proveedor
    estado = "PEDIR_CUIT"                   # estado inicial de la maquina de estados
    cuits_existentes = cuits_registrados()  # se leen los CUIT ya cargados una sola vez

    # Maquina de estados:
    # El bucle se repite mientras el estado actual no sea un estado final.
    # Segun el estado actual, se llama a la funcion del paso correspondiente.
    # Cada funcion hace su tarea y devuelve el siguiente estado.
    while estado not in ESTADOS_FINALES:
        if estado == "PEDIR_CUIT":
            estado = pedir_cuit(datos, cuits_existentes)
        elif estado == "PEDIR_RAZON":
            estado = pedir_razon_social(datos)
        elif estado == "PEDIR_RUBRO":
            estado = pedir_rubro(datos)
        elif estado == "PEDIR_EMAIL":
            estado = pedir_email(datos)
        elif estado == "PEDIR_MONTO":
            estado = pedir_monto(datos)
        elif estado == "EVALUAR_MONTO":
            estado = evaluar_monto(datos)
        elif estado == "APROBACION":
            estado = pedir_aprobacion(datos)
        elif estado == "REGISTRAR":
            estado = registrar_proveedor(datos)

    # Al salir del bucle, el estado es uno final: se muestra el resultado.
    mostrar_resultado_final(estado, datos)


# Esto hace que main() se ejecute solo si corremos este archivo directamente.
if __name__ == "__main__":
    main()
