import os
import can
from datetime import datetime
import hmac
import hashlib
import keys

keys = keys.keys

os.system('sudo ip link set can0 type can bitrate 100000')
os.system('sudo ifconfig can0 up')

can0 = can.interface.Bus(channel = 'can0', bustype = 'socketcan_ctypes')# socketcan_native
my_id= 'B'


while True:
	print("----------------------------------------------------------------------")
	msg = can0.recv(10.0)
	f = open('./msgCounter')
	file_read = int(f.read())
	if(file_read == 128):
        	counter = 0
	else:
        	counter = file_read

	f = open('./msgCounter','w')
	f.write(str(file_read+1))

	counter_bytearray = bytearray(counter)
	self_truncated_counter = counter % 16

	if msg is None:
		print('Timeout occurred, no message.')
	elif msg.arbitration_id == ord(my_id) or msg.arbitration_id == ord('0'):
		print(msg.data)
		data = msg.data

		id = data[0]
		truncated_counter = data[1] - 64
		print(truncated_counter)
		if (truncated_counter != self_truncated_counter):
			print("ECU out of sync. Sync Required. Message Rejected")
		else:
			payload = data[2:6]
			digest_to_verify = data[-2:]

			if(msg.arbitration_id == ord('0')):
				key = keys["0"]
			else:
				key = keys[chr(id)]

			key_bytearray = bytearray(key,encoding='utf8')

			hmac_message = payload.decode("utf-8") + str(counter)
			hmac_message = bytearray(hmac_message,encoding='utf8')


			h = hmac.new(key_bytearray,hmac_message ,hashlib.sha256 )
			digest_caluclated = h.hexdigest()[-2:]
			print("ID : ", id)
			print("Counter : ", counter, " --> ASCII: ",chr(counter))
			print("Payload : ", payload)
			print("HMAC to verify: ", str(digest_to_verify,"utf-8"))
			print("HMAC generated: ", digest_caluclated)


			if (digest_to_verify == bytearray(digest_caluclated,encoding='utf8')):
				print("Message:", str(payload,"utf-8"), "Accepted" )
				#f = open('./msgCounter','w')
				#f.write(str(file_read+1))
			else:
				print("Message Rejected")

os.system('sudo ifconfig can0 down')
