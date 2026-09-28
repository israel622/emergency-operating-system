import socket
import json
import uuid
import datetime
import threading

s = socket.socket()

port = 12345

s.connect(('localhost', port))
def receive_messages():
    while True:
        data = s.recv(1024)
        if not data:
            break
        print(f"Received: {data.decode()}")

threading.Thread(target=receive_messages, daemon=True).start()
while True:
    choice = input("Enter 's' to send or 'c' to close ")

    if choice == 's':
        message_type = input("Enter message type: ")
        message = input("Enter message to send to server: ")

        message_type = message_type.strip()
        message = message.strip()

        if message_type == "SOS":
            priority = "HIGH"
        elif message_type == "ACK":
            priority = "LOW"
            sos_message_id = input("Enter the SOS message ID to acknowledge: ")
            
        elif message_type == "WARNING":
            priority = "MEDIUM"
        else:
            priority = "LOW"
            
    
        data = {
            "message_id": str(uuid.uuid4()),
            "type": message_type,
            "message": message,
            "timestamp": datetime.datetime.now().isoformat(),
            "priority": priority
        }
        if message_type == "ACK":
            data["acknowledged"] = sos_message_id
            
        json_message = json.dumps(data)

        s.send(json_message.encode())



    elif choice == 'c':
        s.close()
        break
