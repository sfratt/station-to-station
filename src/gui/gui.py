import tkinter as tk
from tkinter.constants import DISABLED, NORMAL

def Register():
    return

window = tk.Tk()
window.geometry("450x400")
window.resizable(False, False)

label = tk.Label(text="Name").grid(row=0, column=0)
entry = tk.Entry(window, width=40)
entry.grid(row=0, column=1, padx=5, pady=5)

tk.Button(window, text="Register", command=Register).grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
tk.Button(window, text="Deregister", command=Register).grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)

log_text = tk.Text(window, height=20, width=40, state=NORMAL)
log_text.grid(row=2, column=1)
log_text.insert(tk.END, "testing")
log_text.configure(state=DISABLED)

window.mainloop()