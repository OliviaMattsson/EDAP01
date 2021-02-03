import numpy as np
import math
from gym_connect_four import ConnectFourEnv

import random

class Node:

    def __init__(self, state):
        self.height = [0, 0, 0, 0, 0, 0, 0]
        self.width = 7
        self.nodeBoard = np.zeros((6, 7), dtype=int)
        self.nbrMoves = 0
        # Creates the board of the node according to the state
        for x, row in enumerate(state):
            for y, cell in enumerate(row):
                self.nodeBoard[x, y] = cell
                if cell != 0:
                    self.height[y] += 1 
    
    # Checks if the chosen column is playable.
    # Returns true if there are empty slots
    def playable(self, cell:int):
        # print("Playable on row {0} : {1}".format(cell,self.height[cell] < 6))
        return self.height[cell] <= 4 and self.nodeBoard[0, cell] == 0

    # Plays on the cell and changes the value in the board depending on
    # Which player's turn it is
    def play(self, cell:int, isMax):
        if isMax:
            self.nodeBoard[(5 - self.height[cell]), cell] = 1
        else:
            self.nodeBoard[(5 - self.height[cell]), cell] = -1
        self.height[cell] += 1
        self.nbrMoves += 1

    def moves(self):
        return self.nbrMoves

    def setMoves(self, nbr):
        self.nbrMoves = nbr

    def winningMove(self, cell, isMax):
        player = 0
        if isMax: 
            player = 1 
            print("player 1")
        else: 
            player = -1
        # Checks vertical wins.
        # 
        # Checks horizontal wins.
        # Get the row of the cell where we want to put the coin:
        horizontalRow = self.nodeBoard[self.height[cell]]
        # Checks left side for 3 in a row:
        nbrRow = 0
        for x in range(1,4):
            if cell+x <= 6 and cell+x >= 0:
                if horizontalRow[cell+x] == player:
                    nbrRow += 1
            if cell-x <= 6 and cell-x >= 0:
                if horizontalRow[cell-x] == player:
                    nbrRow += 1
            if nbrRow > 3:
                print("fOUND 3 IN  A ROW")
                return True
        


        # 2 on left and 1 on right:
        
        # Same for right:

        # 2 on right and 1 on left:
        return False
        # Checks diagonal wins.


    # Evaluation method of the node's score.
    # If there is a draw, the value will be 0.
    # The faster win gets the higher value, and the opposite for the
    # opponent. 
    def evaluate(self, isMax):
        # Draw - return 0
        if self.moves() == (6*7)/2:
            return 0
        val = -math.inf
        # Iterate over columns to check for vertical 
        for index, col in enumerate(self.nodeBoard[0]):
            # print(self.playable(index))
            # print(self.winningMove(index, isMax))
            if self.playable(index) and self.winningMove(index, isMax):
                nodeVal = (6*7 - self.moves()) / 2
                if nodeVal > val:
                    val = nodeVal
        return val

    # Returns all possible states after a move has been made in an array.
    def getChildren(self, isMax):
        children = []
        i = 0
        #print("PRINTING CHILDREN FOR {0} :".format(self.nodeBoard))
        while i < self.width:
            if self.playable(i):
                #print("Current nodeBoard: {0}".format(self.nodeBoard))
                newNode = Node(self.nodeBoard)
                newNode.setMoves(self.nbrMoves)
                newNode.play(i, isMax)
                #print("New nodeboard : {0}".format(newNode.nodeBoard))
                children.append(newNode)
            i += 1
        return children
    
