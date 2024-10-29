import socket

def start_contact_id_server(ip, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((ip, port))
        s.listen(1)
        print(f"Contact ID Server listening on {ip}:{port}")
        
        conn, addr = s.accept()
        with conn:
            print(f"Connected by {addr}")
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                print(f"Contact ID Event Received: {data.decode('utf-8')}")
                conn.sendall(b"ACK")
                return data.decode('utf-8')
  