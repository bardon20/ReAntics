from AIPlayerUtils import *
from Constants import *
from GameState import GameState
from Inventory import Inventory
from Player import Player
from typing import Dict, List


class AIPlayer(Player):
    """
    Class: AIPlayer
    The Heuristic Search Agent for CS 421.

    Authors: Alex Hadi and Reeca Bardon
    Version: September 24, 2018
    """

    def __init__(self, input_player_id: int):
        """
        __init__

        The constructor for AIPlayer (creates a new player).

        :param input_player_id: The player's ID as an integer.
        """
        super(AIPlayer, self).__init__(input_player_id, "HadBarAgent")

    def getPlacement(self, current_state):
        """
        Called during the setup phase for each Construction that must be placed by the player.
        These items are: 1 Anthill on the player's side; 1 tunnel on player's side; 9 grass on the
        player's side; and 2 food on the enemy's side.

        :param current_state: The state of the game at this point in time.
        :return: The coordinates of where the construction items should be placed.
        """

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

    def getMove(self, current_state) -> Move:
        """
        getMove

        Gets the next move from the player. The search tree is used to make this decision.

        :param current_state: The state of the current game (GameState).
        :return: The move to be made.
        """
        return self.find_best_move(current_state, 0)

    def getAttack(self, current_state, attacking_ant, enemy_locations):
        """
        getAttack

        Gets the attack to be made from the player.
        Just attacks a random enemy.

        :param current_state: A clone of the current state (GameState).
        :param attacking_ant: The ant currently making the attack (Ant).
        :param enemy_locations: The locations of the enemies that can be attacked (Location[])
        :return:
        """
        return enemy_locations[random.randint(0, len(enemy_locations) - 1)]

    def registerWin(self, has_won):
        """
        registerWin

        This agent doesn't learn.

        :param has_won: Whether the agent has won or not.
        """
        pass

    def evaluate_game_state(self, current_state):
        game_state_score = 0.0

        # Number of worker ants
        items = Items(current_state)

        my_soldiers = items.my_soldiers
        my_r_soldiers = items.my_r_soldiers
        my_drones = items.my_drones
        my_workers = items.my_workers
        my_queen = items.my_queen
        my_anthill = items.my_anthill
        my_tunnel = items.my_tunnel

        ant_at_anthill = getAntAt(current_state, my_anthill.coords)
        if ant_at_anthill and ant_at_anthill.type != WORKER:
            return -0.99

        ant_at_tunnel = getAntAt(current_state, my_tunnel.coords)
        if ant_at_tunnel and ant_at_tunnel.type != WORKER:
            return -0.99

        if my_r_soldiers or my_drones:
            return -0.99

        food_count_rewards: Dict[int, float] = {
            0: 0.00,
            1: 0.10,
            2: 0.20,
            3: 0.30,
            4: 0.40,
            5: 0.50,
            6: 0.60,
            7: 0.70,
            8: 0.80,
            9: 0.90,
            10: 1.00
        }
        my_food_count = items.my_food_count
        game_state_score += food_count_rewards.get(my_food_count, 0.00)

        if len(my_soldiers) > 1:
            return -0.99

        if len(my_workers) != 1:
            return -0.99

        worker_dist_rewards: Dict[int, float] = {
            0: 0.80,
            1: 0.60,
            2: 0.40,
            3: 0.30,
            4: 0.20,
            5: 0.10,
            6: 0.00,
            7: -0.10,
            8: -0.20,
            9: -0.30,
            10: -0.40,
            11: -0.60,
            12: -0.80
        }

        soldier_dist_rewards: Dict[int, float] = {
            0: 0.00,
            1: 0.56,
            2: 0.47,
            3: 0.35,
            4: 0.21,
            5: 0.15,
            6: -0.10,
            7: -0.25,
            8: -0.30,
            9: -0.35,
            10: -0.40,
            11: -0.45,
            12: -0.50
        }

        enemy_tunnel = items.enemy_tunnel
        for soldier in my_soldiers:
            dist_to_enemy_tunnel = approxDist(soldier.coords, enemy_tunnel.coords)
            soldier_dist_rewards.get(dist_to_enemy_tunnel, -0.35)

        enemy_workers = items.enemy_workers
        if enemy_workers:
            for soldier in my_soldiers:
                dist_to_enemy_worker = approxDist(soldier.coords, enemy_workers[0].coords)
                if dist_to_enemy_worker <= 1:
                    if enemy_workers[0].coords in listAdjacent(soldier.coords):
                        game_state_score += 0.5
                else:
                    game_state_score += soldier_dist_rewards.get(dist_to_enemy_worker, -0.60)

        if approxDist(my_anthill.coords, my_queen.coords) == 0:
            game_state_score -= .99
        for worker in my_workers:
            dist_to_tunnel = approxDist(worker.coords, my_tunnel.coords)
            dist_to_anthill = approxDist(worker.coords, my_anthill.coords)
            closest_construction = min(dist_to_anthill, dist_to_tunnel)
            if worker.carrying:
                game_state_score += worker_dist_rewards.get(closest_construction, -0.80)
            else:
                if closest_construction == 0:
                    game_state_score -= 0.50
                my_closest_food = items.my_closest_food
                dist_to_closest_food = approxDist(worker.coords, my_closest_food.coords)
                game_state_score += worker_dist_rewards.get(dist_to_closest_food, -0.80)

        winner = getWinner(current_state)
        if winner == 1:
            return 1.0
        elif winner == 0:
            return -1.0

        if game_state_score >= 1.0:
            return 0.99
        elif game_state_score <= -1.0:
            return -0.99
        return game_state_score

    def find_best_move(self, current_state: GameState, current_depth: int):
        """
        find_best_move                  <!-- RECURSIVE -->

        The best move is found by recursively traversing the search tree.
        An average of the evaluation scores is used to determine an overall score.

        :param current_state: The current GameState.
        :param current_depth: The current depth level in the tree.
        :return: The Move that the agent wishes to perform.
        """
        # The children nodes are checked, so it goes to a depth limit of 2.
        DEPTH_LIMIT = 1
        all_legal_moves: List[Move] = listAllLegalMoves(current_state)
        all_nodes: List[Node] = []

        for move in all_legal_moves:
            # Ignore the END_TURN move.
            if move.moveType == "END_TURN":
                continue

            next_state_reached = self.getNextState(current_state, move)
            node = Node(move, next_state_reached, self.evaluate_game_state(next_state_reached))

            # Recursively goes through the search tree.
            if current_depth < DEPTH_LIMIT:
                node.state_evaluation = self.find_best_move(next_state_reached, current_depth + 1)
            all_nodes.append(node)

        if current_depth > 0:
            return self.average_evaluation_score(all_nodes)
        else:
            # Citation: https://stackoverflow.com/questions/13067615/
            # python-getting-the-max-value-of-y-from-a-list-of-objects
            return max(all_nodes, key=lambda x: x.state_evaluation).move

    def average_evaluation_score(self, nodes: list) -> float:
        """
        Helper method to determine the overall evaluation score of a list of nodes.
        The average method is used.

        :param nodes: The list of nodes to check.
        :return: The average evaluation score of all the checked nodes.
        """
        return sum(node.state_evaluation for node in nodes) / len(nodes)

    def getNextState(self, currentState, move):
        """
        Revised version of getNextState from AIPlayerUtils.
        Copied from Nux's email to the class.
        
        :param currentState: The current GameState.
        :param move: The move to be performed.
        :return: The next GameState from the specified move.
        """

        # variables I will need
        myGameState = currentState.fastclone()
        myInv = getCurrPlayerInventory(myGameState)
        me = myGameState.whoseTurn
        myAnts = myInv.ants
        myTunnels = myInv.getTunnels()
        myAntHill = myInv.getAnthill()

        # If enemy ant is on my anthill or tunnel update capture health
        ant = getAntAt(myGameState, myAntHill.coords)
        if ant is not None:
            if ant.player != me:
                myAntHill.captureHealth -= 1

        # If an ant is built update list of ants
        antTypes = [WORKER, DRONE, SOLDIER, R_SOLDIER]
        if move.moveType == BUILD:
            if move.buildType in antTypes:
                ant = Ant(myInv.getAnthill().coords, move.buildType, me)
                myInv.ants.append(ant)
                # Update food count depending on ant built
                if move.buildType == WORKER:
                    myInv.foodCount -= 1
                elif move.buildType == DRONE or move.buildType == R_SOLDIER:
                    myInv.foodCount -= 2
                elif move.buildType == SOLDIER:
                    myInv.foodCount -= 3
            # ants are no longer allowed to build tunnels, so this is an error
            elif move.buildType == TUNNEL:
                print("Attempted tunnel build in getNextState()")
                return currentState

        # If an ant is moved update their coordinates and has moved
        elif move.moveType == MOVE_ANT:
            newCoord = move.coordList[-1]
            startingCoord = move.coordList[0]
            for ant in myAnts:
                if ant.coords == startingCoord:
                    ant.coords = newCoord
                    # TODO: should this be set true? Design decision
                    ant.hasMoved = False
                    attackable = listAttackable(ant.coords, UNIT_STATS[ant.type][RANGE])
                    for coord in attackable:
                        foundAnt = getAntAt(myGameState, coord)
                        if foundAnt is not None:  # If ant is adjacent my ant
                            if foundAnt.player != me:  # if the ant is not me
                                foundAnt.health = foundAnt.health - UNIT_STATS[ant.type][
                                    ATTACK]  # attack
                                # If an enemy is attacked and looses all its health remove it from the other players
                                # inventory
                                if foundAnt.health <= 0:
                                    myGameState.inventories[1 - me].ants.remove(foundAnt)
                                # If attacked an ant already don't attack any more
                                break
        return myGameState


class Node:
    def __init__(self, move: Move, state: GameState, state_evaluation: float):
        """
        Node

        Class that represents a single node in the search tree.

        :param move: The move that is taken from the parent node to the current node.
        :param state: The resulting state of the move.
        :param state_evaluation: The state evaluation score for the node.
        """
        self.move = move
        self.state = state
        self.state_evaluation = state_evaluation


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
    def my_food(self) -> List[Construction]:
        return getConstrList(self._current_state, None, (FOOD,))

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
            # Want the food closest to either the tunnel or anthill.
            food_dist_to_tunnel = approxDist(self.my_tunnel.coords, food.coords)
            food_dist_to_anthill = approxDist(self.my_anthill.coords, food.coords)
            food_distances_dict[min(food_dist_to_anthill, food_dist_to_tunnel)] = food

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
        return getAntList(self._current_state, self._me, (QUEEN,))[0]

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
