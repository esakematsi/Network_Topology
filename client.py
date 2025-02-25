import socket 
import threading
import time 
import os
import sys
from uuid import uuid4

YELLOW = "\033[33m" 
RED = "\033[31m"
GREEN = "\033[32m"
BLUE = "\033[34m"
RESET = "\033[0m"



host = '0.0.0.0'
port = 5000
online=True

VALID_CLIENT_IDS = ['Client1', 'Client2', 'Client3', 'Client4','Client5']
message_timers = {}



def delivery_timer(delivery_event, receiver_id, message_id):
    if not delivery_event.wait(8) and message_id in message_timers:
        print(f"{RED}Delivery Timeout. No acknowledgment received within 8 seconds. Message to {receiver_id} probably failed.{RESET}")
        del message_timers[message_id]


def forwarding_message(client_id, next_client, port, message, prev_client):
    global message_timers
    if message.split('|', 5)[2] == "forward":
        try:
            with socket.socket() as s:
                s.settimeout(3)
                s.connect((next_client, port))
                s.sendall(message.encode('utf-8'))

                if message.split('|', 5)[3] == "delivering":
                    print(f"{YELLOW}Transmission to next client successful.{RESET}")
                    
                    return

        except Exception as e:

            if message.split('|', 5)[3] =='delivering':
                print(f"{YELLOW}Error sending message to next client: {e}{RESET}")
                print(f"{YELLOW}{next_client} not available.{RESET}")


                if next_client=="Client4" and message.split('|', 5)[0] =='Client5':
                    print(f"{RED}Message discarded.{RESET}")
                    return
               
            if message.split('|', 5)[0] in next_client :
                message_id=message.split('|', 5)[4]
                if message_id in message_timers:
                    message_timers[message_id]["event"].set() 
                    del message_timers[message_id]  
                    print(f"{RED}Message discarded.{RESET}")
                return
            

            if client_id=='Client4' and message.split('|', 4)[0] =='Client5':
                print(f"{RED}Message discarded.{RESET}")
                return 

            if message.split('|', 5)[1] =='Client5' and message.split('|', 5)[3] =='delivering':
                message_id=message.split('|', 5)[4]
                if message_id in message_timers:
                    message_timers[message_id]["event"].set() 
                    del message_timers[message_id]  
                    print(f"{RED}Message discarded.{RESET}")
                    return
                
            if message.split('|', 5)[3] =='delivering':
                print(f"{YELLOW}Sending message to previous client at {prev_client}:{port}{RESET}")

            new_message = f"{message.split('|', 5)[0]}|{message.split('|', 5)[1]}|backward|{message.split('|', 5)[3]}|{message.split('|',5)[4]}|{message.split('|',5)[5]}"
            forwarding_message(client_id, next_client, port, new_message, prev_client)

    elif message.split('|', 5)[2] == "backward":
        try:
            
            with socket.socket() as s2:
                s2.settimeout(3)
                s2.connect((prev_client, port))
                s2.sendall(message.encode('utf-8'))

                if message.split('|', 5)[3] == "delivering":
                    print(f"{YELLOW}Transmission to previous client successsful.{RESET}")
                    return

        except Exception as e:
            if message.split('|', 5)[3] =='delivering':
                print(f"{YELLOW}Error sending message to previous client: {e}{RESET}")
                print(f"{YELLOW}{prev_client} not online.{RESET}")
            if message.split('|', 5)[0] in prev_client :
                message_id=message.split('|', 5)[4]
                if message_id in message_timers:
                    message_timers[message_id]["event"].set() 
                    del message_timers[message_id]  
                    print(f"{RED}Message discarded.{RESET}")
                    return
            
            
         



def insert_message(next_client,client_id, prev_client,conn_client, port=5000):
    global online, message_timers
    try:
        while online:
            receiver_id = input("Enter receiver client ID: ").strip().capitalize()
            if receiver_id.lower() == "exit":
                online = False
                print("Exiting...")
                break
            if receiver_id not in VALID_CLIENT_IDS:
                print(f'Invalid recipient ID: {receiver_id}. Please enter a valid client ID.')
                continue
            message = input("Enter message: ")


            if message.lower() == "exit":
                online = False
                print("Exiting...")
                break

            if receiver_id==client_id:
                print("Message for this client: ", message)
                continue


            message_id = str(uuid4())[:16]
            delivery_confirmed = threading.Event() 

            message_timers[message_id] = {
                "event": delivery_confirmed,
                "receiver_id": receiver_id,
            }

            timer_thread = threading.Thread(target=delivery_timer, args=(delivery_confirmed, receiver_id, message_id), daemon=True)
            timer_thread.start()

            

            if receiver_id==prev_client:
                formatted_message = f"{receiver_id}|{client_id}|backward|delivering|{message_id}|{message}"
                forwarding_message(client_id, next_client, port, formatted_message, prev_client)
                continue

            formatted_message = f"{receiver_id}|{client_id}|forward|delivering|{message_id}|{message}"

            if conn_client and receiver_id==conn_client:
                forwarding_message(client_id, conn_client, port, formatted_message, prev_client)
                continue

            if conn_client and client_id=="Client5":
                forwarding_message(client_id, conn_client, port, formatted_message, conn_client)
                continue

            forwarding_message(client_id, next_client, port, formatted_message, prev_client)


            

    except KeyboardInterrupt as e:
        online = False
        print("KeyboardInterrupt: Exiting...")



    
