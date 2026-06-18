# ------------------------------------------------------------
# SIMULADOR DE BOT - ALTA DE PROVEEDORES
# Organizacion Empresarial - TUPaD - UTN
# Empresa: DevSolutions S.R.L. (ficticia)
#
# El bot simula el proceso de alta de un proveedor nuevo.
# Funciona como una MAQUINA DE ESTADOS: en cada momento el bot
# esta en un solo estado y, segun lo que escribe el usuario,
# pasa (transiciona) al estado siguiente.
# ------------------------------------------------------------

import csv
import os
from datetime import date

# ------------------------------------------------------------
# CONFIGURACION (reglas de negocio)
# ------------------------------------------------------------

ARCHIVO = "proveedores.csv"          # base de datos simulada
UMBRAL_APROBACION = 500000           # si el monto anual supera esto, va a aprobacion

# Lista cerrada de rubros permitidos (el usuario elige por numero)
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

# Devuelve una lista con todos los CUIT que ya estan cargados
def cuits_registrados():
    lista = []
    # si el archivo no existe todavia, devolvemos lista vacia
    if not os.path.exists(ARCHIVO):
        return lista
    with open(ARCHIVO, newline="", encoding="utf-8") as f:
        lector = csv.DictReader(f)
        for fila in lector:
            lista.append(fila["cuit"])
    return lista

# Agrega un proveedor nuevo al final del archivo CSV
def guardar_proveedor(datos):
    existe = os.path.exists(ARCHIVO)
    with open(ARCHIVO, "a", newline="", encoding="utf-8") as f:
        campos = ["cuit", "razon_social", "rubro", "email",
                  "monto_estimado_anual", "estado", "fecha_alta"]
        escritor = csv.DictWriter(f, fieldnames=campos)
        # si el archivo no existia, primero escribimos el encabezado
        if not existe:
            escritor.writeheader()
        escritor.writerow(datos)

# ------------------------------------------------------------
# FUNCIONES DE VALIDACION (camino infeliz)
# ------------------------------------------------------------

# El CUIT es valido si tiene exactamente 11 numeros
def cuit_valido(texto):
    texto = texto.strip()
    if texto.isdigit() and len(texto) == 11:
        return True
    return False

# Validacion simple de email: tiene que tener un "@" y un "." despues
def email_valido(texto):
    texto = texto.strip()
    if "@" in texto and "." in texto.split("@")[-1]:
        return True
    return False

# El monto es valido si es un numero entero positivo
def monto_valido(texto):
    texto = texto.strip()
    if texto.isdigit() and int(texto) > 0:
        return True
    return False

# ------------------------------------------------------------
# PROGRAMA PRINCIPAL - MAQUINA DE ESTADOS
# ------------------------------------------------------------

