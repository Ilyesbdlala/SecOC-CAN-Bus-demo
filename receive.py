import os
import can
from datetime import datetime
import hmac
import hashlib
import keys
import id

# Import keys form keys.py file
keys = keys.keys

# Setting the Bitrate for the CAN bus
os.system('sudo ip link set can0 type can bitrate 100000')

# Turning on the CAN network interface
os.system('sudo ifconfig can0 up')

can0 = can.interface.Bus(channel = 'can0', bustype = 'socketcan_ctypes')# socketcan_native

# Import current CAN id from id.py file
my_id= id.id["id"]


while True:
	print("----------------------------------------------------------------------")
	# Waiting on the Message to be received with a Timeout of 10s
	msg = can0.recv(10.0)


	if msg is None:
		print('Timeout occurred, no message.')
	else:
		# Getting the current message counter from the msgCounter file
		# Each CAN ECU has its own msgCounter file
		f = open('./msgCounter')
		file_read = int(f.read())
		# if the current message counter is above 127, it is reset to 0
		# 127 is the maximum message counter
		if(file_read == 128):
			counter = 0
		else:
			counter = file_read
			
		# Updating the Message Counter with +1
		f = open('./msgCounter','w')
		f.write(str(file_read+1))

		counter_bytearray = bytearray(counter)
		# Truncating counter to compare with truncated counter from received CAN Frame
		self_truncated_counter = counter % 16
		# Checking if the arbitration_id is this CAN's ID or Broadcast message ID
		if msg.arbitration_id == ord(my_id) or msg.arbitration_id == ord('0'):
			print(msg.data)
			data = msg.data

			id = data[0]
			truncated_counter = data[1] - 64
			print(truncated_counter)
			# if truncated counter is not the same as the one locally, that one of the ECUs is out of sync
			if (truncated_counter != self_truncated_counter):
				print("ECU out of sync. Sync Required. Message Rejected")
			else:
				# Extracting the different values from the Frame received
				payload = data[2:6]
				digest_to_verify = data[-2:]
				
				# If it's broadcast message use broadcast key, otherwise use the corresponding sender key
				if(msg.arbitration_id == ord('0')):
					key = keys["0"]
				else:
					key = keys[chr(id)]

				key_bytearray = bytearray(key,encoding='utf8')
				# Calculating the hmac of the recieved message payload
				hmac_message = payload.decode("utf-8") + str(counter)
				hmac_message = bytearray(hmac_message,encoding='utf8')
				h = hmac.new(key_bytearray,hmac_message ,hashlib.sha256 )
				
				# Truncating the HMAC
				digest_caluclated = h.hexdigest()[-2:]
				
				print("ID : ", id)
				print("Counter : ", counter, " --> ASCII: ",chr(counter))
				print("Payload : ", payload)
				print("HMAC to verify: ", str(digest_to_verify,"utf-8"))
				print("HMAC generated: ", digest_caluclated)

				# Comparing the locally calculated truncated HMAC with the one received in CAN Frame
				# If they are the same, the message is accepted and the message counter is incremented
				# Otherwise the message is rejected.
				if (digest_to_verify == bytearray(digest_caluclated,encoding='utf8')):
					print("Message:", str(payload,"utf-8"), "Accepted" )
					#f = open('./msgCounter','w')
					#f.write(str(file_read+1))
				else:
					print("Message Rejected")

# Shutting down  the CAN network interface
os.system('sudo ifconfig can0 down')
