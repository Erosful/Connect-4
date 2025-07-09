import json,datetime,tkinter,socket,threading,pickle,json

class Game:
    
    def __init__(self,Client):
        self.Client = Client
        self.Background = "light gray"
        self.Client.Root.geometry("1500x900")
        self.Board = self.SetupBoard()
        self.WaitingScreen = self.Loading()
        self.CurrentPlayer = ""
        self.LoginMenu().pack()
        
    def ColourCheck(self,Colour,Pos1,Pos2):
        Win = False
        Array = {}
        for x in ["Vertical","Horizontal","Ldiag","Rdiag"]:
            Array[x] = [self.FlatBoard[Pos1][Pos2]]
        for i in range(1,4):
            try:
                if self.FlatBoard[Pos1][Pos2+i].cget("bg") == Colour:
                    Array["Vertical"].append(self.FlatBoard[Pos1][Pos2+i])
            except:
                pass
            try:
                if self.FlatBoard[Pos1+i][Pos2].cget("bg") == Colour:
                    Array["Horizontal"].append(self.FlatBoard[Pos1+i][Pos2])
            except:
                pass
            try:
                if self.FlatBoard[Pos1-i][Pos2+i].cget("bg") == Colour and (Pos1-i)>=0:
                    Array["Ldiag"].append(self.FlatBoard[Pos1-i][Pos2+i])
            except:
                pass
            try:
                if self.FlatBoard[Pos1+i][Pos2+i].cget("bg") == Colour:
                    Array["Rdiag"].append(self.FlatBoard[Pos1+i][Pos2+i])
            except:
                pass
        for k,v in Array.items():
            if len(v) >= 4:
                for x in v:
                    x.config(bg = "yellow")
        if any(len(x) >= 4 for x in Array.values()):
            Win = True
        return Win

    def ResetBoard(self):
        self.Clear()
        self.Board = self.SetupBoard()
        NewData = {
            "Command": "EndGame",
            "Arguments": None
        }
        self.Client.SendToHost(NewData)
        NewData = {
            "Command": "Matchmaker",
            "Arguments": self.Client.Name
            }
        self.Client.SendToHost(NewData)
        self.WaitingScreen.pack()

    def Checkwin(self,Colour):
        def Looping(): #Wrapped as a nested function so that I can exit both loops at once.
            Draw = True
            for i in range(len(self.FlatBoard)):
                for i2 in range(len(self.FlatBoard[i])):
                    if self.FlatBoard[i][i2].cget("bg") == self.Background:
                        Draw = False
                    if self.FlatBoard[i][i2].cget("bg") == Colour:
                        Win = self.ColourCheck(Colour,i,i2)
                        if Win:
                            return True,Draw
            return False,Draw
        Win,Draw = Looping()
        if Draw or Win:
            if Win:
                if self.Client.Colour == Colour:
                    text = "You Win!"
                else:
                    text = "You Lose!"
            else:
                text = "Draw!"
            self.Labels["Turn"].config(text = text,bg = "green")
            for b in self.Buttons:
                b.config(bg = "black")
            self.ResetButton().pack()

    def MoveMade(self,Position,Colour):
        if Colour != self.CurrentPlayer:
            return
        Column = self.Board.winfo_children()[Position].winfo_children()
        if Column[0].cget("bg") != "Green" and Colour == self.Client.Colour:
            return
        for i in Column:
            if i.cget("bg") == self.Background and isinstance(i,tkinter.Label):
                i.config(bg=Colour)
                break
        if Column[-1].cget("bg") != self.Background:
            Column[0].config(bg = "Black") #Make button black
        if Colour == self.Client.Colour:
            self.Client.ReplicateMove(Position)
            self.CurrentPlayer = self.Client.OpponentColour
            self.Labels["Turn"].config(text="Their Turn",bg=self.Client.OpponentColour)     
        else:
            self.CurrentPlayer = self.Client.Colour
            self.Labels["Turn"].config(text="Your Turn",bg=self.Client.Colour)
        self.Checkwin(Colour)

    def ResetButton(self):
        x = tkinter.Frame(self.Client.Root)
        Reset = tkinter.Button(x, bg = "red", height = 4, width = 8, text = ('Lobby'),font = ("Ariel",8, "bold"), command = lambda x = self: x.ResetBoard())
        Reset.pack()
        return x

    def SetupBoard(self):
        Rows = 7
        Columns = 6
        self.FlatBoard = []
        self.Buttons = []
        board = tkinter.Frame(self.Client.Root)
        Top = tkinter.Frame(board)
        Top.pack(side = tkinter.TOP)
        Playing = tkinter.Label(Top,font= ("Courier",20,"bold"),text = f"Playing: Nobody")
        GameID = tkinter.Label(Top,font = ("Courier",16, "bold"), text = (f"Game ID: Null"))
        TurnText = tkinter.Label(Top,font = ("Courier",20, "bold"), text = (f"Nobody's Turn"), bg = "white")
        self.Labels = {
            "Turn": TurnText,
            "Opponent": Playing,
            "Game": GameID
            }
        TurnText.pack() 
        Playing.pack()
        GameID.pack()
        for i in range(Columns):
            L = []
            frm = tkinter.Frame(board)
            frm.pack(side = tkinter.LEFT)
            btn = tkinter.Button(frm, bg = "green", height = 4, width = 8, font = ("Ariel",8, "bold"), command = lambda pos = (i+1): self.MoveMade(pos,self.Client.Colour))
            btn.pack(side = tkinter.BOTTOM)
            self.Buttons.append(btn)
            for j in range(Rows):
                Lbl = tkinter.Label(frm, bg = self.Background, height = 4, width = 8, font = ("Ariel",8, "bold"))
                Lbl.pack(side = tkinter.BOTTOM,pady=1)
                L.append(Lbl)
            self.FlatBoard.append(L)
        return board

    def LoginMenu(self):
        def EnterUsername():
            Name = (TextBox.get())
            if Name == "":
                return
            TextBox.delete(0, 'end')
            self.Client.Name = Name
            NewData = {
                "Command": "Matchmaker",
                "Arguments": self.Client.Name
            }
            self.Client.SendToHost(NewData)
            self.Clear()
            self.WaitingScreen.pack()
        Screen = tkinter.Frame(self.Client.Root)
        fill = tkinter.Frame(Screen,width=1900,height=300,padx=0,pady=0)
        fill.pack(side = tkinter.TOP)
        fill.pack_propagate(0)
        frame1 = tkinter.Frame(Screen,width=1900,height=50,padx=0,pady=0)
        frame1.pack(side = tkinter.TOP)
        frame1.pack_propagate(0)
        displayText = tkinter.Label(frame1,width = 1000, height = 1,text = "Please enter username:",font = "lato, 30")
        displayText.pack(side = tkinter.TOP)
        displayText.pack_propagate(0)
        frame2 = tkinter.Frame(Screen,width=600,height=100,padx=0,pady=0)
        frame2.pack(side = tkinter.TOP)
        frame2.pack_propagate(0)
        TextBox = tkinter.Entry(frame2,width = 25,font ="lato, 21")
        TextBox.pack(side = tkinter.LEFT)
        TextBox.pack_propagate(0)
        fill2 = tkinter.Frame(frame2,width = 8, height = 1)
        fill2.pack(side = tkinter.LEFT)
        fill2.pack_propagate(0)
        EntryButton = tkinter.Button(frame2, width = 20, height = 2, text = ('Enter'), font = "lato,25", command = EnterUsername, bg = "lavender")
        EntryButton.pack(side = tkinter.LEFT)
        EntryButton.pack_propagate(0)
        return Screen
    
    def Loading(self):
        Screen = tkinter.Frame(self.Client.Root)
        Label = tkinter.Label(Screen, text = "WAITING...", font=('Lato',50), height = 10, width = 400)
        Label.pack(side = tkinter.TOP)
        return Screen

    def Clear(self):
        for child in self.Client.Root.winfo_children():
            if isinstance(child, tkinter.Frame):
                child.pack_forget()

