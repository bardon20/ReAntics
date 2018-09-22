from AIPlayerUtils import *
from Constants import *
from GameState import GameState
from Player import Player


# AIPlayer
# Description: The responsibility of this class is to interact with the game by
# deciding a valid move based on a given game state. This class has methods that
# will be implemented by students in Dr. Nuxoll's AI course.
#
# Variables:
#   playerId - The id of the player.
class AIPlayer(Player):
    # __init__
    # Description: Creates a new Player
    #
    # Parameters:
    #   inputPlayerId - The id to give the new player (int)
    def __init__(self, input_player_id):
        super(AIPlayer, self).__init__(input_player_id, "HadBarAgent")
    
    # getPlacement
    #
    # Description: called during setup phase for each Construction that
    #   must be placed by the player.  These items are: 1 Anthill on
    #   the player's side; 1 tunnel on player's side; 9 grass on the
    #   player's side; and 2 food on the enemy's side.
    #
    # Parameters:
    #   construction - the Construction to be placed.
    #   currentState - the state of the game at this point in time.
    #
    # Return: The coordinates of where the construction is to be placed
    def getPlacement(self, current_state):
        # implemented by students to return their next move
        if current_state.phase == SETUP_PHASE_1:    # stuff on my side
            num_to_place = 11
            moves = []
            for i in range(0, num_to_place):
                move = None
                while move is None:
                    # Choose any x location
                    x = random.randint(0, 9)
                    # Choose any y location on your side of the board
                    y = random.randint(0, 3)
                    # Set the move if this space is empty
                    if current_state.board[x][y].constr is None and (x, y) not in moves:
                        move = (x, y)
                moves.append(move)
            return moves
        elif current_state.phase == SETUP_PHASE_2:   # stuff on foe's side
            num_to_place = 2
            moves = []
            for i in range(0, num_to_place):
                move = None
                while move is None:
                    # Choose any x location
                    x = random.randint(0, 9)
                    # Choose any y location on enemy side of the board
                    y = random.randint(6, 9)
                    # Set the move if this space is empty
                    if current_state.board[x][y].constr is None and (x, y) not in moves:
                        move = (x, y)
                moves.append(move)
            return moves
        else:
            return [(0, 0)]
    
    # getMove
    # Description: Gets the next move from the Player.
    #
    # Parameters:
    #   currentState - The state of the current game waiting for the player's move (GameState)
    #
    # Return: The Move to be made
    def getMove(self, current_state):
        moves = listAllLegalMoves(current_state)
        selected_move = moves[random.randint(0, len(moves) - 1)]

        # don't do a build move if there are already 3+ ants
        num_ants = len(current_state.inventories[current_state.whoseTurn].ants)
        while selected_move.moveType == BUILD and num_ants >= 3:
            selected_move = moves[random.randint(0, len(moves) - 1)]
        return selected_move

    # getAttack
    # Description: Gets the attack to be made from the Player
    #
    # Parameters:
    #   currentState - A clone of the current state (GameState)
    #   attackingAnt - The ant currently making the attack (Ant)
    #   enemyLocation - The Locations of the Enemies that can be attacked (Location[])
    ##
    def getAttack(self, current_state, attacking_ant, enemy_locations):
        # Attack a random enemy.
        return enemy_locations[random.randint(0, len(enemy_locations) - 1)]

    # registerWin
    #
    # This agent doesn't learn
    #
    def registerWin(self, has_won):
        # method template, not implemented
        pass

    def examine_game_state(self, current_state: GameState) -> int:
        pass


class Node:
    def __init__(self, move: Move, state: GameState, state_evaluation: int, parent_node):
        self._move = move
        self._state = state
        self._state_evaluation = state_evaluation
        self._parent_node = parent_node

    @property
    def move(self) -> Move:
        return self._move

    @property
    def state(self) -> GameState:
        return self._state

    @property
    def state_evaluation(self) -> int:
        return self._state_evaluation

    @property
    def parent_node(self):
        return self._parent_node
