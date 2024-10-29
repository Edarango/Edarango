import tkinter as tk
from tkinter import ttk
import threading
import socket
import time
import os
from com_handler import COMHandler

server_socket = None  # Variable global para el socket del servidor
is_socket_open = False  # Variable para verificar si el socket está abierto
stop_event = threading.Event()  # Evento para detener el hilo del servidor

def create_gui():
    global root  # Hacer root global
    try:
        global protocol_var, connection_status_label, canvas, connection_circle

        root = tk.Tk()
        root.title("Receptora de Eventos de Alarmas")

        # Obtén la ruta completa del ícono
        icon_path = os.path.join(os.path.dirname(__file__), "Main_logo.png")

        # cargar el ícono
        try:
            root.iconphoto(True, tk.PhotoImage(file=icon_path))
        except Exception as e:
            print(f"Error al cargar el ícono: {e}")

        
        # Cambiar el color de fondo de la ventana principal
        root.configure(bg="#303030")

        # Etiqueta y cuadro de entrada para la IP
        ip_label = tk.Label(root, text="Server IP:", bg="#303030", fg="white")
        ip_label.grid(row=0, column=0, padx=10, pady=10)
        ip_entry = tk.Entry(root)
        ip_entry.grid(row=0, column=1, padx=10, pady=10)
        ip_entry.insert(0, "192.168.1.134")  # Valor predeterminado

        # Etiqueta y cuadro de entrada para el puerto
        port_label = tk.Label(root, text="Server Port:", bg="#303030", fg="white")
        port_label.grid(row=1, column=0, padx=10, pady=10)
        port_entry = tk.Entry(root)
        port_entry.grid(row=1, column=1, padx=10, pady=10)
        port_entry.insert(0, "9294")  # Puerto predeterminado

        # Variable para almacenar el protocolo seleccionado
        protocol_var = tk.StringVar(value="SIA DC-09")

        # Selector de protocolo
        protocol_label = tk.Label(root, text="Select Protocol:", bg="#303030", fg="white")
        protocol_label.grid(row=2, column=0, padx=10, pady=10)
        protocol_menu = ttk.Combobox(root, textvariable=protocol_var)
        protocol_menu['values'] = ("SIA DC-09", "Contact ID")
        protocol_menu.grid(row=2, column=1, padx=10, pady=10)

        # Lista para mostrar eventos (ancho de 100 y color #F7F7F7)
        event_list = tk.Listbox(root, height=25, width=120, bg="#F7F7F7")  # Color del ListBox
        event_list.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

        # Espacio para el estado de la conexión
        tk.Label(root, text="Connection Status", bg="#303030", fg="#1DCF8E").grid(row=4, column=0, padx=10, pady=10)
        
        # Crear un canvas para mostrar los círculos de estado
        # Crear un canvas para mostrar los círculos de estado con color de fondo #303030
        canvas = tk.Canvas(root, width=50, height=50, bg="#303030", highlightthickness=0)
        canvas.grid(row=4, column=1)
        
        # Crear el círculo rojo (offline) por defecto
        connection_circle = canvas.create_oval(5, 5, 20, 20, fill="red")

        # Etiqueta que muestra el estado actual (online/offline)
        connection_status_label = tk.Label(root, text="Offline", fg="red", bg="#303030")
        connection_status_label.grid(row=5, column=1)

        # Botón para iniciar la recepción de eventos
        start_button = tk.Button(root, text="Iniciar Receptora", command=lambda: start_listener(event_list, ip_entry, port_entry))
        start_button.grid(row=6, column=0, columnspan=2, pady=20,)

        # Botón para detener la recepción de eventos
        stop_button = tk.Button(root, text="Detener Receptora", command=stop_listener)
        stop_button.grid(row=6, column=1, columnspan=2, pady=20,)

        root.protocol("WM_DELETE_WINDOW", on_closing)  # Manejar el cierre de la ventana
        root.mainloop()
    except Exception as e:
        print(f"Error en la GUI: {e}")

