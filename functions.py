
import sys
import subprocess
import socket
import os
import platform
import re
import Crypto.Cipher
from Crypto.Cipher import PKCS1_OAEP
import hashlib
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA512, SHA384, SHA256, SHA, MD5
from Crypto import Random
from base64 import b64encode, b64decode
from Crypto.PublicKey import RSA
import requests
import time




def Traceroute(host, que2, who):
    count = 0
    if(platform.system().lower() == "linux"):
        s = "traceroute " + "-w " + "100 " + host
        traceroute = subprocess.Popen(
            ["traceroute", host], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        for line in iter(traceroute.stdout.readline, b''):
            count = count + 1
            lastLine = line

         
        s = lastLine.find('* * *')
        if(s!=-1):
            ret = who+" "+str(100)
            que2.put(ret) 
            return ret
        count = count - 1
        output = who + " " + str(count)
        que2.put(output)

        return output

    else:
        traceroute = subprocess.Popen(
            ["tracert", '-w', '100', host], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        for line in iter(traceroute.stdout.readline, b''):
            count = count + 1

        count = count - 6
        output = who + " " + str(count)
        que2.put(output)
        return(output)

def bestResult(que1,que2,metric,names):
    names.append('Direct')
    dictionary = {}
    dictionary2 = {}

    for x in names:
    	dictionary2[x]=0
    for x in names:
        dictionary[x] = 0

       
    numberOfRelays = len(names)
    
    l1 = []
    l2 = []
    while not que1.empty():
    	result = que1.get()
    	
    	l1.append(result.split(' '))

    while not que2.empty():
        result = que2.get()
        
        l2.append(result.split(' '))	


        
    i=0
    while(i<numberOfRelays):
        name = names[i]
        j = 0
        while(j<len(l1)):
            if(name == 'Direct'):
                direct1 = l1[j][1]
            if(l1[j][0]==name):
                x = dictionary[name]
                dictionary[name] = x + float(l1[j][1])
            j += 1
        i+=1

    
    count = 0
    sum = 0
    for key in dictionary:
        count += 1
        sum += dictionary[key]

    mean =  sum/count
    
    print(dictionary)
    min = dictionary['Direct']
    name =  "Direct"
    for n in names:
    	if(dictionary[n]<min):
    		name = n;
    		min = dictionary[n]
    #print(name,min)


    i=0
    while(i<numberOfRelays):
        name2 = names[i]
        j = 0
        while(j<len(l2)):
            if(name2 == 'Direct'):
                direct2 = l2[j][1]
            if(l2[j][0]==name2):
                x = dictionary2[name2]
                dictionary2[name2] = x + float(l2[j][1])
            j += 1
        i+=1		

    print(dictionary2)
    min2 = dictionary2['Direct']
    name2 =  "Direct"
    for n in names:
    	if(dictionary2[n]<min2):
    		name2 = n;
    		min2 = dictionary2[n]



    count = 0
    sum = 0
    for key in dictionary2:
        count += 1
        sum += dictionary2[key]

    mean2 =  sum/count       
    #print(name2,min2)

    if(metric == 'Latency'):
        if(mean >= 100000):
            return "EndServer Couldnt be reached"   
        else:
    	   return name

    else:
        if(mean2>=100):
            print("Traceroute failed,Trying Ping criteria")
            return name

        else:
                
    	   return name2
   



def getFileType(link):

    index  = link.find("png")
    if(index!= -1):
        return "png"
    
    else:
    	return "gif"
    
    

def download(name,link,ip,port,public,private):
    
    notVerfied=1
    filetype = getFileType(link)
    if(name == "Direct"):
    	print(filetype)
        t0 = time.time()
        r = requests.get(link, stream = True)
        if(filetype == 'png'):
            with open("file.png","wb") as png:
                for chunk in r.iter_content(chunk_size=1024):
                    
                    if chunk: 
                        png.write(chunk)
        else:
            with open("file.gif","wb") as gif:
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk:
                        
                        gif.write(chunk)
        t1 = time.time() 
        print("Time needed to download = ",(t1-t0))               
        return 0                    
     
    else:
        
        port = int(port)
        command = link
        
    
        notVerfied = 1
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        s.connect((ip, port))
        
        pubText = public.exportKey('PEM')
        hash_object = hashlib.sha256(bytes(pubText))
        hex_dig = hash_object.hexdigest()
        message = pubText+hex_dig
        s.send(message)
    
    answer =s.recv(1024)
    while(notVerfied):
        #hash is 64 byte cause hex has 4 digits, 256/4 = 64
        keyTextRelay = answer[0:450]
        hashRelay = answer[450:514]
        hash_object = hashlib.sha256(bytes(keyTextRelay))
        hex_dig = hash_object.hexdigest() 
        if(hashRelay == hex_dig):
            print("Verification was success with "+ name)

            notVerfied=0
        else:
            s.send("Resend")

    hash_object = hashlib.sha256(bytes(command))
    hex_dig = hash_object.hexdigest()  





    signer = PKCS1_v1_5.new(private)
    digest = SHA256.new()
    digest.update(command)
    signature = signer.sign(digest)

    #signature = (sign(command, private))

    message = str(signature+command)
  
    pubKeyRelay = RSA.importKey(keyTextRelay)
   
    encryptHash1 = signature[0:210]
    encryptHash2 =signature[210:256]

    encryptHash = encryptHash1 + encryptHash2
    
    print(len(encryptHash))

    encryptMessage1 = (encrypt(encryptHash1,pubKeyRelay))
    encryptmessage2 = (encrypt(encryptHash2,pubKeyRelay))




    encryptmessage3 =  (encrypt(command,pubKeyRelay))

    encryptMessage = encryptMessage1 + encryptmessage2 + encryptmessage3
    
    time.sleep(2)
    s.send(encryptMessage)

    if(filetype == 'png'):
            a =  open("file.png","wb") 
    else:
            a =  open("file.gif","wb")




    answer = s.recv(1024)  
    message1 = answer[0:256]
    message2 = answer[256:512]
    message3 = answer[512:768]

    message1 = decrypt(message1,private)
    message2 = decrypt(message2,private)
    message3 = decrypt(message3,private)
    message = message1 + message2 + message3
    
    signature = message[0:256]
        


    message = message[256:(256+(len(message3)))]
    pubKeyRelay = RSA.importKey(keyTextRelay)



    signer = PKCS1_v1_5.new(pubKeyRelay)
    digest = SHA256.new()
    digest.update(message)
    ver = signer.verify(digest, signature)



    
    if(ver):
        print("Identity of relay Verified\n")
    
    print("Size of the file : "+ message)
     
    imageSize = int(message)
    bytesReceived = 0
    file=""
    t0 = time.time()
    while(bytesReceived< imageSize):

        answer = s.recv(1024)
       
        if not answer:
            break   


        message1 = answer[0:256]
        message2 = answer[256:512]
        message3 = answer[512:768]

        message1 = decrypt(message1,private)
        message2 = decrypt(message2,private)
        message3 = decrypt(message3,private)
        message = message1 + message2 + message3
        
        
        signature = message[0:256]
            


        message = message[256:(256+(len(message3)))]
        print(len(message))
        pubKeyRelay = RSA.importKey(keyTextRelay)
        bytesReceived = bytesReceived + len(message)

        print(bytesReceived)



        signer = PKCS1_v1_5.new(pubKeyRelay)
        digest = SHA256.new()
        digest.update(message)
        ver = signer.verify(digest, signature)

        
        if(ver):
            print("Identity of relay Verified")
        
        file =  file + message
        if(bytesReceived==imageSize):
            s.close()
        

    if(filetype == 'png'):
            a =  open("file10.png","wb") 
    else:
            a =  open("file10.gif","wb")     
    
    a.write(file.decode('base64'))
    t1 = time.time()
    timer = t1-t0
    print("Downloaded in : " ,timer)
    a.close()    
            

        



def Traceroute2(host, who):
    count = 0
    if(platform.system().lower() == "linux"):
        s = "traceroute " + "-w " + "100 " + host
        traceroute = subprocess.Popen(
            ["traceroute", host], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
       
        for line in iter(traceroute.stdout.readline, b''):
            count = count + 1
            lastLine =  line

        
        s = lastLine.find('* * *')
        if(s!=-1):
            ret = who+" "+str(100)
            
            return ret    
        count = count - 1
        output = who + " " + str(count)
        
        return output

    else:
        traceroute = subprocess.Popen(
            ["tracert", '-w', '100', host], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        for line in iter(traceroute.stdout.readline, b''):
            count = count + 1

        count = count - 6
        output = who + " " + str(count)
       
        return(output)


def ping(ip, numberofPings, que, who):

    if(platform.system().lower() == "linux"):
        command = "ping " + "-c " + numberofPings + " " + ip
        
        ping = subprocess.Popen(
            [command], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        
        output = ping.communicate()
        output = str(output)
       
        s = output.find("min/avg/max/mdev =")
        if(s==-1):
            avg = who+" "+str(100000)
            que.put(avg)
            return avg
        outputsize = len(output)

        output = output[s:outputsize]
        output = output[0:(len(output) - 9)]
        output = output[19:len(output)]
        i = 0
        avg = who + " "
        
        s = output.find("/")
        output = output[(s + 1):(len(output))]
        while(i < len(output)):
            if(output[i] != '/'):
                avg = avg + output[i]
                i = i + 1
            else:
                break

        output = avg
        

        que.put(output)
        return output
    else:
        ping = subprocess.Popen(["ping", ip, "-n", numberofPings], stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, shell=True)
        output = ping.communicate()
        output = str(output)
        s = output.find("Minimum = ")
        output = output[s:len(output)]
        output = output[0:(len(output) - 5)]
        output = output.split(",")
        
        que.put(output)
       
        return output


def ping2(ip, numberofPings, who):
    if(platform.system().lower() == "linux"):
        command = "ping " + "-c " + numberofPings + " " + ip
        print(platform.system().lower())
        ping = subprocess.Popen(
            [command], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        
        output = ping.communicate()
        output = str(output)
        
        s = output.find("min/avg/max/mdev =")
        if(s==-1):
            avg = who+" "+str(100000)
           
            return avg
        outputsize = len(output)

        output = output[s:outputsize]
        output = output[0:(len(output) - 9)]
        output = output[19:len(output)]
        i = 0
        avg = who + " "
       
        s = output.find("/")
        output = output[(s + 1):(len(output))]
        while(i < len(output)):
            if(output[i] != '/'):
                avg = avg + output[i]
                i = i + 1
            else:
                break

        output = avg

        return output
    else:
        ping = subprocess.Popen(["ping", ip, "-n", numberofPings], stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, shell=True)
        output = ping.communicate()
        output = str(output)
        s = output.find("Minimum = ")
        output = output[s:len(output)]
        output = output[0:(len(output) - 5)]
        output = output.split(",")
        
        return output


def getIP(endservers, alias):
    ret = []
    s = ""
    endservers = str(endservers)

    if(endservers.find("," + " " + alias) != -1):
        counter = endservers.find("," + " " + alias) - 1
        while(counter > 0):
            if(endservers[counter]) != "'":
                s += endservers[counter]
                counter = counter - 1
            else:
                break
        ip = s[::-1]
        found = 1
        ret.append(found)
        ret.append(ip)
    else:
       
        found = 0
        ret.append(found)
    return ret


def getRelaysName(relays):
    names = []
    counter = 0
    while(1):
        if(counter < len(relays)):
            names.append(relays[counter][0])
            counter = counter + 1
        else:
            break
    return names


def getRelaysIP(relays):
    ips = []
    counter = 0
    while(1):
        if(counter < len(relays)):
            ips.append(relays[counter][1])
            counter = counter + 1
        else:
            break

    return ips


def getRelaysPort(relays):
    ports = []
    counter = 0
    while(1):
        if(counter < len(relays)):
            ports.append(relays[counter][2])
            counter = counter + 1
        else:
            break

    return ports

def newkeys(keysize):
    random_generator = Random.new().read
    key = RSA.generate(keysize, random_generator)
    private, public = key, key.publickey()
    return public, private

def encrypt(message, pub_key):
    cipher = PKCS1_OAEP.new(pub_key)
    return cipher.encrypt(message)


def decrypt(ciphertext, priv_key):
    cipher = PKCS1_OAEP.new(priv_key)
    return cipher.decrypt(ciphertext)

def connectToRelay(host, port, command, que, que2, name, public, private):
 
    port = int(port)
    command = command + " " + name

    notVerfied = 1
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))

    pubText = public.exportKey('PEM')
    hash_object = hashlib.sha256(bytes(pubText))
    hex_dig = hash_object.hexdigest()
    print(len(hex_dig))
    message = pubText+hex_dig
    s.send(message)
    
    answer =s.recv(1024)
    while(notVerfied):
        #hash is 64 byte cause hex has 4 digits, 256/4 = 64
        keyTextRelay = answer[0:450]
        hashRelay = answer[450:514]
        hash_object = hashlib.sha256(bytes(keyTextRelay))
        hex_dig = hash_object.hexdigest() 
        if(hashRelay == hex_dig):
            print("Verification was success with "+ name)
            print("\n\n")
            #s.send("Success")
            #answer = s.recv(1024)
            notVerfied=0
        else:
            s.send("Resend")     
            
    


    hash_object = hashlib.sha256(bytes(command))
    hex_dig = hash_object.hexdigest() 


    signer = PKCS1_v1_5.new(private)
    digest = SHA256.new()
    digest.update(command)
    signature = signer.sign(digest)



    #signature = (sign(command, private))

    message = str(signature+command)
    
    pubKeyRelay = RSA.importKey(keyTextRelay)
  
    encryptHash1 = signature[0:210]
    encryptHash2 =signature[210:256]

    encryptHash = encryptHash1 + encryptHash2
    
    

    encryptMessage1 = (encrypt(encryptHash1,pubKeyRelay))
    encryptmessage2 = (encrypt(encryptHash2,pubKeyRelay))




    encryptmessage3 =  (encrypt(command,pubKeyRelay))

    encryptMessage = encryptMessage1 + encryptmessage2 + encryptmessage3
    
    time.sleep(2)
    s.send(encryptMessage)
    answer = s.recv(1024)


    message1 = answer[0:256]
    message2 = answer[256:512]
    message3 = answer[512:768]

    message1 = decrypt(message1,private)
    message2 = decrypt(message2,private)
    message3 = decrypt(message3,private)
    message = message1 + message2 + message3
    
    signature = message[0:256]
    mesLen = (len(message)-256)    
    message = message[256:(256+mesLen)]

    print(message)
    pubKeyRelay = RSA.importKey(keyTextRelay)


    signer = PKCS1_v1_5.new(pubKeyRelay)
    digest = SHA256.new()
    digest.update(message)
    ver = signer.verify(digest, signature)



    
    if(ver):
        print("Identity of "+name+ " relay Verified\n\n")
    
    


    s.close()
  

    message = message.replace(" ", "")
    i = 0
    s = name
    while(i < len(message)):
        if(message[i + 1] != 'r'):
            s = s + message[i + 1]
            i = i + 1
        else:
            break

    tmp = message[2:len(message)]
    index = tmp.find(name)
    tmp = tmp[index:len(tmp)]

    sub = tmp[0:2]
    tmp = sub + " " + tmp[2:len(tmp)]
    
    sub = s[0:2]
    s = sub + " " + s[3:len(s)]
    message = tmp + " " + s
    que.put(s)
    que2.put(tmp)
    return message


def list2string(list):
    s = ""
    i = 0
    while(i < len(list)):

        s = s + list[i] + " "
        i = i + 1

    return s

def terminateRelay(ip,port):
    port = int(port)
    port=((port)+1)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    s.connect((ip, port))
    s.send("Shutdown")
    #time.sleep(1)
    s.close()
    return 0

