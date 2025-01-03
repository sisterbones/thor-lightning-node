
import time

class Logger:
    #def __init__
    
    def log(self, level="INFO", message=""):
        print("[{}::{}] {}".format(time.time(), level, message))
     
    def info(self, msg):
        self.log("INFO", msg)
        
    def debug(self, msg):
        self.log("DEBUG", msg)

    def warn(self, msg):
        self.log("WARN", msg)

    def error(self, msg):
        self.log("ERROR", msg)

    def critical(self, msg):
        self.log("CRITICAL", msg)