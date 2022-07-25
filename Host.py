import socket,threading,random,time,string
List = [] #Im going to use an Array to store incoming connections as a pool
ActiveGames = [] #And then store matches in a 2D array, where I can forward messages to the other player
AliveConnections = []
PORT_NUMBER = 65000
SIZE = 1024

x = socket.getfqdn()
MY_IP = socket.gethostbyname_ex(x)[2][0] #Code to get my local IP address - I don't want to have to manually input it everytime I change computers

print("Running on IP {}:{}\n".format(MY_IP, PORT_NUMBER))
mySocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM )
BROADCAST_IP = (".".join(MY_IP.split(".")[:3])+".255") #IP Address to send a "broadcast" - message to all IPs in this subnet.
mySocket.bind((MY_IP,PORT_NUMBER))

def broadcasting(): #Constantly sends out the broadcast so that new computers can be added to the game seamlessly
    while 1:
        print("Sending out Broadcast")
        mySocket.sendto("Anybody alive!?".encode('utf-8'),((BROADCAST_IP,PORT_NUMBER)))
        time.sleep(3)

def handling():
    global AliveConnections
    while 1:
        try:
            (data,addr) = mySocket.recvfrom(SIZE)#
            if "pong" in str(data):
                AliveConnections.append(addr[0])
            elif "recieving connection" in str(data): #This is the established reply to the broadcast.
                if addr[0] in List:
                    continue
                List.append([addr[0],str(data)[24:len(str(data))-1]]) #Appends the IP Address (of the computer sending a reply) to a list
                print(List)
                if len(List)>=2:
                    x = random.sample(List,2) #Randomly selects two IP addresses.
                    GameID = (''.join(random.choice(string.ascii_letters) for _ in range(5)))#Make random GameID - Simply for display purposes (seeing which two computers are in sync)
                    for i,v in enumerate(x): #Tells one that it's P1, Tells the other it's P2. -- Enumerate is essentially a for i in range and a for loop combined.
                        mySocket.sendto(f"Player {i}! GameID: {GameID} {x[i-1][1]}".encode('utf-8'),((v[0],PORT_NUMBER)))#"v" is the IP address, whereas i is the index.
                        List.remove(v) #Remove the IP address from the matchmaking pool.
                    ActiveGames.append([x[0][0],x[1][0]])#Append the paired IPs intoa a 2D Array - end result might be [['112.53.34.16','112.53.34.20'],['112.53.34.190','112.53.34.54']]
                    print(ActiveGames)
            else: #Its sent something that ISNT the established reply
                for x in ActiveGames: #Iterate through all current open matches
                    if addr[0] in x: #See which one the incoming message is from
                        for x2 in x: #Iterate through that match -- NOTE: I might make this more efficient as I dont need a for loop for a two element array.
                            if x2 != addr[0]: #Find the address in the match that ISNT the incoming message.
                                mySocket.sendto(data,((x2,PORT_NUMBER))) #Send the data to that address (The host simply acts as the middleman in this regard)
                                break
        except:
            pass

def checkconnections():
    global AliveConnections
    time.sleep(30)
    while 1:
        AliveConnections = []
        mySocket.sendto("ping!".encode('utf-8'),((BROADCAST_IP,PORT_NUMBER)))
        time.sleep(5) #wait 5 seconds.
        ListOfAddressess = []
        print(ActiveGames)
        print(AliveConnections)
        for x in ActiveGames:
            for i in x:
                ListOfAddressess.append(i)
        for x in ActiveGames:
            for x2 in x:
                if x2 not in AliveConnections:
                    print(x)
                    print(x2)
                    ActiveGames.remove(x)
        time.sleep(10)

x = threading.Thread(target=broadcasting) #I need both of these codes running at once, since I need to broadcast constantly,
y = threading.Thread(target=handling) #as well as IMMEDIATELY handle incoming messages, so threads were my best option.
z = threading.Thread(target=checkconnections)
x.start()
y.start()
z.start()
