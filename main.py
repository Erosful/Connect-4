import Host,Utils,Client,time
C = Client.Client()
Hand = Utils.Handler(C)
Hand.begin()
time.sleep(3)
if C.IsMatchMaking:
    H = Host.Host(C.Socket)
    Hand.Add_Listener(H)
    H.start()
C.Root.mainloop()
