import tkinter,pickle,socket,threading,time
import Utils
class Client:
    
    def __init__(self,Socket=None):
        self.IP,self.Port = Utils.Utils.Get_IP()
        if not Socket:
            self.Socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM )
            self.Socket.bind((self.IP,self.Port))
        else:
            self.Socket = Socket
        self.IsMatchMaking = True
        self.Root = tkinter.Tk()
        self.Game = Utils.Game(self)
        self.Name = "None"
        self.Colour = "red"
        self.OpponentColour = "blue"
        self.Server = None

    def SendToHost(self,data):
        self.Socket.sendto(pickle.dumps(data),(self.Server,self.Port))
            
    def ReplicateMove(self,Position):
        NewData = {
            "Command": "Choice",
            "Arguments": {
                "Name": self.Name,
                "Position": Position
            }
        }
        self.SendToHost(NewData)

    def Choice(self,ctx,data):
        if data['Name'] != self.Name:
            self.Game.MoveMade(data['Position'],self.OpponentColour)
    
    def Matchmaking(self,ctx,data):
        if self.IsMatchMaking:
            self.IsMatchMaking = False
            self.Server = ctx[0]
            print(f"Connected to host.")

    def Game_Create(self,ctx,data):
        self.Game.Clear()
        Player = data['Player']
        TheirName = data['Opponent']
        GameID = data['GameID']
        self.Game.Labels["Opponent"].config(text=f"Playing: {TheirName}")
        self.Game.Labels["Game"].config(text=f"GameID: {GameID}")
        if Player == 0:
            self.Game.CurrentPlayer = self.Colour
            self.Game.Labels["Turn"].config(text="Your Turn",bg=self.Colour)
        else:
            self.Game.CurrentPlayer = self.OpponentColour
            self.Game.Labels["Turn"].config(text="Their Turn",bg=self.OpponentColour)            
        self.Game.Board.pack(side = tkinter.TOP)
