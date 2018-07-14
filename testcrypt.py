from Crypto.Cipher import DES
import base64

def pad(text):
	while len(text) % 8 != 0:
		text += ' '
	return text

key = '9mBjx1oW'.encode("utf-8")
des = DES.new(key, DES.MODE_ECB)
text = 'phil@email.com'
padded_text = pad(text)

encrypted_text = des.encrypt(padded_text.encode("utf-8"))
encrypted_text = base64.urlsafe_b64encode(encrypted_text).decode()

print(encrypted_text)

# key = settings.ENCRKEY.encode("utf-8")
# des = DES.new(key, DES.MODE_ECB)
# encrypted_text = encrypted_text.encode("utf-8")
# assert False, decrypted_text

encrypted_text = encrypted_text.encode("utf-8")
decoded_text = base64.urlsafe_b64decode(encrypted_text)
decrypted_text = des.decrypt(decoded_text).decode()

#decrypted_text = base64.urlsafe_b64decode(decrypted_text)

print(decrypted_text)


