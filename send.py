import os
import can
from datetime import datetime
import hmac
import hashlib
import sys
import keys
import id


keys = keys.keys
id= id.id["id"]

os.system('sudo ip link set can0 type can bitrate 100000')
os.system('sudo ifconfig can0 up')

if len(sys.argv) == 2 :
        if len(sys.argv[1]) == 4:
                payload = sys.argv[1]
else:
	print("Custom Message not included or not 4 bytes long.\nSending default message: \"CANs\"")
	payload = "CANs"


if len(sys.argv) == 3 :
        if len(sys.argv[2]) == 1:
                receiver = sys.argv[2]
else:
        print("Reciever ID erroneous or not set, Default 0 (Broadcast)")
        receiver = '0'



key = keys[receiver]
key_bytearray = bytearray(key,encoding='utf8')


f = open('./msgCounter')
file_read = int(f.read())

if(file_read == 128):
	counter = 0
else:
	counter = file_read
counter_bytearray = bytearray(counter)
truncated_counter = counter % 16
#time = datetime.now()
#time_minutes_hours = str(time.hour) + str(time.minute)
#counter = int(time_minutes_hours) % 127
#counter_bytearray = bytearray(counter)

hmac_message = payload + str(counter)
hmac_message = bytearray(hmac_message,encoding='utf8')

h = hmac.new(key_bytearray,hmac_message , hashlib.sha256 )
hmac_digest = h.hexdigest()[-2:]
data = id + chr(truncated_counter+64) + payload + hmac_digest

print("ID:", id, "\t\t\t\t\tSize: ", len(id))
print("Counter:", counter , "\t\t\t\tSize: ", len(chr(counter)))
print("Truncated Counter:", truncated_counter, "+64 --> ASCII:",chr(truncated_counter+64), "\tSize: ", len(chr(counter)))
print("Payload:", payload, "\t\t\t\tSize: ", len(payload))
print("HMAC Digest:", hmac_digest, "\t\t\tSize: ", len(hmac_digest))

data = bytearray(data,encoding='utf8')
print("\nData to send: " ,str(data, 'utf-8'), "\tSize: ", len(data))


can0 = can.interface.Bus(channel = 'can0',bustype = 'socketcan_ctypes')# socketcan_nati
msg = can.Message(arbitration_id=ord(receiver),data=data,extended_id=False)

can0.send(msg)
f = open('./msgCounter','w')
f.write(str(file_read+1))

os.system('sudo ifconfig can0 down')
