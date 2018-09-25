from AIPlayerUtils import *
from Constants import *
from GameState import GameState
from Inventory import Inventory
from Player import Player
from typing import Dict, List


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
        return self.find_best_move(current_state, 0, None)

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

    def score_number_of_ants(self, current_state):
        # If more than enemy or not
        pass

    def score_ant_types(self, current_state):
        # Multiplier for differing types of ants
        # Soldier/r-soldier: x3
        # Drone: x2
        # Worker: x1

        # If you have more ___ than ___ (specific types)
        pass

    def score_ant_health(self, current_state):
        # If you have more health or not
        pass

    def score_food(self, current_state):

        pass

    def score_queen_threatened(self, current_state):
        # Use steps to reach on enemy fighters
        pass

    def score_anthill_protected(self, current_state):
        # How much grass around
        # how many attacking ants are around anthill
        pass

    def examine_game_state(self, current_state: GameState) -> float:
        return random.uniform(-1.0, 1.0)
        game_state_score = 0.0
        items = Items(current_state)

        my_workers = items.my_workers
        # check for each of own workers
        for worker in my_workers:
            # check if carrying food
            if worker.carrying:
                food_score += 0.01
            # add to score for each worker
            game_state_score += 0.1

        # check proximity of fighting ants to enemy workers
        enemy_workers = items.enemy_workers
        my_r_soldiers = items.my_r_soldiers
        my_soldiers = items.my_soldiers
        my_drones = items.my_drones
        for e_worker in enemy_workers:
            # check proximity of my drones to enemy workers
            for drone in my_drones:
                drone_prox = drone.coords - e_worker.coords
                game_state_score += drone_prox / 5
            # check proximity of my soldiers to enemy workers
            for r_soldier in my_r_soldiers:
                r_soldier_prox = r_soldier.coords - e_worker.coords
                game_state_score += r_soldier_prox / 5
            # check proximity of my range soldiers to enemy workers
            for soldier in my_soldiers:
                soldier_prox = soldier.coords - e_worker.coords
                game_state_score += soldier_prox / 5

        # add to score for own total amount of food
        my_food_count = items.my_food_count
        game_state_score += my_food_count / 44

        my_ants = items.my_ants
        for ant in my_ants:
            pass

        if game_state_score > 1.0:
            game_state_score = 0.99
        elif game_state_score < -1.0:
            game_state_score = -0.99

        winner = getWinner(current_state)
        if winner is None:
            return game_state_score
        elif winner == 1:
            return 1.0
        else:
            return -1.0

    def find_best_move(self, current_state, current_depth, parent_node):
        DEPTH_LIMIT = 1
        nodes: List[Node] = []
        all_legal_moves: List[Move] = listAllLegalMoves(current_state)
        move_next_state: Dict[Move, GameState] = {}
        for move in all_legal_moves:
            if move.moveType == END:
                continue

            next_state = getNextState(current_state, move)
            state_evaluation = self.examine_game_state(next_state)
            node = Node(move, next_state, state_evaluation, parent_node)
            move_next_state[move] = next_state
            nodes.append(node)

        best_nodes = self.get_list_of_best_nodes(nodes)
        if current_depth < DEPTH_LIMIT:
            for node in best_nodes:
                node.state_evaluation =\
                    self.find_best_move(move_next_state[node.move], current_depth + 1, node)

        highest_scoring_node = self.highest_scoring_node(best_nodes)
        if current_depth > 0:
            return highest_scoring_node.state_evaluation
        elif current_depth == 0:
            return highest_scoring_node.move

    def get_list_of_best_nodes(self, nodes: list) -> list:
        NUM_BEST_NODES = 5
        best_nodes: List[Node] = []
        for _ in range(NUM_BEST_NODES):
            best_nodes.append(max(nodes, key=lambda node: node.state_evaluation))
        return best_nodes

    def highest_scoring_node(self, nodes: list):
        # Citation: https://stackoverflow.com/questions/13067615/
        # python-getting-the-max-value-of-y-from-a-list-of-objects
        return max(nodes, key=lambda node: node.state_evaluation)


class Node:
    def __init__(self, move: Move, state: GameState, state_evaluation: float, parent_node):
        self.move = move
        self.state = state
        self.state_evaluation = state_evaluation
        self.parent_node = parent_node


