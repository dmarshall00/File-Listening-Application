# listening for files in a specified directory, to be placed in directory to be listened to
import sys
import time
import logging
import socket
import tkinter as tk
from queue import Queue
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

HOST = '127.0.0.1'
PORT = 5050
IP = socket.gethostbyname(socket.gethostname())

server = socket.socket()
server.bind((HOST, PORT))
server.listen()

client = socket.socket()

class Handler(FileSystemEventHandler):
    def __init__(self, app):
        FileSystemEventHandler.__init__(self)
        self.app = app

    def on_any_event(self, event):
        self.app.forward(event)

class FileListenerApp():
    def __init__(self):
        logging.basicConfig(filename='log_events.txt', level=logging.DEBUG, format='')
        self.path = sys.argv[1] if len(sys.argv) > 1 else '.'
        event_handler = Handler(self)
        self.observer = Observer()
        self.observer.schedule(event_handler, self.path, recursive=True)

        self.queue = Queue()
        self.root = tk.Tk()

        self.req_w = self.root.winfo_reqwidth()
        self.req_h = self.root.winfo_reqheight()
        self.screen_w = self.root.winfo_screenwidth()
        self.screen_h = self.root.winfo_screenheight()
        x = (self.screen_w/3.5) - (self.req_w/3.5)
        y = (self.screen_h/3.5) - (self.req_h/3.5)
        self.root.geometry('+%d+%d' % (x, y))

        self.root.title("[FILE LOG]")

        self.text = tk.Text(self.root, font=("Courier New", 14, "normal"))
        self.text.pack(fill="both", expand=True)
        self.text.insert("end", "[ACTIVE STATE] LISTENING %s...\n\n" % self.path)

        self.root.bind("<Destroy>", self.shutdown)
        self.root.bind("<<WatchdogEvent>>", self.event)

        # server
        #conn, addr = server.accept()
        #print("Connection from", addr)
        #conn.send("Connection received.".encode())

        self.observer.start()

    def event(self, event):
        self.queue.get(event)

    def shutdown(self, event):
        self.observer.stop()
        self.observer.join()

    def mainloop(self):
        self.root.mainloop()

    def forward(self, event):
        self.text.config(state="normal")
        self.queue.put(event)

        self.save_events("{} - [{}] on: [{}] at [{}]\n\n".format(IP, event.event_type, time.asctime(), event.src_path))
        self.text.insert("end", "{} - [{}] on: [{}] at [{}]\n\n".format(IP, event.event_type, time.asctime(), event.src_path))
        
        self.text.config(state="disabled")
    
    def save_events(self, data):
        logging.info(data)
        print(data)

if __name__ == "__main__":
    app = FileListenerApp()
    app.mainloop()