# Función para actualizar la lista de eventos en la GUI
def update_event_display(event_list, event_data):
    try:
        event_list.insert(tk.END, event_data)
        event_list.see(tk.END)  # Desplaza hacia el final de la lista
    except Exception as e:
        print(f"Error actualizando la lista de eventos: {e}")

# Función para actualizar el estado de la conexión
def update_connection_status(is_online):
    try:
        global canvas, connection_circle, connection_status_label
        if is_online:
            canvas.itemconfig(connection_circle, fill="green")
            connection_status_label.config(text="Connected", fg="green", bg="#303030")
        else:
            canvas.itemconfig(connection_circle, fill="red")
            connection_status_label.config(text="Not Connected", fg="red", bg="#303030")
    except Exception as e:
        print(f"Error actualizando el estado de conexión: {e}")

# Función para escuchar los eventos y actualizar la interfaz
def start_listener(event_list, ip_entry, port_entry):
    global is_socket_open, stop_event  # Usar las variables globales
    try:
        ip = ip_entry.get()  # Obtener la IP desde el cuadro de entrada
        port = int(port_entry.get())  # Obtener el puerto desde el cuadro de entrada
        protocol = protocol_var.get()  # Protocolo seleccionado

        # Inicia el servidor SIA en un hilo separado
        stop_event.clear()  # Asegurarse de que el evento de parada esté limpio
        server_thread = threading.Thread(target=start_sia_server, args=(ip, port, protocol, update_connection_status, event_list))
        server_thread.daemon = True  # Permitir que el hilo se cierre cuando se cierra la aplicación
        server_thread.start()

        is_socket_open = True  # Marcar el socket como abierto
        print(f"Starting to listen on {ip}:{port} using {protocol} protocol...")  # Mensaje de depuración
    except Exception as e:
        print(f"Error al iniciar el listener: {e}")

# Función para detener la recepción de eventos
def stop_listener():
    global server_socket, is_socket_open  # Asegurarse de que server_socket es global
    try:
        if is_socket_open:  # Solo cerrar si está abierto
            stop_event.set()  # Señaliza al hilo del servidor que debe detenerse
            time.sleep(1)  # Espera un momento para permitir que el hilo cierre el socket
            if server_socket:
                server_socket.close()  # Cerrar el socket
            is_socket_open = False  # Marcar el socket como cerrado
            update_connection_status(False)
            print("Receptora detenida.")
    except Exception as e:
        print(f"Error al detener la receptora: {e}")

def on_closing():
    stop_listener()  # Asegurarse de que el socket se cierre al cerrar la ventana
    root.destroy()  # Cerrar la ventana

def start_sia_server(ip, port, protocol, update_connection_status, event_list):
    global server_socket  # Hacer que el socket sea global para que se pueda cerrar
    try:
        global server_socket
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((ip, port))
        server_socket.listen(5)

        print(f"Listening on {ip}:{port} using {protocol} protocol...")
        update_connection_status(True)

        while not stop_event.is_set():  # Esperar hasta que se establezca la señal de parada
            try:
                client_socket, addr = server_socket.accept()
                print(f"Connection from {addr}")

                while not stop_event.is_set():  # Bucle para seguir recibiendo datos del cliente
                    data = client_socket.recv(1024).decode()
                    if not data:
                        break

                    # Aquí se procesaría el evento de acuerdo al protocolo
                    event_data = f"Event received from {addr}: {data}\n"  # Agregar salto de línea

                    # Actualiza la lista de eventos en la GUI
                    update_event_display(event_list, event_data)

                    # Responder ACK (ejemplo)
                    client_socket.send("ACK".encode())

                client_socket.close()
            except Exception as e:
                print(f"Error en la conexión del cliente: {e}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        if server_socket:
            server_socket.close()  # Asegúrate de cerrar el socket al final
        update_connection_status(False)
        print("Server stopped.")


# Ejecuta la creación de la GUI
create_gui()
