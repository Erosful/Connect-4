from tkinter import *
import random
import socket
import threading
root = Tk()
root.geometry("500x600")
frame_1 = Frame(root)
frame_2 = Frame(root)
frame_1.pack()
frame_2.pack()
Players = ["1","2"]
Colors = ["red","blue"]
TurnText = ["Your","Opponents"]
Columns = 7
Rows = 6
NumInARow = 4
List = []
Buttons = []
LabelColour = "light gray"
SIZE = 1024
PORT_NUMBER = 65000
SIZE = 1024

#TO DO LIST:
#View all available games
#Personal matchmaking - join game via gameID
#View games?
#Start Random or Private game
#Signin/Play as guest
#Store data such as leaderboards
#Tournament???

#ERRORS:
#If one player closes python, entire host might break.
#If computer closes and reopens connection, it will duplicate multiple times.
mySocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM )
x = socket.getfqdn()
MY_IP = socket.gethostbyname_ex(x)[2][0]
Name = input("Enter your username: ")
print(MY_IP)
mySocket.bind((MY_IP,PORT_NUMBER))
MatchMaking = True
while True:
    (data,addr) = mySocket.recvfrom(SIZE)
    SERVER_IP = addr[0]
    if "Anybody alive!?" in str(data) and MatchMaking:
        mySocket.sendto(f"recieving connection! {Name}".encode('utf-8'),(addr))
        print(f"Connected to host, entering matchmaking")
        MatchMaking = False
    if "Player" in str(data):
        print(f"You are player {int(str(data)[9])+1}")
        Player = int(str(data)[9])
        TheirName = str(data)[26:len(str(data))-1]
        GameID = str(data)[20:24]
        break

def handler():
    while True:
        (data,addr) = mySocket.recvfrom(SIZE)
        if addr[0] != SERVER_IP:
            continue #Ignore everything that isn't sent from the Host. 
        data = str(data)
        if "ping" in data:
            mySocket.sendto(f"pong".encode('utf-8'),(addr))
        elif "Anybody alive!?" in data:
            continue
        elif "reset" in data:
            Reset(False,int(str(data)[8]))
            continue
        else:
            data = data[2:len(data)-1]
            choice(int(data),False)

def ColourCheck(Pos1,Pos2,Colour):
    Win = True
    UpCount = 0; UpList = []
    HorizontalCount = 0; HorizontalList = []
    LeftDiagonalCount = 0; LeftDiagonalList = []
    RightDiagonalCount = 0; RightDiagonalList = []
    for i in range(0,NumInARow):
        try:
            if List[Pos1][Pos2+i].cget("bg") == Colour:
                UpCount += 1
                UpList.append(List[Pos1][Pos2+i])
        except: UpCount += 0
        try:
            if List[Pos1+i][Pos2].cget("bg") == Colour:
                HorizontalCount += 1
                HorizontalList.append(List[Pos1+i][Pos2])
        except: HorizontalCount += 0
        try:
            if List[Pos1-i][Pos2+i].cget("bg") == Colour and (Pos1-i)>=0:
                LeftDiagonalCount += 1
                LeftDiagonalList.append(List[Pos1-i][Pos2+i])
        except: LeftDiagonalCount += 0
        try:
            if List[Pos1+i][Pos2+i].cget("bg") == Colour:
                RightDiagonalCount += 1
                RightDiagonalList.append(List[Pos1+i][Pos2+i])
        except: RightDiagonalCount += 0
    if UpCount == NumInARow:
        for i in range(len(UpList)): UpList[i].config(background = "yellow")
    elif HorizontalCount == NumInARow:
        for i in range(0,len(HorizontalList)): HorizontalList[i].config(background = "yellow")
    elif LeftDiagonalCount == NumInARow:
        for i in range(len(LeftDiagonalList)): LeftDiagonalList[i].config(background = "yellow")
    elif RightDiagonalCount == NumInARow:
        for i in range(len(RightDiagonalList)): RightDiagonalList[i].config(background = "yellow")
    else:
        Win = False
    return Win

def WinCheck(player,pos):
    turn.config(text=(player[0],"Turn"),bg=Colors[player[1]])
    Win = False
    for i in range(len(List)):
        for i2 in range(len(List[i])):
            if List[i][i2].cget("bg") == Colors[int(player[1])-1]:
                Win = ColourCheck(i,i2,Colors[int(player[1])-1])
                if Win == True:
                    if player[0] == "Opponents":
                        text = "You Win!"
                    else:
                        text = "You Lose!"
                    turn.config(text = text,bg = "green")
                    for i in range(len(List)):
                        Buttons[i].config(bg = "black")
                    break
                continue

def Reset(Network,P):
    global Player
    Player = P
    if Network:
        if P == 1:
            Player2 = 0
        else:
            Player2 = 1
        mySocket.sendto(f"reset {Player2}".encode('utf-8'),(SERVER_IP,PORT_NUMBER))
    turn.config(text = (f"{TurnText[Player]} Turn"), bg = Colors[Player])
    for i in range(len(List)):
        Buttons[i].config(bg = "green")
        for i2 in range(len(List[i])):
            List[i][i2].config(bg = LabelColour)

def choice(pos,Network):
    txt = turn.cget("text")
    if "Opponent" in txt and Network:
        return
    if Network:
        mySocket.sendto(str(pos).encode('utf-8'),(SERVER_IP,PORT_NUMBER))
    if Buttons[pos].cget("bg") == "green":
        txt = turn.cget("text")
        if "Opponent" in txt:
            player = ["Your",0]
        else:
            player = ["Opponents",1]
        for i in range(Rows):
            if List[pos][i].cget("bg") == LabelColour:
                List[pos][i].config(bg = Colors[int(player[1])-1])
                break
            if List[pos][len(List[pos])-2].cget("bg") != LabelColour:
                Buttons[pos].config(bg = "Black")
        WinCheck(player,pos)
Playing = Label(frame_1,font= ("Courier",20,"bold"),text = f"Playing: {TheirName}")
GameID = Label(frame_1,font = ("Courier",16, "bold"), text = (f"Game ID: {GameID}"))
Playing.pack()
GameID.pack()
for i in range(Columns):
    frm = Frame(frame_1)
    frm.pack(side = LEFT)
    btn = Button(frm, bg = "green", height = 4, width = 8, font = ("Ariel",8, "bold"), command = lambda pos = (i): choice(pos,True))
    btn.pack(side = BOTTOM)
    Buttons.append(btn)
    List2 = []
    for j in range(Rows):
        Lbl = Label(frm, bg = LabelColour, height = 4, width = 8, font = ("Ariel",8, "bold"))
        Lbl.pack(side = BOTTOM,pady=1)
        List2.append(Lbl)
    List.append(List2)

turn = Label(frame_2,font = ("Courier",20, "bold"), text = (f"{TurnText[Player]} Turn"), bg = Colors[Player])
turn.pack()
reset = Button(root, font = ("Courier",10, "bold"), text = ("Reset"), command = lambda: Reset(True,random.randint(0,1)),bg='red',height = 2, width = 4)
reset.pack()
x = threading.Thread(target=handler)
x.start()
root.mainloop()
