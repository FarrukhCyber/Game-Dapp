'''
This module defines the behaviour of server in your Chat Application
'''
import sys
import getopt
import socket
from threading import Thread
import queue
import time
import math
import json
import llist
import hashlib
from llist import dllist as doublell

class Block:

    def __init__(self, block_id, prev_hash, apna_hash, data):
        
        self.data = data
        self.block_id = block_id
        self.prev_hash = prev_hash
        self.apna_hash = apna_hash

class Server:
    '''
    This is the main Server Class. You will to write Server code inside this class.
    '''
    def __init__(self, dest, port):
        self.server_addr = dest
        self.server_port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.settimeout(None)
        self.sock.bind((self.server_addr, self.server_port))

        self.connections = {}
        self.transactions = 0
        self.public_ledger = []
        self.blockchain = doublell()
        self.hash_of_prev_block = ""
        self.temp_chain = []
        self.block_id = 1


    def start(self):
        while True:
            Packet, address = self.sock.recvfrom(4096)
            
            Incoming_packet = Packet.decode("utf-8")

            try:
                block = json.loads(Incoming_packet)
                data = json.loads(block['data'])
                self.public_ledger.append(data)


            except:
                Incoming_packet =  Incoming_packet.split()
                if Incoming_packet[0] == "Join":
                    if address[0] not in self.connections.keys():
                        self.connections[address] = Incoming_packet[1]
                        continue

            name = "miner.txt"
            f = open(name, "a")
            f.write(json.dumps(data))
            f.write("\n")
            f.close()
             # Puts the block in blockchain after 3 transactions, Handles the hashing of the previous hash block
            if self.transactions == 3:

               

                if self.blockchain.size == 0:
                    blockchain_block = Block(self.block_id,self.hash_of_prev_block,self.hasher(self.temp_chain),self.temp_chain)
                    self.blockchain.append(blockchain_block) 

                    self.hash_of_prev_block = self.hasher(self.temp_chain)
                    self.block_id +=1
                    self.temp_chain.clear()

                else:
                    blockchain_block = Block(self.block_id,self.hash_of_prev_block,self.hasher(self.temp_chain),self.temp_chain)
                    self.blockchain.append(blockchain_block) 
                    self.hash_of_prev_block = self.hasher(self.temp_chain)
                    self.temp_chain.clear()
                    self.block_id +=1

                self.transactions=0
            

            else:
                self.temp_chain.append(data)
                self.transactions +=1

            # broadcasting
           
            for addr in self.connections.keys():
                if addr != address:
                    self.sock.sendto(Packet,addr)


    #sha256 hasher
    def hasher(self, data):
        DIGEST = hashlib.sha256(json.dumps(data,sort_keys=True).encode('utf8')).hexdigest()
        return DIGEST


if __name__ == "__main__":
    def helper():
        '''
        This function is just for the sake of our module completion
        '''
        print("Server")
        print("-p PORT | --port=PORT The server port, defaults to 15000")
        print("-a ADDRESS | --address=ADDRESS The server ip or hostname, defaults to localhost")
        print("-w WINDOW | --window=WINDOW The window size, default is 3")
        print("-h | --help Print this help")

    try:
        OPTS, ARGS = getopt.getopt(sys.argv[1:],
                                   "p:a:w", ["port=", "address=","window="])
    except getopt.GetoptError:
        helper()
        exit()

    PORT = 48601
    DEST = "localhost"

    for o, a in OPTS:
        if o in ("-p", "--port="):
            PORT = int(a)
        elif o in ("-a", "--address="):
            DEST = a

    SERVER = Server(DEST, PORT)
    try:
        # SERVER.load_ledger()
        SERVER.start()
    except (KeyboardInterrupt, SystemExit):
        exit()