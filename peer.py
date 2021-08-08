

import sys
import getopt
import socket
import random
from threading import Thread
import os
import time
import math
import queue
import json
import hashlib
from cryptography.fernet import Fernet
import rsa

'''
Write your code inside this class. 
In the start() function, you will read user-input and act accordingly.
receive_handler() function is running another thread and you have to listen 
for incoming messages in this function.
'''

# Block for the transaction, which is send to the miner. It contains the data and the required fields as shown in the class intialisation.
# Transcation is validated and broadcasted to the entire network. 3 transcations form a block and then the block is added to the blockchain.
class Block:

    def __init__(self, block_id, prev_hash, apna_hash, data, utxo, encrypted_hash):
        
        if prev_hash == 0:
            #genesis
            self.data = data
            self.block_id = block_id
            self.prev_hash = 0
            self.apna_hash = apna_hash
            self.utxo = utxo
            self.encrypted_hash = encrypted_hash

        else:
            #other
            self.data = data
            self.block_id = block_id
            self.prev_hash = prev_hash
            self.apna_hash = apna_hash
            self.utxo = utxo  
            self.encrypted_hash = encrypted_hash 

class Client:
    '''
    This is the main Client Class. 
    '''
    def __init__(self, username, dest, port):
        # sockets initialisation
        self.server_addr = dest
        self.server_port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(None)
        self.sock.bind(('', random.randint(10000, 40000)))
        self.name = username
        
        # State variables
        self.utxo = 10
        self.block_id = 1
        self.prev_hash = 0
        self.apna_hash = 0 
        self.public_ledger = []
        self.skins = []
        self.valo_coins = 0

    def start(self):
       

        while True:
            print()
            print()
            print("********** Welcome to GameDapp **********")
            print("Do you want to Enter the network?")
            print("Press Y if you agree , N if you dont agree")
            if input().lower()=="y":
                self.sock.sendto(("Join " + self.name).encode("utf-8"), (self.server_addr, self.server_port))
            else:
                if input().lower()=="n":
                    sys.exit
                    sys.clear()
                #quit
            print("Congratulations you are part of GameDapp, have fun sharing virutal assets!")
            print("Commands :")
            print("Enter 1 if you want to trade with a peer")
            print("Enter 2 if you want to trade with game")

            x = int(input())

            if x==1:
                print("Who do you want to send Pasha Coins?")
                rec = input()
                print("How many Pasha Coins do you want to send to")
                amount  = int(input())

            if x==2:
                print("You can trade with the following games")
                print("Valorant(enter V, uppercase, for this)")
                av = (input())
                print(av)
                if av=="V":
                    print("Following assets are available: ")
                    print("Press 1 for game points ")
                    print("Press 2 for pasha coins transfer")
                    x_= int(input())
                    if x_==1:
                        print("Trade rate for valorant game points : 100 valo = 1 pasha")
                        print("Do you want to proceed? Press (Y/N)")
                        if input().lower()=="y":
                            print("How many points to add? 100 valo point = 1 pasha coin (enter whole numbers)")
                            coin = int(input())

                            self.utxo -= coin/100
                            self.valo_coins+=coin
                            print("added coins")
                            continue
                        if input().lower()=="n":
                            sys.exit
                            sys.clear()
                    if x_==2:
                        print("Following skins are available:")
                        print("Prime-Vandal, Omni-Phantom, Gold-Dagger")
                        sk = input().lower()
                        if sk=="prime-vandal":
                            print("Do you want to buy Prime-Vandal for 5 Pasha? Press(Y/N)")
                            x3 = (input())
                            if x3.lower()=="y":
                                self.skins.append("Prime-Vandal")
                                self.utxo -= 5
                                print("skin added")
                                continue
                            if x3.lower()=="n":
                                sys.exit
                                sys.clear()
                        if sk=="Omni-Phantom":
                            print("Do you want to buy for 5 Pasha? Press(Y/N)")
                            x3 = (input())
                            if x3.lower()=="y":
                                self.skins.append("Omni-Phantom")
                                self.utxo -= 5
                                print("skin added")
                                continue
                            if x3.lower()=="n":
                                sys.exit
                                sys.clear()

                        if sk=="Gold-Dagger":
                            print("Do you want to buy for 5 Pasha? Press(Y/N)")
                            x3 = (input())
                            if x3.lower()=="y":
                                self.skins.append("Gold-Dagger")
                                self.utxo -= 5
                                print("skin added")
                                continue
                            if x3.lower()=="n":
                                sys.exit
                                sys.clear()

                continue

            self.utxo = self.utxo-amount
            data = [{"receiver": rec, "sender": self.name, "UTXO": amount}]
            data = json.dumps(data)
            self.public_ledger.append(data)
            name = self.name+".txt"
            f = open(name, "a")
            f.write(json.dumps(json.loads(data)))
            f.write("\n")
            f.close()

            self.apna_hash = self.hasher(data)
            encrypted_hash = self.encrypt(self.apna_hash)



            block = Block(self.block_id, self.prev_hash, self.apna_hash, data, amount,encrypted_hash)

            block = json.dumps(block,default=vars)

            self.sock.sendto(block.encode("utf-8"), (self.server_addr, self.server_port))
            print("Transcation Successful")

    def receive_handler(self):

        while True:
            
            # Listens for incoming data. Updates the public ledger and if the data is meant for the current user, it updates its values and acts correspondingly.

            Packet, address = self.sock.recvfrom(120000)
            Incoming_Packet = Packet.decode("utf-8")

            block = json.loads(Incoming_Packet)
            data = json.loads(block['data'])


            self.public_ledger.append(data)
            name = self.name+".txt"

            f = open(name, "a")
            f.write(json.dumps(data))
            f.write("\n")
            f.close()

            # Finds the hash of the data and decrypts the hash of the encrypted hash and if both are equal adds the corresponding to the wallet and further transactions.

            hash_of_data = self.hasher(json.dumps(data))
            encrypted_hash_of_block = block['encrypted_hash']

            decrypted_hash = self.decrypt(encrypted_hash_of_block)

            if hash_of_data == decrypted_hash:
                if data[0]['receiver'] == self.name:
                    self.utxo += data[0]['UTXO']
                print('Coins Recieved, New balance is ' ,self.utxo)


    # Hasher uses the sha256 to hash the data
    def hasher(self, data):
        DIGEST = hashlib.sha256(json.dumps(data,sort_keys=True).encode('utf8')).hexdigest()
        return DIGEST

    # Encryptor uses string manipualtion to manipulate and encrypt the string
    def encrypt(self, hashh):
        Lfirst = hashh[0 :4] 
        Lsecond = hashh[4 :] 
        return Lsecond+Lfirst
    
    # Decryptor uses state of the art string manipulation to decrypt the string.
    def decrypt(self,hashh):
        Lfirst = hashh[len(hashh)-4:]
        Lsecond = hashh[0:len(hashh)-4]
        return Lfirst+Lsecond

    def load_ledger(self):
        try:
            name = self.name+".txt"
            f = open(name, "r")
            print(f.read())
        except:
            pass
        

