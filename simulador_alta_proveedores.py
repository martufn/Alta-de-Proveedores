# ------------------------------------------------------------
# SIMULADOR DE BOT - ALTA DE PROVEEDORES
# Organizacion Empresarial - TUPaD - UTN
# Empresa: DevSolutions S.R.L. (ficticia)
# ------------------------------------------------------------

import csv
import os
from datetime import date

# ------------------------------------------------------------
# CONFIGURACION (reglas de negocio)
# ------------------------------------------------------------

ARCHIVO = "proveedores.csv"          # base de datos simulada
UMBRAL_APROBACION = 500000           # si el monto anual supera esto, va a aprobacion

# Lista cerrada de rubros permitidos
RUBROS = {
    "1": "Hardware",
    "2": "Software/Licencias",
    "3": "Cloud",
    "4": "Consultoria",
    "5": "Insumos de oficina"
}

# ------------------------------------------------------------
# FUNCIONES DE LA BASE DE DATOS (persistencia)
# ------------------------------------------------------------

def cuits_registrados():
    # Devuelve una lista con todos los CUIT que ya estan cargados
    lista = []
    if not os.path.exists(ARCHIVO):
        return lista
    try:
        with open(ARCHIVO, newline="", encoding="utf-8") as f:
            lector = csv.DictReader(f)
            # Solo leemos si el archivo tiene datos y existe la columna 'cuit'
            if lector.fieldnames and "cuit" in lector.fieldnames:
                for fila in lector:
                    if fila.get("cuit"):
                        lista.append(fila["cuit"].strip())
    except OSError:
        # Si hay un error al leer el archivo, devolvemos lo que tengamos
        pass
    return lista


def guardar_proveedor(datos):
    # Agrega un proveedor nuevo al final del archivo CSV
    existe = os.path.exists(ARCHIVO)
    with open(ARCHIVO, "a", newline="", encoding="utf-8") as f:
        campos = ["cuit", "razon_social", "rubro", "email",
                  "monto_estimado_anual", "estado", "fecha_alta"]
        escritor = csv.DictWriter(f, fieldnames=campos)
        if not existe:
            escritor.writeheader()
        escritor.writerow(datos)


# ------------------------------------------------------------
# FUNCIONES DE VALIDACION (camino infeliz controlado)
# ------------------------------------------------------------

def cuit_valido(texto):
    # El CUIT es valido si son 11 digitos numericos
    texto = texto.strip()
    return texto.isdigit() and len(texto) == 11


def email_valido(texto):
    # El email es valido si tiene un @ y un punto en el dominio
    texto = texto.strip()
    if "@" not in texto:
        return False
    partes = texto.split("@")
    if len(partes) != 2:
        return False
    if "." not in partes[1]:
        return False
    return True


def monto_valido(texto):
    # El monto es valido si es un numero entero positivo
    texto = texto.strip()
    return texto.isdigit() and int(texto) > 0


# ------------------------------------------------------------
# PROGRAMA PRINCIPAL - MAQUINA DE ESTADOS
# ------------------------------------------------------------

