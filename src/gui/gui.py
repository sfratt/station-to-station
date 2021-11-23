import tkinter as tk
from tkinter.constants import DISABLED, NORMAL, RIGHT, X, Y

def register():
    # Make call to register function in client.py
    pass

def de_register():
    pass

def insert_log(msg: str):
    log_text.configure(state=NORMAL)
    log_text.insert(tk.END, msg)
    log_text.configure(state=DISABLED)

window = tk.Tk()
window.geometry("450x400")
window.resizable(False, False)

label = tk.Label(text="Name").place(x=0, y=0)
entry = tk.Entry(window, width=40)
entry.place(x=50, y=0)

tk.Button(window, text="Register", command=register).place(x=0, y=25)
tk.Button(window, text="Deregister", command=de_register).place(x=55, y=25)
tk.Button(window, text="Func1", command=register).place(x=120, y=25)

scroll = tk.Scrollbar(window)

log_text = tk.Text(window, height=20, width=55, state=NORMAL)
log_text.place(x=0, y=50)
insert_log('testing\nasfasf\nfasf\ng\nfn\nfnfn\nfnn\nfnfn\nfnf\ndndn\ndddd\nddddd\nddddd\ndddddasfasf\nfasf\ng\nfn\nfnfn\nfnn\nfnfn\nfnf\ndndn\ndddd\nddddd\nddddd\nddddd')

# Need to start running the Client() when the UI starts

window.mainloop()