class Items:
    """
    Items

    Helper class that serves three primary purposes.
    First, it handles calls to getAntList, getConstrList, etc.
    so that the main AIPlayer class doesn't have to do this.
    Second, it provides type hints so that the main AIPlayer class doesn't get cluttered with them.
    Third, it handles the logic for getting the inventory and me/enemy,
    so these lines of code aren't repeated needlessly in the main AIPlayer class.
    """
    def __init__(self, current_state: GameState):
        """
        __init__

        Creates a new Items object.

        :param current_state: The current GameState.
        """
        self._current_state = current_state

        # I should either be 0 or 1 (enemy is just 1 or 0, respectively)
        self._me: int = current_state.whoseTurn
        self._enemy = 1 - current_state.whoseTurn

        self._my_inventory: Inventory = current_state.inventories[self._me]
        self._enemy_inventory: Inventory = current_state.inventories[self._enemy]

    @property
    def my_food_count(self) -> int:
        """
        my_food_count

        :return: The amount of food I currently have.
        """
        return self._my_inventory.foodCount

    @property
    def enemy_food_count(self) -> int:
        """
        enemy_food_count

        :return: The amount of food that the enemy currently has.
        """
        return self._enemy_inventory.foodCount

    @property
    def my_closest_food(self) -> Construction:
        """
        my_closest_food

        :return: My food that is the closest to my tunnel.
        """
        # Distance to food and the corresponding food.
        food_distances_dict: Dict[int, Construction] = {}
        foods = getConstrList(self._current_state, None, (FOOD,))
        for food in foods:
            food_dist = stepsToReach(self._current_state, self.my_tunnel.coords, food.coords)
            food_distances_dict[food_dist] = food

        # Return the food that has the minimum cost to get to.
        return food_distances_dict[min(food_distances_dict)]

    @property
    def my_ants(self) -> List[Ant]:
        """
        my_ants

        :return: A list of all of my ants.
        """
        return getAntList(self._current_state, self._me)

    @property
    def my_queen(self) -> Ant:
        """
        my_queen

        :return: My queen from my inventory.
        """
        return getAntList(self._current_state, self._me, (QUEEN,))

    @property
    def my_workers(self) -> List[Ant]:
        """
        my_workers

        :return: A list of my workers.
        """
        return getAntList(self._current_state, self._me, (WORKER,))

    @property
    def my_drones(self) -> List[Ant]:
        """
        my_drones

        :return: A list of my drones.
        """
        return getAntList(self._current_state, self._me, (DRONE,))

    @property
    def my_soldiers(self) -> List[Ant]:
        """
        my_soldiers

        :return: A list of my soldiers.
        """
        return getAntList(self._current_state, self._me, (SOLDIER,))

    @property
    def my_r_soldiers(self) -> List[Ant]:
        """
        my_r_soldiers

        :return: A list of my ranged soldiers.
        """
        return getAntList(self._current_state, self._me, (R_SOLDIER,))

    @property
    def my_anthill(self) -> Construction:
        """
        my_anthill

        :return: My anthill from my inventory.
        """
        return self._my_inventory.getAnthill()

    @property
    def my_tunnel(self) -> Construction:
        """
        my_tunnel

        :return: My tunnel.
        """
        return getConstrList(self._current_state, self._me, (TUNNEL,))[0]

    @property
    def enemy_drones(self) -> List[Ant]:
        """
        enemy_drones

        :return: A list of enemy drones.
        """
        return getAntList(self._current_state, self._enemy, (DRONE,))

    @property
    def enemy_soldiers(self) -> List[Ant]:
        """
        my_soldiers

        :return: A list of my soldiers.
        """
        return getAntList(self._current_state, self._enemy, (SOLDIER,))

    @property
    def enemy_r_soldiers(self) -> List[Ant]:
        """
        enemy_r_soldiers

        :return: A list of enemy ranged soldiers.
        """
        return getAntList(self._current_state, self._enemy, (R_SOLDIER,))

    @property
    def enemy_queen(self) -> Ant:
        """
        enemy_queen

        :return: Enemy queen from my inventory.
        """
        return getAntList(self._current_state, self._enemy, (QUEEN,))

    @property
    def enemy_workers(self) -> List[Ant]:
        """
        enemy_workers

        :return: A list of the enemy's workers.
        """
        return getAntList(self._current_state, self._enemy, (WORKER,))

    @property
    def enemy_anthill(self) -> Construction:
        """
        enemy_anthill

        :return: The enemy's anthill.
        """
        return getConstrList(self._current_state, self._enemy, (ANTHILL,))[0]

    @property
    def enemy_tunnel(self) -> Construction:
        """
        enemy_tunnel

        :return: The enemy's tunnel.
        """
        return getConstrList(self._current_state, self._enemy, (TUNNEL,))[0]