def main():
    print("=" * 55)
    print(" BOT DE ALTA DE PROVEEDORES - DevSolutions S.R.L.")
    print("=" * 55)
    print("(escribi 'cancelar' en cualquier momento para salir)\n")

    datos = {}
    estado = "PEDIR_CUIT"

    while estado not in ("FIN_ALTA", "FIN_RECHAZO", "FIN_CANCELADO"):

        # ------ ESTADO: PEDIR CUIT ------
        if estado == "PEDIR_CUIT":
            entrada = input("Bot: Ingresa el CUIT del proveedor (11 numeros): ").strip()
            if entrada.lower() == "cancelar":
                estado = "FIN_CANCELADO"
            elif not cuit_valido(entrada):
                print("Bot: CUIT invalido. Tienen que ser 11 digitos numericos.\n")
            elif entrada in cuits_registrados():
                print("Bot: Ese CUIT ya esta registrado. No se permiten duplicados.")
                estado = "FIN_RECHAZO"
            else:
                datos["cuit"] = entrada
                estado = "PEDIR_RAZON"

        # ------ ESTADO: PEDIR RAZON SOCIAL ------
        elif estado == "PEDIR_RAZON":
            entrada = input("Bot: Ingresa la razon social (nombre de la empresa): ").strip()
            if entrada.lower() == "cancelar":
                estado = "FIN_CANCELADO"
            elif entrada == "":
                print("Bot: La razon social no puede quedar vacia.\n")
            else:
                datos["razon_social"] = entrada
                estado = "PEDIR_RUBRO"

        # ------ ESTADO: PEDIR RUBRO ------
        elif estado == "PEDIR_RUBRO":
            print("Bot: Elegi el rubro del proveedor:")
            for numero, nombre in RUBROS.items():
                print(f"   {numero}) {nombre}")
            entrada = input("Opcion: ").strip()
            if entrada.lower() == "cancelar":
                estado = "FIN_CANCELADO"
            elif entrada not in RUBROS:
                print("Bot: Seleccion invalida. Elegi un numero del 1 al 5.\n")
            else:
                datos["rubro"] = RUBROS[entrada]
                estado = "PEDIR_EMAIL"

        # ------ ESTADO: PEDIR EMAIL ------
        elif estado == "PEDIR_EMAIL":
            entrada = input("Bot: Ingresa el email de contacto: ").strip()
            if entrada.lower() == "cancelar":
                estado = "FIN_CANCELADO"
            elif not email_valido(entrada):
                print("Bot: Formato de email incorrecto. Acordate de incluir el '@' y un dominio valido.\n")
            else:
                datos["email"] = entrada
                estado = "PEDIR_MONTO"

        # ------ ESTADO: PEDIR MONTO ------
        elif estado == "PEDIR_MONTO":
            entrada = input("Bot: Ingresa el monto estimado anual de contratacion (solo numeros): ").strip()
            if entrada.lower() == "cancelar":
                estado = "FIN_CANCELADO"
            elif not monto_valido(entrada):
                print("Bot: El monto tiene que ser un numero entero positivo, sin puntos ni comas.\n")
            else:
                # Guardamos el entero para poder compararlo en la evaluacion
                datos["monto_estimado_anual"] = int(entrada)
                estado = "EVALUAR_MONTO"

        # ------ ESTADO: EVALUAR MONTO (COMPUERTA XOR 2) ------
        elif estado == "EVALUAR_MONTO":
            monto = datos["monto_estimado_anual"]
            if monto <= UMBRAL_APROBACION:
                print(f"\nBot: El monto (${monto}) no supera el umbral de ${UMBRAL_APROBACION}. Alta automatica.")
                datos["estado"] = "Activo"
                estado = "REGISTRAR"
            else:
                print(f"\nBot: El monto (${monto}) supera el umbral de ${UMBRAL_APROBACION}. Requiere autorizacion.")
                estado = "APROBACION"

        # ------ ESTADO: APROBACION (COMPUERTA XOR 3) ------
        elif estado == "APROBACION":
            entrada = input("Responsable de Compras: ¿Aprobas el alta? (si / no): ").strip().lower()
            if entrada == "cancelar":
                estado = "FIN_CANCELADO"
            elif entrada == "si":
                datos["estado"] = "Activo"
                estado = "REGISTRAR"
            elif entrada == "no":
                datos["estado"] = "Rechazado"
                estado = "REGISTRAR"
            else:
                print("Bot: Por favor, responde 'si' o 'no'.\n")

        # ------ ESTADO: REGISTRAR (guardado definitivo) ------
        elif estado == "REGISTRAR":
            datos["fecha_alta"] = str(date.today())
            # Formateamos el monto a string con dos decimales recien al guardar
            datos["monto_estimado_anual"] = "{:.2f}".format(datos["monto_estimado_anual"])
            guardar_proveedor(datos)
            if datos["estado"] == "Activo":
                estado = "FIN_ALTA"
            else:
                estado = "FIN_RECHAZO"

    # ------------------------------------------------------------
    # ESTADOS FINALES (mensajes en consola)
    # ------------------------------------------------------------
    print("\n" + "-" * 55)
    if estado == "FIN_ALTA":
        print("Bot: ¡Proveedor dado de ALTA correctamente!")
        print(f"     Razon social: {datos['razon_social']}")
        print(f"     Estado: {datos['estado']}")
        print("     Registro guardado en el archivo CSV.")
    elif estado == "FIN_RECHAZO":
        print("Bot: La solicitud fue RECHAZADA.")
        if "razon_social" in datos:
            print(f"     La empresa '{datos['razon_social']}' quedo asentada como Rechazada.")
    elif estado == "FIN_CANCELADO":
        print("Bot: Proceso cancelado por el usuario. No se efectuaron cambios.")
    print("-" * 55)


if __name__ == "__main__":
    main()
