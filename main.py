import tkinter
import views
import os

root = tkinter.Tk()
root.wm_title("Mango")
root.geometry("750x600")
root.resizable()

views.search_games(root)

root.mainloop()

if os.path.exists("temp.html"):
    os.remove("temp.html")