if __name__ == "__main__":
    def helper():
        '''
        This function is just for the sake of our Client module completion
        '''
        print("Client")
        print("-u username | --user=username The username of Client")
        print("-p PORT | --port=PORT The server port, defaults to 15000")
        print("-a ADDRESS | --address=ADDRESS The server ip or hostname, defaults to localhost")
        print("-w WINDOW_SIZE | --window=WINDOW_SIZE The window_size, defaults to 3")
        print("-h | --help Print this help")
    try:
        OPTS, ARGS = getopt.getopt(sys.argv[1:],
                                   "u:p:a:w", ["user=", "port=", "address=","window="])
    except getopt.error:
        helper()
        exit(1)

    PORT = 48601
    DEST = "localhost"
    USER_NAME = None

    for o, a in OPTS:
        if o in ("-u", "--user="):
            USER_NAME = a
        elif o in ("-p", "--port="):
            PORT = int(a)
        elif o in ("-a", "--address="):
            DEST = a


    if USER_NAME is None:
        print("Missing Username.")
        helper()
        exit(1)

    S = Client(USER_NAME, DEST, PORT)
    try:
        # S.load_ledger()
        # Start receiving Messages
        T = Thread(target=S.receive_handler)
        T.daemon = True
        T.start()
        # Start Client
        S.start()
    except (KeyboardInterrupt, SystemExit):
        sys.exit()