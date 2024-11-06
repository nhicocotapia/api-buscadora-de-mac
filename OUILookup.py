#Maximiliano Rozas Rifo
#Nicolás Tapia Gallardo

import sys
import getopt
import requests
import subprocess

def programa_principal(argumentos):
    mac_a_buscar = None
    mostrar_arp = False

    try:
        opciones, extra_args = getopt.getopt(argumentos, "hm:a", ["ayuda", "mac=", "arp"])
    except getopt.GetoptError:
        mostrar_ayuda()
        sys.exit(2)

    for opt, arg in opciones:
        if opt in ("-h", "--ayuda"):
            mostrar_ayuda()
            sys.exit()
        elif opt in ("-m", "--mac"):
            mac_a_buscar = arg
        elif opt in ("-a", "--arp"):
            mostrar_arp = True

    if mac_a_buscar:
        buscar_mac(mac_a_buscar)
    elif mostrar_arp:
        mostrar_tabla_arp()
    else:
        mostrar_ayuda()

def mostrar_ayuda():
    print("Uso: OUILookup.py --mac <mac> | --arp | [--ayuda]")
    print(" --mac: Dirección MAC a consultar. Ejemplo: aa:bb:cc:00:00:00")
    print(" --arp: Muestra los fabricantes de los primeros 10 dispositivos en la tabla ARP.")
    print(" --ayuda: Muestra este mensaje y termina.")

def buscar_mac(direccion_mac):
    url_api = f"https://api.maclookup.app/v2/macs/{direccion_mac}"
    try:
        respuesta = requests.get(url_api)
        
        if respuesta.status_code == 200:
            datos = respuesta.json()
            if datos.get("found") == False:
                print(f"Dirección MAC: {direccion_mac}")
                print("Fabricante: No encontrado")
            else:
                fabricante = datos.get("company", "No encontrado")
                print(f"Dirección MAC: {direccion_mac}")
                print(f"Fabricante: {fabricante}")
                
        else:
            print(f"Dirección MAC: {direccion_mac}")
            print(f"Error: La API devolvió un código de estado {respuesta.status_code}")

        print(f"Tiempo de respuesta: {respuesta.elapsed.total_seconds() * 1000} ms")
        
    except requests.exceptions.RequestException as e:
        print("Error al conectar con la API:", e)

def mostrar_tabla_arp():
    try:
        salida_arp = subprocess.check_output("arp -a", shell=True).decode('latin-1')
        print("IP / MAC / Fabricante:")

        # Procesar las primeras 10 líneas que contienen direcciones MAC válidas
        lineas_arp = salida_arp.splitlines()
        contador = 0
        for linea in lineas_arp:
            componentes = linea.split()
            if len(componentes) >= 2 and '-' in componentes[1]:
                ip = componentes[0]  # La IP es el primer componente en la línea
                mac_en_arp = componentes[1].replace('-', ':')

                # Omitir direcciones de difusión y multidifusión
                if mac_en_arp.startswith("ff:ff:ff:ff:ff:ff") or mac_en_arp.startswith("01:00:5e"):
                    continue

                # Obtener el fabricante para cada MAC
                fabricante = buscar_mac(mac_en_arp)
                
                # Mostrar la IP, MAC y el fabricante
                print(f"{ip} / {mac_en_arp} / {fabricante}")
                
                # Incrementar el contador y detenerse después de 10 MACs
                contador += 1
                if contador >= 10:
                    break

    except subprocess.CalledProcessError as e:
        print("Error al obtener la tabla ARP:", e)

# Corregir la línea de inicialización
if __name__ == "__main__":
    programa_principal(sys.argv[1:])
 
