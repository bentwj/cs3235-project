#!/usr/bin/python3
"""
CS3235 AY19/20 S1, Group 20
This script reads in a byte stream from a file and parses it for
Enhanced ShockBurst(ESB) packets with preamble = '10101010' and
address = '0xb91499bd09', with payload lengths of 0, 5, 10, 22 bytes

Prints out detected packets
"""

import sys

address_bytes = 5
payload_bits = 6
pid_bits = 2
crc_bytes = 2
valid_lengths = [0, 5*8, 10*8, 22*8]

kb_address = "0xb91499bd09" # pre-identified address

# returns hex representation ('0x??') of int val 0 to 255
def get_padded_hex_byte(val):
	return "{0:#0{1}x}".format(val, 4)

# converts 0x00 bytes to '0' characters and 0x01 bytes to '1' characters
def byte_to_bit(x):
	if x == b'\x01':
		return '1'
	elif x == b'\x00':
		return '0'

# checks if a window is a preamble of '10101010' (change to 85 if '01010101')
def is_preamble(val):
	return val == 170

def main(filename):
	packets = []
	window = 255 # to check for preamble
	with open(filename, "rb") as f:
		byte = f.read(1)
		while byte:
			window = window << 1
			window = window % 256
			if byte == b'\x01':
				window += 1
			if is_preamble(window):
				packet = ''
				pos = 0
				# address
				for i in range(address_bytes * 8):
					tmp = f.read(1)
					packet += byte_to_bit(tmp)
				address = "0x"
				for i in range(address_bytes):
					pos = i * 8
					address += get_padded_hex_byte(int(packet[pos:pos+8], 2))[2:]
				# check if the address matches pre-identified address (first 5 bytes)
				if not address == kb_address:
					window = 255
					continue
					
				# payload length
				pos = address_bytes * 8
				for i in range(6):
					tmp = f.read(1)
					packet += byte_to_bit(tmp)
				payload_len = int(packet[pos:pos+payload_bits], 2) * 8

				# PID
				pos = pos + payload_bits
				for i in range(2):
					tmp = f.read(1)
					packet += byte_to_bit(tmp)
				pid = packet[pos:pos+2]

				# ACK Flag
				pos = pos + pid_bits
				tmp = f.read(1)
				packet += byte_to_bit(tmp)
				flag = packet[pos:pos+1]

				# payload
				pos = pos + 1
				for i in range(payload_len):
					tmp = f.read(1)
					packet += byte_to_bit(tmp)
				payload = "0x"
				for i in range(payload_len // 8):
					payload += get_padded_hex_byte(int(packet[pos:pos+8], 2))[2:]
					pos = pos + 8

				# CRC
				for i in range(crc_bytes * 8):
					tmp = f.read(1)
					packet += byte_to_bit(tmp)
				crc = "0x"
				for i in range(crc_bytes):
					crc += get_padded_hex_byte(int(packet[pos:pos+8], 2))[2:]
					pos = pos + 8

				# output
				if payload_len in valid_lengths:
					print(f"\nAddress: {address} payload_len:{payload_len//8:02}",
						f"PID:{pid} no_ack:{flag} crc16:{crc}\npayload:{payload}")

				# reset window
				window = 255

			byte = f.read(1)


if __name__ == "__main__":
	if len(sys.argv) != 2:
		sys.exit()
	main(sys.argv[1])