def receiving_message(client_id, next_client, prev_client, conn_client, host='0.0.0.0', port=5000):
    global online
    try:
        with socket.socket() as s:
            s.bind((host, port))
            s.listen()
            print(f"Listening for messages on {host}:{port}")
            while online:
                s.settimeout(3)
                try:
                    conn, addr = s.accept()
                    with conn:
                        
                        data = conn.recv(1024)
                        if data:
                            time.sleep(1)
                            try:
                                message = data.decode('utf-8').split('|', 5)
                                if len(message) != 6:
                                    print(f"{YELLOW}Invalid message format: {data.decode('utf-8')}{RESET}")
                                    continue

                                receiver_id = message[0]
                                sender_id= message[1]
                                direction= message[2]
                                acknolegement=message[3]
                                message_id=message[4]
                                content=message[5]

                                

                                

                                if acknolegement=="delivering":
                                    print(f"{YELLOW}Connected by {addr}{RESET}")
                                


                                if acknolegement=="delivering":
                                    print(f"{YELLOW}Received message: {content}{RESET}")
                                    
                    
                                

                                if receiver_id==client_id:
                                    if acknolegement=="delivered":
                                        print(f"{GREEN}{content}{RESET}")
                                        if message_id in message_timers:
                                            message_timers[message_id]["event"].set() 
                                            del message_timers[message_id]  
                                        continue
                

                                    print(f'Message for this client: {content} [From: {sender_id}]')
                                    ack_message = f"{sender_id}|{client_id}|forward|delivered|{message_id}|Message delivered successfully to recipient {client_id}."

                                    if client_id=="Client5":
                                        forwarding_message(client_id, conn_client, port, ack_message, conn_client)
                                        continue
                                    

                                    forwarding_message(client_id, next_client, port, ack_message, prev_client)
                                    continue

                               

                                    

                                elif receiver_id in VALID_CLIENT_IDS:
                                    if acknolegement=="delivered":
                                        if client_id=="Client4" and receiver_id=="Client5":
                                             forwarding_message(client_id, conn_client, port, data.decode('utf-8'), conn_client)
                                             continue

                                        if receiver_id==prev_client:
                                            forwarding_message(client_id, prev_client, port, data.decode('utf-8'), prev_client)
                                            continue 

                                    if conn_client and receiver_id==conn_client:
                                        print(f"{YELLOW}Forwarding message to connected client at {conn_client}:{port}{RESET}")
                                        forwarding_message(client_id, conn_client, port, data.decode('utf-8'), conn_client)
                                        continue

                                    if receiver_id==prev_client:
                                        if acknolegement=="delivering":
                                            print(f"{YELLOW}Forwarding message to previous client at {prev_client}:{port}{RESET}")
                                        new_message = f"{receiver_id}|{sender_id}|backward|{acknolegement}|{message_id}|{content}"
                                        forwarding_message(client_id, next_client, port, new_message, prev_client)
                                        continue

                                    if direction=="forward":
                                        if acknolegement=="delivering":
                                            print(f"{YELLOW}Forwarding message to next client at {next_client}:{port}{RESET}")
                                        forwarding_message(client_id, next_client, port, data.decode('utf-8'), prev_client)
                                        continue

                                    elif direction=="backward":
                                        if acknolegement=="delivering":
                                            print(f"{YELLOW}Forwarding message to previous client at {prev_client}:{port}{RESET}")
                                        forwarding_message(client_id, next_client, port, data.decode('utf-8'), prev_client)
                                        continue

                            except Exception as e:
                                print(f'Error processing message: {e}')
                except socket.timeout:
                    continue

    except Exception as e:
        if online:
            print(f'Error receiving message: {e}')




def start_client():
    global online
    
    next_client = os.getenv('NEXT_CLIENT')
    client_id = os.getenv('CLIENT_ID')
    prev_client = os.getenv('PREV_CLIENT')
    conn_client = os.getenv('CONN_CLIENT')

    if  not client_id or not (next_client or conn_client):
        print('Error in setting network topology.')
        exit(1)

    print(f'This is: {client_id}')
    try:
        receive_thread = threading.Thread(target=receiving_message, args=(client_id, next_client, prev_client, conn_client, host, port),daemon=True)
        receive_thread.start()
        
        time.sleep(0.3)

        insert_thread= threading.Thread(target=insert_message, args=(next_client,client_id, prev_client,conn_client, port),daemon=True)
        insert_thread.start()


        insert_thread.join()        
        receive_thread.join() 

        
    except KeyboardInterrupt:
        online = False
        print("KeyboardInterrupt: Exiting...")

    print("Client shut down.")
    sys.exit(0)


if __name__ == "__main__":
    start_client()