def main():
    print("=" * 55)
    print(" BOT DE ALTA DE PROVEEDORES - DevSolutions S.R.L.")
    print("=" * 55)
    print("(escribi 'cancelar' en cualquier momento para salir)\n")

    # Aca vamos guardando los datos del proveedor que se esta cargando
    datos = {}

    # Estado inicial de la maquina
    estado = "PEDIR_CUIT"

    # El bot sigue funcionando hasta llegar a un estado de FIN
    while estado not in ("FIN_ALTA", "FIN_RECHAZO", "FIN_CANCELADO"):

        # ------ ESTADO: PEDIR CUIT ------
        if estado == "PEDIR_CUIT":
            entrada = input("Bot: Ingresa el CUIT del proveedor (11 numeros): ").strip()
            if entrada.lower() == "cancelar":
                estado = "FIN_CANCELADO"
            elif not cuit_valido(entrada):
                # CAMINO INFELIZ: el dato esta mal, no cambiamos de estado, repreguntamos
                print("Bot: El CUIT debe tener exactamente 11 numeros, sin puntos ni guiones. Probemos de nuevo.\n")
            elif entrada in cuits_registrados():
                # COMPUERTA 1 (rama duplicado)
                print("Bot: Ese CUIT ya esta registrado como proveedor. No se puede dar de alta dos veces.")
                estado = "FIN_RECHAZO"
            else:
                # COMPUERTA 1 (rama valido y nuevo) -> seguimos
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
            for numero in RUBROS:
                print("   " + numero + ") " + RUBROS[numero])
            entrada = input("Opcion: ").strip()
            if entrada.lower() == "cancelar":
                estado = "FIN_CANCELADO"
            elif entrada not in RUBROS:
                print("Bot: Tenes que elegir una opcion entre 1 y 5.\n")
            else:
                datos["rubro"] = RUBROS[entrada]
                estado = "PEDIR_EMAIL"

        # ------ ESTADO: PEDIR EMAIL ------
        elif estado == "PEDIR_EMAIL":
            entrada = input("Bot: Ingresa el email de contacto: ").strip()
            if entrada.lower() == "cancelar":
                estado = "FIN_CANCELADO"
            elif not email_valido(entrada):
                print("Bot: Ese email no parece valido (le falta @ o el dominio). Probemos de nuevo.\n")
            else:
                datos["email"] = entrada
                estado = "PEDIR_MONTO"

        # ------ ESTADO: PEDIR MONTO ------
        elif estado == "PEDIR_MONTO":
            entrada = input("Bot: Ingresa el monto estimado anual de contratacion (solo numeros): ").strip()
            if entrada.lower() == "cancelar":
                estado = "FIN_CANCELADO"
            elif not monto_valido(entrada):
                print("Bot: El monto tiene que ser un numero entero positivo (ej: 350000).\n")
            else:
                datos["monto_estimado_anual"] = "{:.2f}".format(int(entrada))
                estado = "EVALUAR_MONTO"

        # ------ ESTADO: EVALUAR MONTO (COMPUERTA 2) ------
        elif estado == "EVALUAR_MONTO":
            monto = float(datos["monto_estimado_anual"])
            if monto <= UMBRAL_APROBACION:
                # rama: alta automatica
                print("\nBot: El monto no supera el umbral de $" + str(UMBRAL_APROBACION) + ". Alta automatica.")
                datos["estado"] = "Activo"
                estado = "REGISTRAR"
            else:
                # rama: necesita aprobacion del responsable
                print("\nBot: El monto supera el umbral de $" + str(UMBRAL_APROBACION) + ". Derivo la solicitud al Responsable de Compras.")
                estado = "APROBACION"

        # ------ ESTADO: APROBACION (COMPUERTA 3) ------
        elif estado == "APROBACION":
            # En el simulador, el rol del Responsable de Compras lo respondemos por consola
            entrada = input("Responsable de Compras: aprobas el alta? (si / no): ").strip().lower()
            if entrada == "cancelar":
                estado = "FIN_CANCELADO"
            elif entrada == "si":
                datos["estado"] = "Activo"
                estado = "REGISTRAR"
            elif entrada == "no":
                datos["estado"] = "Rechazado"
                estado = "REGISTRAR"
            else:
                print("Bot: Respondé 'si' o 'no'.\n")

        # ------ ESTADO: REGISTRAR (tarea de servicio: guardar en la base) ------
        elif estado == "REGISTRAR":
            datos["fecha_alta"] = str(date.today())
            guardar_proveedor(datos)
            if datos["estado"] == "Activo":
                estado = "FIN_ALTA"
            else:
                estado = "FIN_RECHAZO"

    # ------------------------------------------------------------
    # ESTADOS FINALES (mensajes de cierre)
    # ------------------------------------------------------------
    print("\n" + "-" * 55)
    if estado == "FIN_ALTA":
        print("Bot: Proveedor dado de ALTA correctamente.")
        print("     Razon social: " + datos["razon_social"])
        print("     Estado: " + datos["estado"])
        print("     Quedo registrado en la base de datos.")
    elif estado == "FIN_RECHAZO":
        print("Bot: La solicitud fue RECHAZADA.")
        if "razon_social" in datos:
            print("     Quedo registrada como Rechazado para tener trazabilidad.")
    elif estado == "FIN_CANCELADO":
        print("Bot: Proceso cancelado por el usuario. No se guardo nada.")
    print("-" * 55)


# Esto hace que el programa arranque al ejecutar el archivo
if __name__ == "__main__":
    main()
