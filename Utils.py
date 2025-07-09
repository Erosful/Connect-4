class Utils: #Where I'm putting misc subroutines which are called by both Host and Client - DRY
    def Get_IP():
        Port = 43000 #Change this constant to change on both files
        x = socket.getfqdn()
        return socket.gethostbyname_ex(x)[2][0],Port
