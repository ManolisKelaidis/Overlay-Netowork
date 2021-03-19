import socket
import functions
from functions import *
from functions import list2string
from functions import Traceroute2
#from functions import importKey
from functions import newkeys
from Crypto.Cipher import PKCS1_OAEP
import hashlib
import requests
import time
import base64
import sys
from base64 import *
HOST = ''


hostname = socket.gethostname()
ip = socket.gethostbyname(hostname)
print("MY ip is : "+ip)


if len(sys.argv) >= 1 :
	
	if (sys.argv[1] == 'relay_nodes.txt'):
		filename = sys.argv[1]
		


with open(filename) as file_object:
    lines = file_object.readlines()


for a in lines:
    a = a.rstrip()
 
    start = a.find(ip)
    if(start!= -1):
    	a = a[start:len(a)]
    	start = a.find(',')
    	a = a[(start+1):len(a)]
    	break;


print("Im listening to port : " + a)
PORT = int(a)

s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
flag = 1
s.bind((HOST, PORT))
s.listen(1)
(public, private) = newkeys(2048)
conn, addr = s.accept()  # returbs list with 2 eleemnt
notVerfied = 1
print 'Connected by Client with Port', addr
while True:
	if(flag==4):
		print("Time to shut down....")
		time.sleep(1)
		print(3)
		time.sleep(1)
		print(2)
		time.sleep(1)
		print(1)
		conn.close()
		s.close()
		break;

	

	if flag == 1:
		data = conn.recv(1024)
		#hash is 64 byte cause hex has 4 digits, 256/4 = 64
		while(notVerfied):
		    pubText2 = public.exportKey('PEM')
		    hash_object = hashlib.sha256(bytes(pubText2))
		    hex_dig = hash_object.hexdigest()
		    message = pubText2+hex_dig
		    conn.send(message)
		    
		    keyClientText = data[0:450]
		    hashClient = data[450:514]
		    hash_object = hashlib.sha256(bytes(keyClientText))
		    hex_dig = hash_object.hexdigest()
		    if(hashClient == hex_dig):
		    	print("Verfication with client was Success\n\n")
		    	notVerfied = 0
		    
		    else:
		    	print("Resend the message")		 
		    	conn.send("Resend")

		flag += 1


	elif(flag==2):

		data = conn.recv(1024)
		message1 = data[0:256]
		message2 = data[256:512]
		message3 = data[512:768]

		message1 = decrypt(message1,private)
		message2 = decrypt(message2,private)
		message3 = decrypt(message3,private)
		message = message1 + message2 + message3
		
		signature = message[0:256]
		
		
		mesLen = (len(message)-256)
		message = message[256:(256+mesLen)]
		pubKeyClient = RSA.importKey(keyClientText)





		signer = PKCS1_v1_5.new(pubKeyClient)
		digest = SHA256.new()
		digest.update(message)
		verify1 = signer.verify(digest, signature)


		
		if(verify1):
			print("Identity of client Verified")
		print("Clients message " + message)

		message = message.split()
		result = ping2(message[0], message[1], message[2])
		result2 = Traceroute2(message[0], message[2])

		result = result + " " + result2
		result = list2string(result)

		print("My results : "+ result)
		hash_object = hashlib.sha256(bytes(result))
		hex_dig = hash_object.hexdigest()  


		signer = PKCS1_v1_5.new(private)
		digest = SHA256.new()
		digest.update(result)
		signature = signer.sign(digest)




		#signature = (sign(result, private))
		pubKeyClient = RSA.importKey(keyClientText)
		
		encryptHash1 = signature[0:210]
		encryptHash2 =signature[210:256]

		encryptHash = encryptHash1 + encryptHash2
	

		encryptMessage1 = (encrypt(encryptHash1,pubKeyClient))
		encryptmessage2 = (encrypt(encryptHash2,pubKeyClient))

		encryptmessage3 =  (encrypt(result,pubKeyClient))

		encryptMessage = encryptMessage1 + encryptmessage2 + encryptmessage3
		

		conn.send(encryptMessage)
		print("Connection termimated...")
		conn.close()
		s.close()
		flag += 1
	elif(flag==3):

		s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		
		s.bind((HOST, PORT+1))
		print("port binded")
		s.listen(1)
		print("listening")
		(public, private) = newkeys(2048)
		conn, addr = s.accept()
		print("conn accept")
		data = conn.recv(1024)
		if(data=='Shutdown'):
			
			print("Time to shut down....")
			time.sleep(1)
			print(3)
			time.sleep(1)
			print(2)
			time.sleep(1)
			print(1)
			s.close()
			conn.close()
			exit(1)
		if not data:
			break
		print 'Connected by Client with Port', addr
		
		pubText2 = public.exportKey('PEM')
		hash_object = hashlib.sha256(bytes(pubText2))
		hex_dig = hash_object.hexdigest()
		message = pubText2+hex_dig
		conn.send(message)
		#hash is 64 byte cause hex has 4 digits, 256/4 = 64
		keyClientText = data[0:450]
		hashClient = data[450:514]
		hash_object = hashlib.sha256(bytes(keyClientText))
		hex_dig = hash_object.hexdigest()
		if(hashClient == hex_dig):
		    print("Verification was success")
		  
		    notVerfied = 0
		    	
		else:
		    print("Resend the message")		 
		    conn.send("Resend")


		data = conn.recv(1024)
		message1 = data[0:256]
		message2 = data[256:512]
		message3 = data[512:768]

		message1 = decrypt(message1,private)
		message2 = decrypt(message2,private)
		message3 = decrypt(message3,private)
		message = message1 + message2 + message3
		
		signature = message[0:256]
		
		
		mesLen = (len(message)-256)
		message = message[256:(256+mesLen)]
		pubKeyClient = RSA.importKey(keyClientText)




		signer = PKCS1_v1_5.new(pubKeyClient)
		digest = SHA256.new()
		digest.update(message)
		verify2 = signer.verify(digest, signature)


		
		if(verify2):
			print("Identity of client Verified")
		print(verify2)
		print(message)

		filetype = getFileType(message)
		

		r = requests.get(message, stream = True)
		if(filetype == 'png'):
			with open("file.png","wb") as png:
				filename = "file.png"
				for chunk in r.iter_content(chunk_size=1024):
					print(type(chunk))
					if chunk: 
						png.write(chunk)
		else:
			with open("file.gif","wb") as gif:
				filename = "file.gif"
				for chunk in r.iter_content(chunk_size=1024):
					if chunk:
						print(type(chunk))
						gif.write(chunk)




		
		with open(filename, "rb") as imageFile:
				string = base64.b64encode(imageFile.read())
				#print str
		print("FileSize = "+str(len(string)))		
		imageSize= str(len(string))
		result = imageSize
		hash_object = hashlib.sha256(bytes(result))
		hex_dig = hash_object.hexdigest() 

		signer = PKCS1_v1_5.new(private)
		digest = SHA256.new()
		digest.update(result)
		signature =  signer.sign(digest)

		pubKeyClient = RSA.importKey(keyClientText)
		encryptHash1 = signature[0:210]
		encryptHash2 =signature[210:256]
		encryptHash = encryptHash1 + encryptHash2
		#print(len(encryptHash))
		encryptMessage1 = (encrypt(encryptHash1,pubKeyClient))
		encryptmessage2 = (encrypt(encryptHash2,pubKeyClient))
		encryptmessage3 =  (encrypt(result,pubKeyClient))

		encryptMessage = encryptMessage1 + encryptmessage2 + encryptmessage3
	
		conn.send(encryptMessage)
		base = len(string)
		sendBytes = 0
		flag2 = 0
		while(sendBytes!=len(string)):
			if(base>=200):
				result = string[sendBytes:sendBytes+200]
				hash_object = hashlib.sha256(bytes(result))
				hex_dig = hash_object.hexdigest() 





				signer = PKCS1_v1_5.new(private)
				digest = SHA256.new()
				digest.update(result)
				signature =  signer.sign(digest)


				pubKeyClient = RSA.importKey(keyClientText)
				encryptHash1 = signature[0:210]
				encryptHash2 =signature[210:256]
				encryptHash = encryptHash1 + encryptHash2
				#print(len(encryptHash))
				encryptMessage1 = (encrypt(encryptHash1,pubKeyClient))
				encryptmessage2 = (encrypt(encryptHash2,pubKeyClient))
				encryptmessage3 =  (encrypt(result,pubKeyClient))
				encryptMessage = encryptMessage1 + encryptmessage2 + encryptmessage3
				print("Chunk of 200Bytes was sent")
				time.sleep(0.05)
				conn.send(encryptMessage)
				base -= 200
				sendBytes +=200
			else:
				if(flag2==1):
					conn.close()
					s.close()
					print("FIle transfer complete")
					break;
				result = string[sendBytes:len(string)]	
				hash_object = hashlib.sha256(bytes(result))
				hex_dig = hash_object.hexdigest() 



				signer = PKCS1_v1_5.new(private)
				digest = SHA256.new()
				digest.update(result)
				signature =  signer.sign(digest)

 
				pubKeyClient = RSA.importKey(keyClientText)
				encryptHash1 = signature[0:210]
				encryptHash2 =signature[210:256]
				encryptHash = encryptHash1 + encryptHash2
				#print(len(encryptHash))
				encryptMessage1 = (encrypt(encryptHash1,pubKeyClient))
				encryptmessage2 = (encrypt(encryptHash2,pubKeyClient))
				encryptmessage3 =  (encrypt(result,pubKeyClient))
				encryptMessage = encryptMessage1 + encryptmessage2 + encryptmessage3
				print("Chunk of " +str(200)+" "+"Bytes was sent")
				conn.send(encryptMessage)
				base -= 200
				sendBytes +=200
				flag2+=1

		flag+=1
	