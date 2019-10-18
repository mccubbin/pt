from Crypto.Cipher import DES
from django.conf import settings

"""
Encryption
~~~~~~
Originated from http://blog.suminb.com/archives/558
Also from https://github.com/suminb/base62/blob/develop/base62.py
"""
class Encryption:
	def __init__(self):
		pass

	@staticmethod
	def encrypt(text):

		# get secret key and give it to DES
		key = settings.ENCRKEY.encode("utf-8")
		des = DES.new(key, DES.MODE_ECB)

		# pad text before processing, ValueError: Data must be aligned to block boundary in ECB mode
		padded_text = Encryption.pad(text)

		# 1. encrypt text into bytes
		encrypted_text = des.encrypt(padded_text.encode("utf-8"))

		# no longer using base64
		#encrypted_text = base64.urlsafe_b64encode(encrypted_text).decode()
		#print (base64.urlsafe_b64encode(encrypted_text).decode())

		# 2. bytes to int
		encrypted_text = Encryption.bytes_to_int(encrypted_text)

		# 3. int to base62
		encrypted_text = BtSchemes.encode(encrypted_text)

		return encrypted_text


	@staticmethod
	def decrypt(encrypted_text):

		# get secret key and give it to DES
		key = settings.ENCRKEY.encode("utf-8")
		des = DES.new(key, DES.MODE_ECB)

		# what does this do?
		#encrypted_text = encrypted_text.encode("utf-8")

		# no longer using base64
		#encrypted_text = base64.urlsafe_b64decode(encrypted_text)

		# 1. base62 to int
		encrypted_text = BtSchemes.decode(encrypted_text)

		# 2. int to bytes
		encrypted_text = Encryption.int_to_bytes(encrypted_text)

		# 3. decrypt bytes to text
		decrypted_text = des.decrypt(encrypted_text).decode()

		# strip padding
		decrypted_text = decrypted_text.rstrip()

		return decrypted_text


	@staticmethod
	def bytes_to_int(s, byteorder='big', signed=False):
		"""Converts a byte array to an integer value.
		Python 3 comes with a built-in function to do this, but we would like to
		keep our code Python 2 compatible.
		"""

		try:
			return int.from_bytes(s, byteorder, signed=signed)
		except AttributeError:
			# For Python 2.x
			if byteorder != 'big' or signed:
				raise NotImplementedError()

			# NOTE: This won't work if a generator is given
			n = len(s)
			ds = (x << (8 * (n - 1 - i)) for i, x in enumerate(bytearray(s)))

			return sum(ds)


	@staticmethod
	def int_to_bytes(num):
		buf = bytearray()
		while num > 0:
			buf.append(num & 0xff)
			num //= 256
		buf.reverse()
		return buf


	@staticmethod
	def pad(text):
		while len(text) % 8 != 0:
			text += ' '
		return text


#promorencoded = base64.urlsafe_b64encode(emailpromor.encode())
#Upromor.email = Upromor.email.decode('utf-8')

class BtSchemes:

	BASE56 = "ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnpqrstuvwxyz23456789"
	BASE62 = "0ABCDEFGHIJKLMNOPQRSTUVWXYZ1abcdefghijklmnopqrstuvwxyz23456789"

	# Encode a positive number in Base X
	# Arguments:
	# - `num`: The number to encode
	# - `alphabet`: The alphabet to use for encoding
	@staticmethod
	def encode(num, alphabet=BASE62):

		if num == 0:
			return alphabet[0]
		arr = []
		base = len(alphabet)
		while num:
			num, rem = divmod(num, base)
			arr.append(alphabet[rem])
		arr.reverse()
		return ''.join(arr)

	# Decode a Base X encoded string into the number
	# Arguments:
	# - `string`: The encoded string
	# - `alphabet`: The alphabet to use for encoding
	@staticmethod
	def decode(string, alphabet=BASE62):

		base = len(alphabet)
		strlen = len(string)
		num = 0

		idx = 0
		for char in string:
			power = (strlen - (idx + 1))
			num += alphabet.index(char) * (base ** power)
			idx += 1

		return num







