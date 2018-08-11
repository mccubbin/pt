from Crypto.Cipher import DES
from django.conf import settings
import base64

class Encryption:
	def __init__(self):
		pass

	@staticmethod
	def encrypt(text):
		key = settings.ENCRKEY.encode("utf-8")
		padded_text = Encryption.pad(text)
		des = DES.new(key, DES.MODE_ECB)

		encrypted_text = des.encrypt(padded_text.encode("utf-8"))
		encrypted_text = base64.urlsafe_b64encode(encrypted_text).decode()

		return encrypted_text


	@staticmethod
	def decrypt(encrypted_text):
		key = settings.ENCRKEY.encode("utf-8")
		des = DES.new(key, DES.MODE_ECB)

		encrypted_text = encrypted_text.encode("utf-8")
		encrypted_text = base64.urlsafe_b64decode(encrypted_text)
		decrypted_text = des.decrypt(encrypted_text).decode()

		decrypted_text = decrypted_text.rstrip()

		return decrypted_text


	@staticmethod
	def pad(text):
		while len(text) % 8 != 0:
			text += ' '
		return text


#promerencoded = base64.urlsafe_b64encode(emailpromer.encode())
#Upromer.email = Upromer.email.decode('utf-8')

