from datetime import datetime

class Movie:
    def __init__(self, name, duration, start_time, display=True):
        self.name = name
        self.duration = duration
        self.start_time = start_time  
        self.display = display

    def update_display_status(self):
        if datetime.now() > self.start_time:
            self.display = False
            print(f"--- '{self.name}' has already started.")
        else:
            self.display = True
            print(f"--- '{self.name}' is upcoming.")

    def __repr__(self):
        return f"Movie(name='{self.name}', display={self.display})"