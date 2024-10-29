# server.py
import socket
import tkinter as tk

def start_sia_server(ip, port, protocol, update_connection_status, event_list):
    try:
        # Crear el socket
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((ip, port))
        server_socket.listen(5)

        print(f"Listening on {ip}:{port} using {protocol} protocol...")

        # Actualiza el estado de la conexión a "Online" usando el callback
        update_connection_status(True)

        while True:
            # Espera conexiones entrantes
            client_socket, addr = server_socket.accept()
            print(f"Connection from {addr}")

            # Recibe datos de eventos (simulación)
            data = client_socket.recv(1024).decode()
            if not data:
                break

            # Procesar el evento (puedes agregar lógica específica aquí)
            event_data = f"Event received from {addr}: {data}"

            # Actualiza la lista de eventos en la GUI
            event_list.insert(tk.END, event_data)

            # Responder ACK (ejemplo)
            client_socket.send("ACK".encode())

        client_socket.close()

    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Actualiza el estado de la conexión a "Offline"
        update_connection_status(False)
        print("Server stopped.")
