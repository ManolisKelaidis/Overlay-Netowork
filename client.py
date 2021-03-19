import socket
import sys
import subprocess
import itertools
import re
from functions import *
from threading import Thread
import hashlib
import Crypto.Cipher
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
from Crypto import Random
from Crypto.PublicKey import RSA
import Queue
import time
#------------------------------------File Reading
if len(sys.argv) >= 6:
    if (sys.argv[1] == '-e') and (sys.argv[3] == '-r'):
        filename1 = sys.argv[2]
        filename2 = sys.argv[4]
        filename3 = sys.argv[5]


# filename = 'relays.txt'
with open(filename2) as file_object:
    lines = file_object.readlines()


relays = []
for a in lines:
    a = a.rstrip()
    relays.append(a.split(','))


with open(filename1) as file_object:
    lines = file_object.readlines()


endservers = []
for a in lines:
    a = a.rstrip()
    endservers.append(a)

with open(filename3) as file_object:
    lines = file_object.readlines()


links = []
for a in lines:
    a = a.rstrip()
    links.append(a.split(','))









print("\n\n\n\nChoose end server based on the alias\n\n\n\n")
for a in endservers:
    print a
#------------------------------------File Reading


while(1):
    while(1):
        answer = raw_input( "->")
        answer = answer.split()
        if (len(answer) == 3) and (answer[1].isdigit()):

            break
        print("Bad input retry")    

    print("Number of pings : " + answer[1])
   

    endserverAlias = ""
    endserverIP = ""
    for a in endservers:
       
        if a.find(answer[0]) > -1:
            b = a.split(',')
            endserverAlias = b[1]
            endserverIP = b[0]
            break

    numberofPings = answer[1]
    alias = answer[0]
    

    x = getIP(endservers, answer[0])
    rIP = getRelaysIP(relays)
    rNames = getRelaysName(relays)
    rPorts = getRelaysPort(relays)

    if(x[0] == 0):
        print("End server not found retry...")
        continue
    else:
        ip = x[1]
        break
    print("Bad input retry")    






keysize = 2048
(public, private) = newkeys(keysize)



threads = []
# print(type(ip))
#---------------------------DIRECT HOPS PING-----------------------#
que = Queue.Queue()
que2 = Queue.Queue()

t = Thread(target=ping, args=(ip, numberofPings, que, "Direct"))
t.start()
threads.append(t)
#t.join()

t3 = Thread(target=Traceroute, args=(ip, que2, "Direct"))
t3.start()
threads.append(t3)
#t3.join()
#---------------------------DIRECT HOPS PING-----------------------#


#-----------------------------PING TRACEROUTE RELAYS----------------------------------------------#
i = 0
while(i < len(relays)):
    t2 = Thread(target=ping, args=(rIP[i], numberofPings, que, rNames[i]))
    t2.start()
    threads.append(t2)
    #t2.join()
    i = i + 1

i = 0
while(i < len(relays)):
    t2 = Thread(target=Traceroute, args=(rIP[i], que2, rNames[i]))
    t2.start()
    threads.append(t2)
    #t2.join()
    i = i + 1

#-------------------------PING TRACEROUTE RELAYS-----------------------------------------------#

#-------------------------PING TRACEROUTE RELAYS->ENDSERVER------------------------------------#


ans = ip + " " + numberofPings
# print(ans)
i = 0
while(i < len(relays)):
    t2 = Thread(target=connectToRelay, args=(rIP[i], rPorts[i], ans, que, que2, rNames[i], public, private))
    t2.start()
    threads.append(t2)
    
    i=i + 1


for thread in threads:
    thread.join()

i=0
bestRes = bestResult(que,que2,answer[2],rNames)

if(bestRes=='EndServer Couldnt be reached'):
    while(i < len(relays)):
        t2 = Thread(target=terminateRelay, args=(rIP[i], rPorts[i]))
        t2.start()
        threads.append(t2)
        
        i=i + 1

    for thread in threads:
        thread.join()
    print("EndServer couldnt be reached,Shutting Down")

    time.sleep(1)
    print(3)
    time.sleep(1)
    print(2)
    time.sleep(1)
    print(1)
    exit(0)







ipDictionary = {}
portDictionary = {}
linksDictionary = {}
i = 0



while(i<(len(rNames)-1)):
    ipDictionary[rNames[i]] = rIP[i]
    portDictionary[rNames[i]] = rPorts[i]
    i+=1


dict2 = ipDictionary.copy()
dict3 = portDictionary.copy()
    
print("Best result ->"+ bestRes)
i=0
if(bestRes=='Direct'):
    while(i < len(relays)):
        t2 = Thread(target=terminateRelay, args=(rIP[i], rPorts[i]))
        t2.start()
        threads.append(t2)
        #t2.join()
        i=i + 1

    for thread in threads:
        thread.join()

else:
    del dict2[bestRes]
    del dict3[bestRes]
    for key in dict2:
        t2 = Thread(target=terminateRelay, args=(dict2[key], dict3[key]))
        t2.start()
        threads.append(t2)
    for thread in threads:
        thread.join()    







print("Time to download,Pick the link you want, with the respective number:")
i=1
for a in links:

    a = str(a)
    a = a.rstrip(']')
    a = a[2:(len(a)-1)]
    linksDictionary[str(i)] = a
    print(str(i) +" "+ a)
    i+= 1
while(1):
    answer = raw_input( "->")
    if(int(answer) >=1 and int(answer)<=8):
        break;
    else:
        print("Try again :")


ipDictionary['Direct'] = ''
portDictionary['Direct'] = 0
file  = download(bestRes,linksDictionary[answer],ipDictionary[bestRes],(int(portDictionary[bestRes])+1),public,private)



