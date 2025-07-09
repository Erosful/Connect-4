import socket,pickle,time,threading,uuid,random,string
import Utils

class Host:
    
    def __init__(self,Socket=None):
        self.Lobby = []
        self.Connections = []
        self.Games = {}
        self.IP,self.Port = Utils.Utils.Get_IP()
        if not Socket:
            self.Socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM )
            self.Socket.bind((self.IP,self.Port))
        else:
            self.Socket = Socket
        self.Broadcasting = threading.Thread(target=self.pinging) #as well as IMMEDIATELY handle incoming messages, so threads were my best option.

    def Get_Game_By_IP(self,IP):
        ID = None
        for k,v in self.Games.items(): #Iterate through all current open matches
            if not ID:
                for k2,v2 in v.items():
                    if v2["IP"] == IP:
                        ID = k
                        Player = k2
                    else:
                        Other_IP = v2["IP"]
        if not ID:
            return None
        return {
            "Game": ID,
            "Player": Player,
            "Other": Other_IP
            }
    
    def Send_Broadcast(self,data):
        BROADCAST_IP = ".".join(self.IP.split(".")[:3])+".255" #IP Address to send a "broadcast" - message to all IPs in this subnet.
        self.Socket.sendto(pickle.dumps(data),(BROADCAST_IP,self.Port))

    def pinging(self):
        data = {
            "Command": "Matchmaking",
            "Arguments": None
            }
        while 1:
            self.Send_Broadcast(data)
            time.sleep(3)

    def EndGame(self,ctx,data):
        Information = self.Get_Game_By_IP(ctx[0])
        if Information:
            del(self.Games[Information["Game"]])

    def Ping(self,ctx,data):
        if ctx not in self.Connections:
            self.Connections.append(ctx)
            data = {
                "Command": "IsHost",
                "Arguments": True
                }
            self.Socket.sendto(pickle.dumps(data),ctx)
            print(self.Connections)

    def Spectate(self,ctx,data):
        pass

    def Matchmaker(self,ctx,data):
        if ctx in self.Lobby:
            return
        self.Lobby.append([ctx[0],data]) #Appends the IP Address (of the computer sending a reply) to a list
        if len(self.Lobby)>=2:
            self.Create_Match(random.sample(self.Lobby,2))

    def Choice(self,ctx,data):
        Information = self.Get_Game_By_IP(ctx[0])
        NewData = {
            "Command": "Choice",
            "Arguments": data
            }
        self.Socket.sendto(pickle.dumps(NewData),((Information["Other"],self.Port)))
        self.Games[Information["Game"]][Information["Player"]]["Moves"].append(data)

    def Create_Match(self,Players):
        GameID = ("".join(random.choice(string.ascii_letters) for _ in range(5)))#Make random GameID - Simply for display purposes (seeing which two computers are in sync)
        while GameID in self.Games.keys():
            GameID = ("".join(random.choice(string.ascii_letters) for _ in range(5)))#Make random GameID - Simply for display purposes (seeing which two computers are in sync)
        self.Games[GameID] = {}
        for i,v in enumerate(Players): #Tells one that it"s P1, Tells the other it"s P2. -- Enumerate is essentially a for i in range and a for loop combined.
            self.Games[GameID][f"Player {i}"] = {
                "IP":v[0], #Address
                "Name":v[1], ##Player defined name
                "Moves":[]#Empty array to be used with the spectators
                }
            data = {
                "Command": "Game_Create",
                "Arguments": {
                    "Player": i,
                    "GameID": GameID,
                    "Opponent": Players[i-1][1]
                    }
                }
            self.Socket.sendto(pickle.dumps(data),(v[0],self.Port))#"v" is the IP address, whereas i is the index.
            self.Lobby.remove(v) #Remove the IP address from the matchmaking pool.
        
    def start(self):
        self.Broadcasting.start()
