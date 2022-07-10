import os
import can
from datetime import datetime
import hmac
import hashlib
import sys
import keys
import id

# Import keys form keys.py file
keys = keys.keys

# Import current CAN id from id.py file
id= id.id["id"]

# Setting the Bitrate for the CAN bus
os.system('sudo ip link set can0 type can bitrate 100000')

# Turning on the CAN network interface
os.system('sudo ifconfig can0 up')

# Checking if the second argument (i.e. python send.py XXXX) is used for setting a custom message
if len(sys.argv) == 2 :
        if len(sys.argv[1]) == 4:
                payload = sys.argv[1]
else:
	print("Custom Message not included or not 4 bytes long.\nSending default message: \"CANs\"")
	payload = "CANs"

	
# Checking if the third argument is set for setting the receiver id i.e the arbitration id of the CAN Frame 
# Set second argument to 1, to send default message 
if len(sys.argv) == 3 :
        if len(sys.argv[2]) == 1:
                receiver = sys.argv[2]
else:
        print("Reciever ID erroneous or not set, Default 0 (Broadcast)")
        receiver = '0'


# Setting the current key to the key used in the communication between Current CAN and the Receiver ID
# Key is taken from the keys package (i.e keys.py)
key = keys[receiver]
key_bytearray = bytearray(key,encoding='utf8')

# Getting the current message counter from the msgCounter file
# Each CAN ECU has its own msgCounter file
f = open('./msgCounter')
file_read = int(f.read())

# if the current message counter is above 127, it is reset to 0
# 127 is the maximum message counter

if(file_read >= 128):
	counter = 0
else:
	counter = file_read
counter_bytearray = bytearray(counter)

# The counter is truncated, so it can be sent in ASCII encoding in the CAN Frame
truncated_counter = counter % 16

# Creating the HMAC from the message i.e payload and the counter
hmac_message = payload + str(counter)
hmac_message = bytearray(hmac_message,encoding='utf8')
h = hmac.new(key_bytearray,hmac_message , hashlib.sha256 )

# The HMAC is truncated, so it can be sent in ASCII encoding in the CAN Frame
hmac_digest = h.hexdigest()[-2:]

# Data to be sent in the CAN Frame
data = id + chr(truncated_counter+64) + payload + hmac_digest

print("ID:", id, "\t\t\t\t\tSize: ", len(id))
print("Counter:", counter , "\t\t\t\tSize: ", len(chr(counter)))
print("Truncated Counter:", truncated_counter, "+64 --> ASCII:",chr(truncated_counter+64), "\tSize: ", len(chr(counter)))
print("Payload:", payload, "\t\t\t\tSize: ", len(payload))
print("HMAC Digest:", hmac_digest, "\t\t\tSize: ", len(hmac_digest))

data = bytearray(data,encoding='utf8')
print("\nData to send: " ,str(data, 'utf-8'), "\t\tSize: ", len(data))


# Sending the CAN Frame
can0 = can.interface.Bus(channel = 'can0',bustype = 'socketcan_ctypes')# socketcan_nati
msg = can.Message(arbitration_id=ord(receiver),data=data,extended_id=False)
can0.send(msg)
# Updating the Message Counter with +1
f = open('./msgCounter','w')
f.write(str(file_read+1))

os.system('sudo ifconfig can0 down')
