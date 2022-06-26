import os
import can
import sys

os.system('sudo ip link set can0 type can bitrate 100000')
os.system('sudo ifconfig can0 up')

can0 = can.interface.Bus(channel = 'can0',bustype = 'socketcan_ctypes')

msg = can.Message(arbitration_id=ord('0'),data=bytearray(b'A\x40goode0'),extended_id=False)

can0.send(msg)
f = open('./msgCounter')
file_read = int(f.read())

f = open('./msgCounter','w')
f.write(str(file_read+1))

os.system('sudo ifconfig can0 down')
