import tkinter as tk
from tkinter import ttk
import threading
from sia_handler import start_sia_server
import socket

# Variable global para manejar el hilo del servidor y el socket
server_socket = None
server_thread = None
server_running = False  # Control para detener el servidor

def create_gui():
    global protocol_var, connection_status_label, canvas, connection_circle, event_list, root

    root = tk.Tk()
    root.title("Receptora de Eventos de Alarmas")

    # Configuración de la cuadrícula
    root.grid_rowconfigure(3, weight=1)  # Permitir que la fila 3 (event_list) se expanda
    root.geometry("600x400")  # Tamaño inicial de la ventana

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
    port_entry.insert(0, "9294")  # Valor predeterminado

    # Variable para almacenar el protocolo seleccionado
    protocol_var = tk.StringVar(value="SIA DC-09")

    # Selector de protocolo
    protocol_label = tk.Label(root, text="Select Protocol:")
    protocol_label.grid(row=2, column=0, padx=10, pady=10)
    protocol_menu = ttk.Combobox(root, textvariable=protocol_var)
    protocol_menu['values'] = ("SIA DC-09", "Contact ID")
    protocol_menu.grid(row=2, column=1, padx=10, pady=10)

    # Lista para mostrar eventos
    event_list = tk.Listbox(root, height=15, width=70)
    event_list.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

    # Espacio para el estado de la conexión
    tk.Label(root, text="Connection Status").grid(row=4, column=0, padx=10, pady=10)

    # Crear un canvas para mostrar los círculos de estado
    canvas = tk.Canvas(root, width=50, height=50)
    canvas.grid(row=4, column=1, padx=10, pady=10)

    # Crear el círculo rojo (offline) por defecto
    connection_circle = canvas.create_oval(5, 5, 20, 20, fill="red")

    # Etiqueta que muestra el estado actual (online/offline)
    connection_status_label = tk.Label(root, text="Offline", fg="red")
    connection_status_label.grid(row=5, column=1)

    # Botón para iniciar la recepción de eventos
    start_button = tk.Button(root, text="Iniciar Receptora", command=lambda: start_listener(ip_entry, port_entry))
    start_button.grid(row=6, column=0, pady=20)

    # Botón para detener la recepción de eventos
    stop_button = tk.Button(root, text="Detener Receptora", command=stop_listener)
    stop_button.grid(row=6, column=1, pady=20)

    # Ajustar el cuadro de eventos al tamaño de la pantalla al maximizar
    root.bind("<Configure>", lambda event: adjust_event_list(event_list, root))

    root.mainloop()


# Función para actualizar la lista de eventos en la GUI
def update_event_display(event_data):
    event_list.insert(tk.END, event_data)

# Función para actualizar el estado de la conexión
def update_connection_status(is_online):
    if is_online:
        canvas.itemconfig(connection_circle, fill="green")
        connection_status_label.config(text="Online", fg="green")
    else:
        canvas.itemconfig(connection_circle, fill="red")
        connection_status_label.config(text="Offline", fg="red")

# Función para escuchar los eventos y actualizar la interfaz
def start_listener(ip_entry, port_entry):
    global server_socket, server_thread, server_running
    ip = ip_entry.get()  # Obtener la IP desde el cuadro de entrada
    port = int(port_entry.get())  # Obtener el puerto desde el cuadro de entrada
    protocol = protocol_var.get()  # Protocolo seleccionado

    server_running = True  # Control para permitir que el servidor corra

    # Inicia el servidor SIA en un hilo separado
    server_thread = threading.Thread(target=start_sia_server, args=(ip, port, protocol, update_connection_status, event_list))
    server_thread.start()
    update_connection_status(True)  # Cambia el estado a "Online"
    print(f"Starting to listen on {ip}:{port} using {protocol} protocol...")  # Mensaje de depuración

def stop_listener():
    global server_socket, server_thread, server_running
    server_running = False  # Detener el servidor

    if server_socket:
        try:
            server_socket.close()  # Cierra el socket
        except Exception as e:
            print(f"Error closing socket: {e}")
    if server_thread and server_thread.is_alive():
        server_thread.join()  # Espera que el hilo termine
    update_connection_status(False)  # Cambia el estado a "Offline"
    print("Server stopped.")

def adjust_event_list(event_list, root):
    # Ajustar el tamaño del cuadro de eventos
    event_list.config(height=(root.winfo_height() // 20))  # Cambia el divisor según tu diseño

# ---------------- Función start_sia_server -------------------------
def start_sia_server(ip, port, protocol, update_connection_status, event_list):
    global server_socket, server_running
    try:
        # Crear el socket
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((ip, port))
        server_socket.listen(5)
        
        print(f"Listening on {ip}:{port} using {protocol} protocol...")

        # Actualiza el estado de la conexión a "Online"
        update_connection_status(True)

        while server_running:
            # Espera conexiones entrantes
            client_socket, addr = server_socket.accept()
            print(f"Connection from {addr}")

            # Recibe datos de eventos (simulación)
            data = client_socket.recv(1024).decode()
            if not data:
                break

            # Aquí se procesaría el evento de acuerdo al protocolo (SIA o Contact ID)
            event_data = f"Event received from {addr}: {data}"
            
            # Actualiza la lista de eventos en la GUI
            event_list.insert(tk.END, event_data)

            # Responder ACK (ejemplo)
            client_socket.send("ACK".encode())

        client_socket.close()

    except Exception as e:
        print(f"Error: {e}")
    finally:
        update_connection_status(False)
        print("Server stopped.")
