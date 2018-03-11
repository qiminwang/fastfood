"""A command line version of Minesweeper"""
import random
from tkinter import messagebox
import tkinter
import re
import time
import sched
from string import ascii_lowercase

class Minesweeper:
    def __init__(self, master):
        # import images
        self.tile_plain = tkinter.PhotoImage(file = "images/tile_plain.png")
        self.tile_clicked = tkinter.PhotoImage(file = "images/tile_clicked.png")
        self.tile_mine = tkinter.PhotoImage(file = "images/tile_mine.png")
        self.tile_flag = tkinter.PhotoImage(file = "images/tile_flag.png")
        self.tile_wrong = tkinter.PhotoImage(file = "images/tile_wrong.png")
        self.tile_no = {}
		
		#for tile numbers 1-8
        for x in range(1, 9):
            self.tile_no[x]=tkinter.PhotoImage(file = "images/tile_"+str(x)+".png")

        # set up frame
        frame = tkinter.Frame(master)
        frame.pack()

        # show "Minesweeper" at the top
        self.gridsize = 10
        self.label1 = tkinter.Label(frame, text="Minesweeper")
        self.label1.grid(row = 0, column = 0, columnspan = self.gridsize)

        # create flag and clicked tile variables
        self.flags = 0
        self.correct_flags = 0
        self.clicked = 0
        
        # timer counter
        self.timerCounter = 0;

        # create buttons
        self.buttons = dict({})
        self.mines = 0
        self.numberofmines = 10

		# tile image changeable for debug reasons:
        gfx = self.tile_plain
		
        for x in range(self.gridsize):
            for y in range(self.gridsize):
                # 0 = Button widget
                # 1 = if a mine y/n (1/0)
                # 2 = state (0 = unclicked, 1 = clicked, 2 = flagged)
                # 3 = [x, y] coordinates in the grid
                # 4 = nearby mines, 0 by default, calculated after placement in grid
                self.buttons[x, y] = [ tkinter.Button(frame, image = gfx),
                                0,
                                0,
                                [x, y],
                                0 ]
                #if left clicked, go to lclicked_wrapper, else right clicked go rclicked_wrapper
                self.buttons[x, y][0].bind('<Button-1>', self.lclicked_wrapper(*self.buttons[x,y][3]))
                self.buttons[x, y][0].bind('<Button-3>', self.rclicked_wrapper(*self.buttons[x,y][3]))
        
        # lay buttons in grid
        for key in self.buttons:
            self.buttons[key][0].grid( row = self.buttons[key][3][0], column = self.buttons[key][3][1] )
        
        # find nearby mines and display number on tile
        #add mine and count at the end
        """
        below is the code for labeling, can use for timer
        """
        self.label2 = tkinter.Label(frame, text = "Mines: "+str(self.numberofmines))
        self.label2.grid(row = self.gridsize+1, column = 0, columnspan = self.gridsize//3)

        self.label3 = tkinter.Label(frame, text = "Flags: "+str(self.flags))
        self.label3.grid(row = self.gridsize+1, column = self.gridsize//3, columnspan = self.gridsize//3)
        
        #time label
        self.label4 = tkinter.Label(frame, text = "Time: "+str(self.timerCounter))
        self.label4.grid(row = self.gridsize+1, column = round(self.gridsize//1.5), columnspan = self.gridsize//3)
        
        # start timer
        self.update_time()
    ## End of __init__
	
    def lclicked_wrapper(self, x, y):
        return lambda Button: self.lclicked(self.buttons[x,y])

    def rclicked_wrapper(self, x, y):
        return lambda Button: self.rclicked(self.buttons[x,y])

    def lclicked(self, button_data):
        grid=[[0]*self.gridsize]*self.gridsize
        if self.mines==0:
            grid = self.setupgrid(button_data[3])
            for x in range(self.gridsize):
                for y in range(self.gridsize):
                    if grid[x][y]=='X':
                        self.buttons[x,y][1]=1
                    else:
                        self.buttons[x,y][4]=grid[x][y]
            self.mines=self.numberofmines
                    
        if button_data[1] == 1: #if user clicked a mine
            # show all mines and check for flags
            for key in self.buttons:
                #not a mine and flagged, wrong
                if self.buttons[key][1] != 1 and self.buttons[key][2] == 2:
                    self.buttons[key][0].config(image = self.tile_wrong)
                #mine and not flagged, mine
                if self.buttons[key][1] == 1 and self.buttons[key][2] != 2:
                    self.buttons[key][0].config(image = self.tile_mine)
            # end game
            self.gameover()
        else:
            #change image
            if button_data[4] == 0: #if neighbors no mine
                self.showcells(grid,button_data)
            
            else: #if neighbors have mine
                button_data[2] = 1
                self.clicked += 1
                button_data[0].config(image = self.tile_no[button_data[4]])
                
            if self.clicked == 100 - self.numberofmines:
                self.victory()

    def rclicked(self, button_data):
        # if not clicked
        if button_data[2] == 0:
            button_data[0].config(image = self.tile_flag)
            button_data[2] = 2
            button_data[0].unbind('<Button-1>')
            # if a mine
            if button_data[1] == 1:
                self.correct_flags += 1
            self.flags += 1
            self.update_flags()
        # if flagged, unflag
        elif button_data[2] == 2:
            button_data[0].config(image = self.tile_plain)
            button_data[2] = 0
            button_data[0].bind('<Button-1>', self.lclicked_wrapper(*button_data[3]))
            # if a mine
            if button_data[1] == 1:
                self.correct_flags -= 1
            self.flags -= 1
            self.update_flags()

    """
    this is where the label gets updated, timer needs to update this every second...?
    """            

    def update_time(self): 
        global root
        self.timerCounter = self.timerCounter + 1;
        self.label4.config(text = "Time: "+str(self.timerCounter))
        root.after(1000, self.update_time)
    
    
    def update_flags(self):
        self.label3.config(text = "Flags: "+str(self.flags))
        
    def gameover(self):
        messagebox.showinfo("Game Over", "You Lose!")
        global root
        root.destroy()

    def victory(self):
        messagebox.showinfo("Game Over", "You Win!")
        global root
        root.destroy()
        
    def setupgrid(self, start):
        emptygrid = [[0 for i in range(self.gridsize)] for i in range(self.gridsize)]
        mines = self.getmines(emptygrid, start)
        
        for i, j in mines:
            emptygrid[i][j] = 'X'

        grid = self.getnumbers(emptygrid)
        
        return grid

    def getrandomcell(self):
        a = random.randint(0, self.gridsize - 1)
        b = random.randint(0, self.gridsize - 1)
        return (a, b)

    def getneighbors(self, grid, rowno, colno):
        neighbors = []
        
        for i in range(-1, 2):
            for j in range(-1, 2):
                if i == 0 and j == 0:
                    continue
                elif -1 < (rowno + i) < len(grid) and -1 < (colno + j) < len(grid):
                    neighbors.append((rowno + i, colno + j))
        
        return neighbors

    def getmines(self, grid, start):
        mines = []
        neighbors = self.getneighbors(grid, *start)
        
        for i in range(self.numberofmines):
            cell = self.getrandomcell()
            while cell == start or cell in mines or cell in neighbors:
                cell = self.getrandomcell()
            mines.append(cell)
            
        return mines

    def getnumbers(self, grid):
        for rowno, row in enumerate(grid):
            for colno, cell in enumerate(row):
                if cell != 'X':
                    #Gets the values of the neighbors
                    values = [grid[r][c] for r, c in self.getneighbors(grid, rowno, colno)]
					# Counts how many are mines
                    grid[rowno][colno] = values.count('X')

        return grid

    def showcells(self, grid, button_data):
        # Exit function if the cell was already shown
        if button_data[2]==1:
            return
        
        # Show current cell
        button_data[2]=1
        self.clicked += 1
        
        #change image
        if button_data[4]==0:
            button_data[0].config(image = self.tile_clicked)
        else:
            button_data[0].config(image = self.tile_no[button_data[4]])
            
        # Get the neighbors if the cell is empty
        if button_data[4] == 0:
            for r, c in self.getneighbors(grid, *button_data[3]):
                # Repeat function for each neighbor that doesn't have a flag
                if self.buttons[r,c][2] != 2:
                    self.showcells(grid, self.buttons[r,c])
                    
def main():
    global root
    # create Tk widget
    root = tkinter.Tk()
    # set program title
    root.title("Minesweeper")
    # create game instance
    minesweeper = Minesweeper(root)
    # run event loop
    root.mainloop()
    
    
if __name__ == "__main__":
    main()