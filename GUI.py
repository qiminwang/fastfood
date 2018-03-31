import tkinter
from tkinter import messagebox, simpledialog

root = tkinter.Tk()
root.title("Minesweeper")

frame = tkinter.Frame(root)
frame.pack()
  
tile = tkinter.PhotoImage(file = "tile_plain.png")
button = tkinter.Button(frame, image = tile)

def hello(event):
    messagebox.showinfo("Game Over", "You Win!")
button.bind('<Button-1>', hello)

button.grid(row = 0, column = 0)

label1 = tkinter.Label(frame, text = "Mines: 10")
label1.grid(row = 1, column = 0, columnspan = 5)
label2 = tkinter.Label(frame, text = "Flags: 0")
label2.grid(row = 1, column = 5, columnspan = 5)

simpledialog.askstring("Input", "Enter Your Name")

root.mainloop()