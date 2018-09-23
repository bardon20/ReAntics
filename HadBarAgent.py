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

    def examine_game_state(self, current_state: GameState) -> float:
        game_state_score = 0.0
        items = Items(current_state)
        food_score=0
        health_score=0
        e_food_score=0
        e_health_score=0

        my_workers = items.my_workers
        worker_health=0
        # check for each of own workers
        for worker in my_workers:
            # check the health
            worker_health -= worker.health/5
            # check if carrying food
            if worker.carrying:
                food_score += 0.01
            # add to score for each worker
            game_state_score += 0.1

        # same for enemy workers
        enemy_workers = items.enemy_workers
        for e_worker in enemy_workers:
            # check health
            worker_health -= e_worker.health/5
            # check if carrying food
            if e_worker.carrying:
                e_food_score -= 0.01
            # subtract from score for each worker
            game_state_score -= 0.1

        # check each for each of own drones
        my_drones = items.my_drones
        drone_health=0
        for drone in my_drones:
            # check health
            drone_health += drone.health/5
            # check proximity to queen/anthill

            # subtract from score for each drone
            game_state_score += 0.1

        # same for enemy drones
        enemy_drones = items.enemy_drones
        for e_drone in enemy_drones:
            # check health
            drone_health -= e_drone.health/5
            # check proximity to queen/anthill

            game_state_score -= 0.1

        # check each of own range soldiers
        r_soldier_health=0
        my_r_soldiers = items.my_r_soldiers
        for r_soldier in my_r_soldiers:
            # check health
            r_soldier_health += r_soldier.health/5
            # check for proximity fo anthill/queen

            # update score for each soldier
            game_state_score += 0.1

        # same for enemy range soldiers
        enemy_r_soldiers = items.enemy_r_soldiers
        for e_r_soldier in enemy_r_soldiers:
            # check health
            r_soldier_health -= e_r_soldier.health / 5
            # check proximity fo anthill/queen

            # subtract from score for each range soldier
            game_state_score -= 0.1

        # check each of own soldiers
        my_soldiers = items.my_soldiers
        soldier_health=0
        for soldier in my_soldiers:
            # check health
            soldier_health += soldier.health / 5
            # check for proximity fo anthill/queen

            # update score for each soldier
            game_state_score += 0.1

        # same for enemy soldiers
        enemy_soldiers = items.enemy_soldiers
        for e_soldier in enemy_soldiers:
            # check health
            soldier_health -= e_soldier.health / 5
            # check proximity fo anthill/queen

            # subtract from score for each range soldier
            game_state_score -= 0.1

        # check health of own queen
        health_score = items.my_queen/5
        # check health of enemy queen
        e_health_score - items.enemy_queen/5

        # add up health score
        health_score = health_score + worker_health + drone_health + r_soldier_health + soldier_health

        # add to score for own total amount of food
        my_food_count = items.my_food_count
        game_state_score += my_food_count / 44

        # subtract from score for enemy total amount of food
        enemy_food_count = items.enemy_food_count
        game_state_score -= enemy_food_count / 44

        # check how well protect own anthill is, add to score

        # check how well protects own anthill is, subtract from score

        my_ants = items.my_ants
        for ant in my_ants:
            pass

        if game_state_score > 1.0:
            return 1.0
        elif game_state_score < -1.0:
            return -1.0
        return game_state_score

    def call_nodes_recursively(self, current_state, depth_limit):
        all_legal_moves = self.all_possible_moves(current_state)
        next_game_states: List[GameState] = []
        for move in all_legal_moves:
            next_game_states.append(getNextState(current_state, move))

        if depth_limit < 2:
            for game_state in next_game_states:
                self.call_nodes_recursively(game_state, depth_limit+1)
    
    def average_evaluation_score(self, nodes: list) -> float:
        evaluation_score_sum = 0
        for node in nodes:
            evaluation_score_sum += node.state_evaluation
        return evaluation_score_sum / len(nodes)

    def all_possible_moves(self, current_state):
        all_legal_moves = []
        all_legal_moves.extend(listAllMovementMoves(current_state))
        all_legal_moves.extend(listAllBuildMoves(current_state))
        return all_legal_moves


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
