""" QF205 G1 Team 6 - MineSweeper Application """
import random
from tkinter import messagebox, simpledialog
import tkinter
import re
import time
import sched
from string import ascii_lowercase
import math
import googlesheet as gs

class Minesweeper:
    def __init__(self, root):
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
        frame = tkinter.Frame(root)
        frame.pack()
        self.gridsize = 10
       
        # flag and clicked tile variables
        self.flags = 0
        self.clicked = 0
        
        # timer counter
        self.timerCounter = 0
        
        # gameover flag
        self.gameoverstatus = 0
        
        
        # dictionary of buttons
        self.buttons = dict()
        
        # mine and numberofmines variables
        self.mines = 0
        self.numberofmines = 10
        
        # set default image
        default = self.tile_plain
		
        for x in range(self.gridsize):
            for y in range(self.gridsize):
                # 0 = Button widget
                # 1 = if a mine y/n (1/0)
                # 2 = state (0 = unclicked, 1 = clicked, 2 = flagged)
                # 3 = [x, y] coordinates in the grid
                # 4 = nearby mines, 0 by default, calculated after placement in grid
                self.buttons[x, y] = [ tkinter.Button(frame, image = default),
                                0,
                                0,
                                [x, y],
                                0 ]
                                
                #if left clicked, run lclicked_wrapper function, 
                #else right clicked run rclicked_wrapper function
                self.buttons[x, y][0].bind('<Button-1>', 
                                            self.lclicked_wrapper(self.buttons[x,y]))
                
                self.buttons[x, y][0].bind('<Button-3>', 
                                            self.rclicked_wrapper(self.buttons[x,y]))
                
        # lay buttons in grid
        for key in self.buttons:
            self.buttons[key][0].grid(row = self.buttons[key][3][0], 
                                      column = self.buttons[key][3][1])
        
        # create label for number of mines in game
        self.label2 = tkinter.Label(frame, text = "Mines: "+str(self.numberofmines))
        self.label2.grid(row = self.gridsize+1, 
                         column = 0, 
                         columnspan = self.gridsize//3)
        
        # create label for number of flags user set
        self.label3 = tkinter.Label(frame, text = "Flags: "+str(self.flags))
        self.label3.grid(row = self.gridsize+1, 
                         column = self.gridsize//3, 
                         columnspan = self.gridsize//3)
        
        # create label for timer
        self.label4 = tkinter.Label(frame, text = "Time: "+str(self.timerCounter))
        self.label4.grid(row = self.gridsize+1, 
                         column = round(self.gridsize//1.5), 
                         columnspan = self.gridsize//3)
        
        # start timer
        self.update_time()
	
    def lclicked_wrapper(self, button_data):
        return lambda Button: self.lclicked(button_data)

    def rclicked_wrapper(self, button_data):
        return lambda Button: self.rclicked(button_data)

    def lclicked(self, button_data):
        # initialize 2D grid of size 10 by 10
        grid=[[0]*self.gridsize]*self.gridsize
        
        # this is only ran once, on the very first click
        if self.mines == 0:
            # generate the grid with mines marked 'X' 
            # and number of mines nearby if not a mine
            grid = self.setupgrid(button_data[3])
            
            for x in range(self.gridsize):
                for y in range(self.gridsize):
                    # if mine, set mine to be y
                    if grid[x][y] == 'X':
                        self.buttons[x,y][1] = 1
                    # else, set number of mines nearby
                    else:
                        self.buttons[x,y][4] = grid[x][y]
                        
            self.mines=self.numberofmines
        
        # if user clicked a mine
        if button_data[1] == 1:
            # show all mines and check for flags
            for key in self.buttons:
                # if not a mine and flagged, show wrong flag image
                if self.buttons[key][1] != 1 and self.buttons[key][2] == 2:
                    self.buttons[key][0].config(image = self.tile_wrong)
                # if mine and not flagged, show mine image
                if self.buttons[key][1] == 1 and self.buttons[key][2] != 2:
                    self.buttons[key][0].config(image = self.tile_mine)
            
            # end game
            self.gameover()
        else:
            # if neighbors have no mine, open up tiles until numbers or edges
            if button_data[4] == 0:
                self.showcells(grid,button_data)
            
            # show number of nearby mines
            else:
                button_data[2] = 1
                self.clicked += 1
                button_data[0].config(image = self.tile_no[button_data[4]])
            
            # if number of left clicks equal to total tiles - total mines in game
            if self.clicked == self.gridsize*self.gridsize - self.numberofmines:
                self.victory()

    def rclicked(self, button_data):
        # if tile not clicked, flag
        if button_data[2] == 0:
            button_data[0].config(image = self.tile_flag)
            button_data[2] = 2
            button_data[0].unbind('<Button-1>')
            self.flags += 1
            self.update_flags()
        
        # if already flagged, unflag
        elif button_data[2] == 2:
            button_data[0].config(image = self.tile_plain)
            button_data[2] = 0
            button_data[0].bind('<Button-1>', self.lclicked_wrapper(button_data))
            self.flags -= 1
            self.update_flags()        

    def update_time(self): 
        if self.gameoverstatus == 0:
            global root
            self.timerCounter = self.timerCounter + 1;
            self.label4.config(text = "Time: "+str(self.timerCounter))
            root.after(1000, self.update_time)
    
    def update_flags(self):
        self.label3.config(text = "Flags: "+str(self.flags))
        
    def gameover(self):
        global root
        self.gameoverstatus = 1
        messagebox.showinfo("Game Over", "You Lose!")    
        root.destroy()

    def victory(self):
        global root
        self.gameoverstatus = 1
        name = simpledialog.askstring("Input", "Enter Your Name")
        messagebox.showinfo("Game Over", "You Win!")
        self.writeToFile(name)
        root.destroy()
        
        
    def writeToFile(self, username):
        # username is case insensitive
        username = username.lower()
        newScore = self.calculateScore()     
        
        #write to googlesheet
        gs.write_to_googleSpreadsheet(username, newScore)
        
    #only calculate score when player wins
    def calculateScore(self):
        # first 1 min, decrease in score will decrease with time
        if self.timerCounter <= 60:   
            rawScore = (300 ** 2 - 60 ** 2) * 60 / self.timerCounter
            return math.ceil(rawScore) #math function
        
        # next 4 min, decrease in score will increase with time
        elif self.timerCounter <= 300:
            rawScore = 300 ** 2 - self.timerCounter ** 2
            return rawScore
        
        # winning after 6minutes, 0 score
        else: 
            return 0

                
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
                elif (-1 < (rowno + i) < len(grid) 
                      and -1 < (colno + j) < len(grid)):
                    neighbors.append((rowno + i, colno + j))
        
        return neighbors

    def getmines(self, grid, start):
        mines = []
        neighbors = self.getneighbors(grid, *start)
        
        for i in range(self.numberofmines):
            cell = self.getrandomcell()
            while list(cell) == start or cell in mines or cell in neighbors:
                cell = self.getrandomcell()
                
            mines.append(cell)
            
        return mines
    
    def getnumbers(self, grid):
        for rowno, row in enumerate(grid):
            for colno, cell in enumerate(row):
                if cell != 'X':
                    # get the values of the neighbors
                    values = [grid[r][c] 
                              for r, c in self.getneighbors(grid, rowno, colno)]
					# count how many neighbors are mines
                    grid[rowno][colno] = values.count('X')

        return grid

    def showcells(self, grid, button_data):
        # exit function if the cell was already clicked
        if button_data[2]==1:
            return
        
        button_data[2]=1
        self.clicked += 1
        
        # show current cell
        if button_data[4]==0:
            button_data[0].config(image = self.tile_clicked)
        else:
            button_data[0].config(image = self.tile_no[button_data[4]])
            
        # get the neighbors if the cell has 0 nearby mines
        if button_data[4] == 0:
            for r, c in self.getneighbors(grid, *button_data[3]):
                # repeat function for each neighbor that doesn't have a flag
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