class Handler:

    def __init__(self,Class):
        self.Socket = Class.Socket
        self.IP = Class.IP
        self.Port = Class.Port
        self.Type = [Class]
        self.Thread = threading.Thread(target=self.handling_thread)

    def Add_Listener(self,Class):
        self.Type.append(Class)

    def begin(self):
        self.Thread.start()

    def handling_thread(self):
        while True:
            try:
                (data,addr) = self.Socket.recvfrom(1024)
                try:
                    data = pickle.loads(data)
                except Exception as e:
                    print(e)
                    continue
                print(data)
                for h in self.Type: #Allows for both client and host commands to be iterated through
                    if hasattr(h,data["Command"]):
                        function = getattr(h, data["Command"]) #Get the subroutine named after the command sent to us
                        function(addr, data["Arguments"])
            except Exception as e:
                print(e)
        
class Player: #Both Player and Database classes are sadly decommed since I can't store the database properly.

    def __init__(self,info):
        for k,v in info.items():
            setattr(self,k,v)

    def UpdateScore(self,Score):
        if Score > 0:
            self.Wins += 1
        elif Score == 0:
            self.Draws += 1
        else:
            self.Losses += 1
            
class Database:

    def __init__(self):
        self.URL = "https://NEA-API.erosful.repl.co"
        pass
    
    def Login(Username,Password):
        pass
        return Player(Data)

    def Logout(self,Player):
        self.WriteScore(Player)
        
        pass
        
    def WriteScore(self,Player):
        Data = {
            "Player": Player.ID,
            "Data": {
                "Wins": Player.Wins,
                "Draws": Player.Draws,
                "Losses": Player.Losses
            }
        }
        requests.post(f"{self.URL}/database",json=Data)

    def GetScore(self,Player):
        x = requests.get(f"{self.URL}/player",params={"Player":Player.ID})

class Utils: #Where I'm putting misc subroutines which are called by both Host and Client - DRY
    def Get_IP():
        Port = 43000 #Change this constant to change on both files
        x = socket.getfqdn()
        return socket.gethostbyname_ex(x)[2][0],Port



