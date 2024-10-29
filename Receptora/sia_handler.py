import tkinter as tk
from tkinter import ttk
import threading
import socket

# Variables globales para el socket y el hilo
server_socket = None
server_thread = None
running = False  # Variable para controlar si el servidor está en funcionamiento

def create_gui():
    global protocol_var, connection_status_label, canvas, connection_circle

    root = tk.Tk()
    root.title("Receptora de Eventos de Alarmas")

    # Etiqueta y cuadro de entrada para la IP
    ip_label = tk.Label(root, text="Server IP:")
    ip_label.grid(row=0, column=0, padx=10, pady=10)
    ip_entry = tk.Entry(root)
    ip_entry.grid(row=0, column=1, padx=10, pady=10)
    ip_entry.insert(0, "192.168.1.134")  # Valor predeterminado

    # Etiqueta y cuadro de entrada para el puerto
    port_label = tk.Label(root, text="Server Port:")
    port_label.grid(row=1, column=0, padx=10, pady=10)
    port_entry = tk.Entry(root)
    port_entry.grid(row=1, column=1, padx=10, pady=10)
    port_entry.insert(0, "9294")  # Puerto predeterminado

    # Variable para almacenar el protocolo seleccionado
    protocol_var = tk.StringVar(value="SIA DC-09")

    # Selector de protocolo
    protocol_label = tk.Label(root, text="Select Protocol:")
    protocol_label.grid(row=2, column=0, padx=10, pady=10)
    protocol_menu = ttk.Combobox(root, textvariable=protocol_var)
    protocol_menu['values'] = ("SIA DC-09", "Contact ID")
    protocol_menu.grid(row=2, column=1, padx=10, pady=10)

    # Lista para mostrar eventos
    global event_list
    event_list = tk.Listbox(root, height=20, width=50)  # Aumentar la altura
    event_list.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

    # Espacio para el estado de la conexión
    tk.Label(root, text="Connection Status").grid(row=4, column=0, padx=10, pady=10)

    # Crear un canvas para mostrar los círculos de estado
    canvas = tk.Canvas(root, width=50, height=50)
    canvas.grid(row=4, column=1)

    # Crear el círculo rojo (offline) por defecto
    connection_circle = canvas.create_oval(5, 5, 20, 20, fill="red")

    # Etiqueta que muestra el estado actual (online/offline)
    connection_status_label = tk.Label(root, text="Offline", fg="red")
    connection_status_label.grid(row=5, column=1)

    # Botón para iniciar la recepción de eventos
    start_button = tk.Button(root, text="Iniciar Receptora", command=lambda: start_listener(ip_entry, port_entry))
    start_button.grid(row=6, column=0, columnspan=2, pady=20)

    # Botón para detener la recepción de eventos
    stop_button = tk.Button(root, text="Detener Receptora", command=stop_listener)
    stop_button.grid(row=7, column=0, columnspan=2, pady=20)

    root.mainloop()

# Función para actualizar el estado de la conexión
def update_connection_status(is_online):
    global canvas, connection_circle, connection_status_label
    if is_online:
        canvas.itemconfig(connection_circle, fill="green")
        connection_status_label.config(text="Online", fg="green")
    else:
        canvas.itemconfig(connection_circle, fill="red")
        connection_status_label.config(text="Offline", fg="red")

# Función para escuchar los eventos y actualizar la interfaz
def start_listener(ip_entry, port_entry):
    global server_thread, running
    if not running:  # Solo iniciar si no está corriendo
        running = True
        ip = ip_entry.get()
        port = int(port_entry.get())
        protocol = protocol_var.get()

        # Inicia el servidor SIA en un hilo separado
        server_thread = threading.Thread(target=start_sia_server, args=(ip, port, protocol, update_connection_status))
        server_thread.start()

        print(f"Starting to listen on {ip}:{port} using {protocol} protocol...")
    else:
        print("El servidor ya está en funcionamiento.")

# Función para detener la recepción de eventos
def stop_listener():
    global running, server_socket
    if running:
        running = False
        if server_socket:
            server_socket.close()  # Cierra el socket del servidor
            print("Receptora detenida.")
        else:
            print("No hay receptora activa.")
    else:
        print("El servidor ya está detenido.")

def start_sia_server(ip, port, protocol, update_connection_status):
    global server_socket
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((ip, port))
        server_socket.listen(5)

        print(f"Listening on {ip}:{port} using {protocol} protocol...")
        update_connection_status(True)

        while running:  # Solo sigue ejecutando si está en funcionamiento
            client_socket, addr = server_socket.accept()
            print(f"Connection from {addr}")

            while running:  # Bucle para seguir recibiendo datos del cliente
                data = client_socket.recv(1024).decode()
                if not data:
                    break

                # Procesar el evento y actualizar la lista de eventos
                event_data = f"Event received from {addr}: {data}\n"  # Agregar salto de línea
                event_list.insert(tk.END, event_data)
                event_list.see(tk.END)  # Desplaza hacia el final de la lista

                client_socket.send("ACK".encode())

            client_socket.close()

    except Exception as e:
        print(f"Error: {e}")
    finally:
        update_connection_status(False)
        print("Server stopped.")

# Ejecuta la creación de la GUI
create_gui()
