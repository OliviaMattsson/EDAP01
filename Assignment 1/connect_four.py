import gym
import random
import requests
import numpy as np
import math
from gym_connect_four import ConnectFourEnv
import copy

env: ConnectFourEnv = gym.make("ConnectFour-v0")

#SERVER_ADRESS = "http://localhost:8000/"
SERVER_ADRESS = "https://vilde.cs.lth.se/edap01-4inarow/"
API_KEY = 'nyckel'
STIL_ID = ["ol3270ma-s"] # TODO: fill this list with your stil-id's

def call_server(move):
   res = requests.post(SERVER_ADRESS + "move",
                       data={
                           "stil_id": STIL_ID,
                           "move": move, # -1 signals the system to start a new game. any running game is counted as a loss
                           "api_key": API_KEY,
                       })
   # For safety some respose checking is done here
   if res.status_code != 200:
      print("Server gave a bad response, error code={}".format(res.status_code))
      exit()
   if not res.json()['status']:
      print("Server returned a bad status. Return message: ")
      print(res.json()['msg'])
      exit()
   return res

"""
You can make your code work against this simple random agent
before playing against the server.
It returns a move 0-6 or -1 if it could not make a move.
To check your code for better performance, change this code to
use your own algorithm for selecting actions too
"""
def opponents_move(env):
   env.change_player() # change to oppoent
   avmoves = env.available_moves()
   if not avmoves:
      env.change_player() # change back to student before returning
      return -1

   # TODO: Optional? change this to select actions with your policy too
   # that way you get way more interesting games, and you can see if starting
   # is enough to guarrantee a win
   action = random.choice(list(avmoves))

   state, reward, done, _ = env.step(action)
   if done:
      if reward == 1: # reward is always in current players view
         reward = -1
   env.change_player() # change back to student before returning
   return state, reward, done

def student_move(state):
   # Copies over the board of the current game state
   board = copy.deepcopy(state)
   # Call minimax algorithm on the root node:
   choice = minimax(board, 5, -math.inf, math.inf, True)
   return choice[0]

def minimax(board, depth, alpha, beta, isMax):
   """
   Performs the minimax algorithm on the specified board. 
   Returns: The value of the board, from the perspective of the maximizing player.
   """
   # If we are at depth 0 or it is a winning move for one of the players, evaluate the score
   if depth == 0 or isWinningMove(board, isMax) or isWinningMove(board, not isMax):
      return evaluate(board)
   if isMax:
      # Keeps track of the best score, initializes as the worst move possible
      bestChoiceMax = [-1, -math.inf]
      for move in get_valid_moves(board):
         # Tries the new move
         newBoard = copy.deepcopy(board)
         play(newBoard, move, isMax)
         newChoice = minimax(newBoard, depth-1, alpha, beta, not isMax)[1]
         # If the new choice is better than the current best score, then save that move instead.
         if newChoice > bestChoiceMax[1]:
            bestChoiceMax = [move, newChoice]
         alpha = maxValue(alpha, bestChoiceMax[1])
         if alpha >= beta:
            break
      return bestChoiceMax
   else:
      # Keeps track of the best score, initializes as the worst move possible
      bestChoiceMin = [-1, math.inf]
      for move in get_valid_moves(board):
         # Tries the new move
         newBoard =  copy.deepcopy(board)
         play(newBoard, move, isMax)
         newChoice = minimax(newBoard, depth-1, alpha, beta, not isMax)[1]
         # If the new choice is better than the current best score, then save that move instead.
         if newChoice < bestChoiceMin[1]:
            bestChoiceMin = [move, newChoice]
         beta = minValue(beta, bestChoiceMin[1])
         if beta <= alpha:
            break
      return bestChoiceMin

def play(board, col:int, isMax:bool):
   """
   Plays the move in column 'col' on the board 'board' for the player 'isMax'. 
   """
   for row in range(5, -1, -1):
      if board[row,col] == 0:
         if isMax:
            board[row,col] = 1
            break
         else:
            board[row,col] = -1
            break
   return board
   

def is_valid_move(board, col: int): 
   """
   Returns true if the specificed column is playable, otherwise false.
   """
   return board[0][col] == 0

def get_valid_moves(board):
   """
   Retrieves all of the playable columns on the board 'board'.
   """
   valid_moves = []
   for col in range(7):
      if is_valid_move(board, col):
         valid_moves.append(col)
   return valid_moves

def evaluate(board):
   """
   Evaluates the score of the current board. 
   Returns: A set of the value of the board and an illegal move -1.
   """
   board, inARow = board, 0
   player = 1

   # Vertical check
   for row in np.flip(np.transpose(board)):
      for indexX, cell in enumerate(row):
         if indexX < 3:
            currentSet = [row[indexX], row[indexX+1], row[indexX+2], row[indexX+3]]
            inARow += findInARow(currentSet)

   # Horizontal check
   for horizontalrow in board:
      for indexX, horizontalcell in enumerate(horizontalrow):
         if indexX < 4:
            currentSet = [horizontalrow[indexX], horizontalrow[indexX+1], horizontalrow[indexX+2], horizontalrow[indexX+3]]
            inARow += findInARow(currentSet)

   # Diagonal 
   for indexY, diagrow in enumerate(board):
      for indexX, diagcell in enumerate(diagrow):
         if indexY < 3 and indexX < 4:
            currentSet= [board[indexY, indexX], board[indexY+1, indexX+1], board[indexY+2, indexX+2], board[indexY+3, indexX+3]]
            inARow += findInARow(currentSet)
         if indexY < 3 and indexX > 2:
            currentSet= [board[indexY, indexX], board[indexY+1, indexX-1], board[indexY+2, indexX-2], board[indexY+3, indexX-3]]
            inARow += findInARow(currentSet)
   
   # Points for starting in the beginning
   for row in range(6):
      if board[row,3] == player:
         inARow += 1
   
   return [-1, inARow]

