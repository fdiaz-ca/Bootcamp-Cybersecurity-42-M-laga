import argparse, re, hashlib, hmac, struct, time, os
from cryptography.fernet import Fernet

parser = argparse.ArgumentParser(description='Process to create a TOTP (Time-based One Time Password).')
parser.add_argument("-g", dest="hexfile", help="Get file to make a key-file.", type=str)
parser.add_argument("-k", dest="keyfile", help="Use Key-file to generate TOTP.", type=str)
params = parser.parse_args()

KEY_FILE = "pak.key"

if params.hexfile:
	# comprobar que es valido
	with open(params.hexfile, "r") as f:
		hex_pression = f.read()
	
	if not re.match(r'^[0-9a-fA-F]{64,}$', hex_pression):
		print("error: key must be 64 hexadecimal characters.")
		exit (1)
	
	# key generation y cifrarlo 
	f_key = Fernet.generate_key()
	with open(KEY_FILE, "wb") as f:
		f.write(f_key)
	fernet = Fernet(f_key)
	encripted_hex = fernet.encrypt(hex_pression.encode())
	
	# guardarlo como ft_otp.key	
	with open("ft_otp.key", "w") as f:
		f.write(encripted_hex.decode())
	print("Key was successfully saved in ft_otp.key.")
	

elif params.keyfile:
	# Leer el ft_otp.key
	if params.keyfile != "ft_otp.key":
		print("error: file must be ft_otp.key")
		exit (1)

	with open(params.keyfile, "rb") as f:
		encripted_hex = f.read()
	
	# Descifrarlo (y llamarlo 'hex_pression')
	with open(KEY_FILE, "rb") as f:
		f_key = f.read()
	fernet = Fernet(f_key)
	hex_pression = fernet.decrypt(encripted_hex).decode()
	# print(f.decrypt(token).decode())

	# Generar la TOTP 
	def get_hotp(hex_pression, the_time):
		key = bytes.fromhex(hex_pression)
		# decoding our key
		msg = struct.pack(">Q", the_time)
		# conversions between Python values and C structs represente
		h = hmac.new(key, msg, hashlib.sha1).digest()
		o = h[19] & 15
		# Generate a hash using both of these. Hashing algorithm is HMAC
		h = (struct.unpack(">I", h[o:o+4])[0] & 0x7fffffff) % 1000000
		# unpacking
		return h

	def get_totp(hex_pression):
		# ensuring to give the same otp for 30 seconds
		thekey =str(get_hotp(hex_pression,the_time=int(time.time())//30))
		# adding 0 in the beginning till OTP has 6 digits
		while len(thekey) < 6:
				thekey +='0'
		return thekey

	# Devolverla
	print("Shared seed: ", hex_pression)
	print("TOTP password: ", get_totp(hex_pression))
