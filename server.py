import socket
import threading
import json
import sqlite3

conn = sqlite3.connect('emergency_os.db')
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS messages (
                    message_id TEXT PRIMARY KEY,
                    type TEXT,
                    content TEXT,
                    timestamp TEXT,
                    priority TEXT
                )''')
conn.commit()   

s = socket.socket()

port = 12345

s.bind(('', port))
s.listen(5)
print(f"Server listening on port {port}...")

clients = []
message_history = []
sos_senders = {}

def handle_client(c, addr):
    conn = sqlite3.connect("emergency_os.db")
    cursor = conn.cursor()

    clients.append(c)
    while True:
        message = c.recv(1024).decode()

        

        if not message:
            print(f"Connection closed by {addr}")
            c.close()
            clients.remove(c)
            break

        data = json.loads(message)
        message_type = data.get("type")
        if message_type == "ACK":
            acknowledged_message_id = data.get("acknowledged")
            print(f"SOS message {acknowledged_message_id} acknowledged by the server.")
            cursor.execute("SELECT * FROM messages WHERE message_id = ?", (acknowledged_message_id,))
            sos = cursor.fetchone()
            if sos:
                original_sender = sos_senders.get(acknowledged_message_id)
                if original_sender:
                    original_sender.send(f"Your SOS message with ID {acknowledged_message_id} has been acknowledged by the server.".encode())
                print(f"SOS message details: ID: {sos[0]}, Type: {sos[1]}, Content: {sos[2]}, Timestamp: {sos[3]}, Priority: {sos[4]}")
            else:
                print(f"No SOS message found with ID: {acknowledged_message_id}")
            continue
        if message_type == "HISTORY":
            cursor.execute("SELECT * FROM messages")
            rows = cursor.fetchall()
            history = []
            for row in rows:
                history.append({
                    "message_id": row[0],
                    "type": row[1],
                    "content": row[2],
                    "timestamp": row[3],
                    "priority": row[4]
                })
            c.send(json.dumps(history).encode())
            continue
       
        message_content = data.get("message")
        message_id = data.get("message_id")
        timestamp = data.get("timestamp")
        priority = data.get("priority")


        print(f"Received message of type '{message_type}'")
        print(f"Message content: {message_content}")
        print(f"Message ID: {message_id}")
        print(f"Timestamp: {timestamp}")
        print(f"Priority: {priority}")
        if priority == "HIGH":
            print("🚨 HIGH PRIORITY MESSAGE")
            sos_senders[message_id] = c
            for client in clients:
                if client != c:
                    client.send(f"🚨 HIGH PRIORITY MESSAGE from {addr}: {message_content}".encode())
        else:
            for client in clients:
                if client != c:
                    client.send(f"Message from {addr}: {message_content}".encode())
        message_history.append(data)
        cursor.execute("INSERT INTO messages (message_id, type, content, timestamp, priority) VALUES (?, ?, ?, ?, ?)",
                       (message_id, message_type, message_content, timestamp, priority))
        conn.commit()
        c.send(b"Hello, client!")



def show_message_history():
    conn = sqlite3.connect("emergency_os.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM messages")
    rows = cursor.fetchall()
    for row in rows:
        print(f"Message ID: {row[0]}, Type: {row[1]}, Content: {row[2]}, Timestamp: {row[3]}, Priority: {row[4]}")
    conn.close()

while True:
    c, addr = s.accept()
    print(f"Got connection from {addr}")

    threading.Thread(target=handle_client, args=(c, addr)).start()