def findInARow(row):
   """
   Takes a row of 4 cells and finds cells in a row.
   Returns: the score of the row. A positive score for when the maximizing player have two, three or four in
   a row, and a negative if the minimizing player have the same. 
   """
   player = 1   
   ownSlots, opponentSlots, emptySlots, score = 0,0,0,0
   
   for slot in row:
      if slot == player:
         ownSlots += 1
      elif slot == player*-1:
         opponentSlots +=1
      else:
         emptySlots += 1

   if ownSlots == 4:
      # Winning move!
      score += 100001
   elif ownSlots == 3 and emptySlots == 1:
      #Three in a row!
      score += 1000
   elif ownSlots == 2 and emptySlots == 2:
      # Two in a row (ish)
      score += 100
   elif opponentSlots == 2 and emptySlots == 2:
      # Opponent two in a row - block!
      score -= 101
   elif opponentSlots == 3 and emptySlots == 1:
      # Opponent three in a row - block! 
      score -= 1001
   elif opponentSlots == 4:
      # Opponent four in a row
      score -= 100000
   return score

def maxValue(value, other):
   if other > value:
      return other
   return value

def minValue(value, other):
   if other < value:
      return other
   return value

def isWinningMove(board, isMax):
   """
   Checks if the 'isMax' player have a winning move on the current board.
   Returns: True if such a move exists, otherwise false
   """
   if isMax:
      winningScore = 100001
   else:
      winningScore = 100000
   # Vertical check
   for row in np.transpose(board):
      for indexX, cell in enumerate(np.flip(row)):
         if indexX < 3:
            currentSet = [row[indexX], row[indexX+1], row[indexX+2], row[indexX+3]]
            inARow = findInARow(currentSet)
            if inARow == winningScore:
               return True

   # Horizontal check
   for horizontalrow in board:
      for indexX, horizontalcell in enumerate(horizontalrow):
         if indexX < 4:
            currentSet = [horizontalrow[indexX], horizontalrow[indexX+1], horizontalrow[indexX+2], horizontalrow[indexX+3]]
            inARow = findInARow(currentSet)
            if inARow == winningScore:
               return True

   # Diagonal 
   for indexY, diagrow in enumerate(board):
      for indexX, diagcell in enumerate(diagrow):
         if indexY < 3 and indexX < 4:
            currentSet= [board[indexY, indexX], board[indexY+1, indexX+1], board[indexY+2, indexX+2], board[indexY+3, indexX+3]]
            inARow =findInARow(currentSet)
            if inARow == winningScore:
               return True
         if indexY < 3 and indexX > 2:
            currentSet= [board[indexY, indexX], board[indexY+1, indexX-1], board[indexY+2, indexX-2], board[indexY+3, indexX-3]]
            inARow =findInARow(currentSet)
            if inARow == winningScore:
               return True
   return False
   
def play_game(vs_server = False):
   """
   The reward for a game is as follows. You get a
   botaction = random.choice(list(avmoves)) reward from the
   server after each move, but it is 0 while the game is running
   loss = -1
   win = +1
   draw = +0.5
   error = -10 (you get this if you try to play in a full column)
   Currently the player always makes the first move
   """

   # default state
   state = np.zeros((6, 7), dtype=int)

   # setup new game
   if vs_server:
      # Start a new game
      res = call_server(-1) # -1 signals the system to start a new game. any running game is counted as a loss

      # This should tell you if you or the bot starts
      print(res.json()['msg'])
      botmove = res.json()['botmove']
      state = np.array(res.json()['state'])
      env.reset(state)
   else:
      # reset game to starting state
      env.reset(board=None)
      # determine first player
      student_gets_move = random.choice([True, False])
      if student_gets_move:
         print('You start!')
         print()
      else:
         print('Bot starts!')
         print()

   # Print current gamestate
   print("Current state (1 are student discs, -1 are servers, 0 is empty): ")
   print(state)
   print()

   done = False
   while not done:
      # Select your move
      stmove = student_move(state) # TODO: change input here
      # make both student and bot/server moves
      if vs_server:
         env.step(stmove)
         # Send your move to server and get response
         res = call_server(stmove)
         print(res.json()['msg'])

         # Extract response values
         result = res.json()['result']
         botmove = res.json()['botmove']
         state = np.array(res.json()['state'])
         env.reset(state)
      else:
         if student_gets_move:
            # Execute your move
            avmoves = env.available_moves()
            if stmove not in avmoves:
               print("You tied to make an illegal move! Games ends.")
               break
            state, result, done, _ = env.step(stmove)

         student_gets_move = True # student only skips move first turn if bot starts

         # print or render state here if you like

         # select and make a move for the opponent, returned reward from students view
         if not done:
            state, result, done = opponents_move(env)

      # Check if the game is over
      if result != 0:
         done = True
         if not vs_server:
            print("Game over. ", end="")
         if result == 1:
            print("You won!")
         elif result == 0.5:
            print("It's a draw!")
         elif result == -1:
            print("You lost!")
         elif result == -10:
            print("You made an illegal move and have lost!")
         else:
            print("Unexpected result result={}".format(result))
         if not vs_server:
            print("Final state (1 are student discs, -1 are servers, 0 is empty): ")
      else:
         print("Current state (1 are student discs, -1 are servers, 0 is empty): ")

      # Print current gamestate
      print(state)
      print()

def main():
   play_game(vs_server = True)
   # TODO: Change vs_server to True when you are ready to play against the server
   # the results of your games there will be logged

if __name__ == "__main__":
    main()
