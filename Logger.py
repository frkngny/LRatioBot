from datetime import datetime


# logger class to log the contracts if there is any trade
class Logger:
    def __init__(self):
        self.n = datetime.now().strftime("%d%m%Y-%H%M%S")
        self.log_file = f"log_{self.n}.txt"
    
    def log(self, msg: str):
        now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        try:
            with open(self.log_file, "a") as file:
                file.write(f"{now} - {msg}\n")
        except:
            with open(self.log_file, "w") as file:
                file.close()
            self.log(msg)
            pass
