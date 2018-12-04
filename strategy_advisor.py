from game_consts import *
from tree_search import SearchProblem, SearchTree
from pathways import Pathways
from corridor import Corridor
from ghost_info import Ghost_Info
from pacman_info import Pacman_Info
import logging

# logs are written to file advisor.log after the client is closed
# possible messages: debug, info, warning, error, critical 
# how to use: logger.typeOfMessage('message')
logger = logging.getLogger('advisor')
logger_format = '[%(lineno)s - %(funcName)20s() - %(levelname)s]\n %(message)s\n'
#logger_format = '%(levelname)s:\t%(message)' # simpler format

# currently writing over the logger file, change filemode to a to append
logging.basicConfig(format=logger_format, filename='advisor.log', filemode='w', level=logging.DEBUG)

# logger
# logs are written to file strategy_advisor.log after the client is closed
# possible messages: debug, info, warning, error, critical 
# how to use: logger.typeOfMessage('message')
logger = setup_logger('strategy_advisor', 'strategy_advisor.log')

class StrategyAdvisor():
    """Analyses corridors safety (if contains ghost or not) and crossroads
    semaphores. Advises on a strategy for the given conditions.

    Args:
    map_: instance of Map for the current level
    state: the game state given by the server

    Attr:
    ghosts: A set of quadruples with (ghost_position, zombie, timeout, distance_to_pacman)
    """

    def __init__(self, map_, state):
        self.map_ = map_
        self.state = state
        self.unsafe_corridors = self.set_corridors_safety()
        self.pacman_info = Pacman_Info(state['pacman'])
        self.calculate_pacman_corridor()
        self.ghosts_info = self.calculate_ghosts_info()
        self.zombie_ghosts = []
        self.calculate_semaphores()
    


    #* COMPLETE - NOT TESTED
    def set_corridors_safety(self):
        """Sets the corridors safety flag according to the existence of ghosts

        Args:
        ghots: a list with the position of all non zombie ghosts

        Returns:
        A list of tuples with the unsafe corridors and the position of the ghost
        in that corridor. If more than one ghost is in a given corridors, the
        corridor is returned multiple times tupled with each ghost 
        """

        logger.debug("########################################################")
        logger.debug("SET_CORRIDORS_SAFETY()")
        logger.debug("########################################################")

        unsafe_corridors = []
        for ghost in [ghost for ghost in self.state['ghosts'] if ghost[1] == False]: # non zombie ghosts
            for [cA, cB] in self.map_.corr_adjacencies:
                if ghost[0] in cA.coordinates:     # pode dar erro: pesquisar [x,y] em (x,y)
                    cA.safe = CORRIDOR_SAFETY.UNSAFE
                    unsafe_corridors += [cA]
                elif ghost[0] in cB.coordinates:
                    cB.safe = CORRIDOR_SAFETY.UNSAFE
                    unsafe_corridors += [cB]
                else:
                    cA.safe = CORRIDOR_SAFETY.SAFE
                    cA.safe = CORRIDOR_SAFETY.SAFE
        logger.debug("UNSAFE_CORRIDORS:\n" + str(unsafe_corridors))
        return unsafe_corridors
            


    def calculate_ghosts_info(self):

        non_zombie_ghosts = [ghost for ghost in self.state['ghosts'] if ghost[1] == False]
        self.zombie_ghosts = [ghost for ghost in self.state['ghosts'] if ghost[1] == True]

        domain = Pathways(self.map_.corr_adjacencies, non_zombie_ghosts, self.map_)
        pacman = self.pacman_info.position
        pac_corridor = self.pacman_info.corridor
        ghosts_info = []
        #print('\n --------------- ')
        for [ghost,zombie,timeout] in non_zombie_ghosts: # non zombie ghosts
            # get the corridor the ghost is in to give as argument in search
            ghost_corr = None
            if ghost not in self.map_.ghosts_den:
                for corr in self.unsafe_corridors:
                    if ghost in corr.coordinates:
                        ghost_corr = corr
                        break

            # calculate trajectory of every ghost towards Pac-Man
            if ghost_corr != None: # if ghost is not in ghosts_den
                my_prob = SearchProblem(domain, ghost_corr, ghost, \
                                        self.pacman_info.corridor, pacman, \
                                        self.map_, self.state)
                my_tree = SearchTree(my_prob, "a*")
                #TODO if result is None, program breaks
                _, cost, path = my_tree.search()
                
               
                #print(str(ghost) + ' -> ' + str(cost) + ' -> ' + str(path))
            else:
                continue

            # the crossroad that the ghost will use to get to Pac-Man
            sub_corr0, sub_corr1 = pac_corridor.sub_corridors(pacman)
            if ghost in sub_corr0.coordinates:
                crossroad = pac_corridor.ends[0]
            elif ghost in sub_corr1.coordinates:
                crossroad = pac_corridor.ends[1]
            else:
                path_coordinates = [c for corr in path for c in corr.coordinates]
                if pac_corridor.ends[0] in path_coordinates:
                    crossroad = pac_corridor.ends[0]
                elif pac_corridor.ends[1] in path_coordinates:
                    crossroad = pac_corridor.ends[1]

                

            # calculate distance of every ghost to Pac-Man crossroads
            ghost_dist = cost - self.pacman_info.dist_to_crossroad(crossroad)

            # update self.ghosts_info with new attribute of distance_to_pacman
            ghosts_info += [Ghost_Info(ghost, zombie, timeout, ghost_corr, cost, crossroad, ghost_dist, path)]

        return ghosts_info



    def calculate_pacman_corridor(self):

        # Pac-Man position and his corridor (or list of corridors if Pac-Man is in crossroad)
        pacman = (self.state['pacman'])
        pac_corridors = [ adj for adj in self.map_.corr_adjacencies if pacman in adj[0].coordinates or pacman in adj[1].coordinates ]
        aux = [ adj[0] for adj in pac_corridors if pacman in adj[0].coordinates ]
        aux += [ adj[1] for adj in pac_corridors if pacman in adj[1].coordinates ]
        pac_corridors = list(set(aux))
        logger.debug("PACMAN POSITION:\n" + str(pacman))
        logger.debug("PACMAN CORRIDORS:\n" + str(pac_corridors))

        # Pac-Man might be at a crossroad. Choose unsafe corridor if available.
        pac_corridor = None
        for corr in pac_corridors:
            if corr.safe == CORRIDOR_SAFETY.UNSAFE:
                pac_corridor = corr
                break
        if pac_corridor == None:
            for corr in pac_corridors:
                if pacman in corr.coordinates:
                    pac_corridor = corr
                    break
        self.pacman_info.update_corridor(pac_corridor)
        logger.debug("PACMAN CHOSEN CORRIDOR:\n" + str(pac_corridor))



    def calculate_semaphores(self):
        """Attributes a SEMAPHORE color for each crossroad in Pac-Man's corridor
        by comparingthe distance of Pac-Man and the closest ghost to that
        crossroad

        Args:
        unsafe_corridors: list of corridors that have a ghost
        pac_corridor: the corridor Pac-Man is in
        pacman: the coordinates of Pac-Man position

        Returns:
        A dictionary with key = crossroad and value of a tuple with the distance
        of the ghost to Pac-Man and the distance of the ghost to the crossroad
        """

        logger.debug("########################################################")
        logger.debug("CALCULATE_SEMAPHORES()")
        logger.debug("########################################################")

        # get ends of Pac-Man corridor
        pacman = self.pacman_info

        # verify crossroads semaphores
        semaphores = {} # {crossroad : [Ghost_Info]}
        for ghost in self.ghosts_info:
            if frozenset(ghost.crossroad_to_pacman) not in semaphores:
                semaphores[frozenset(ghost.crossroad_to_pacman)] = [ghost]
            else: # gdt(p/c) -> ghost.dist_to_(pacman/crossroad)
                semaphores[frozenset(ghost.crossroad_to_pacman)] += [ghost]

        # select most dangerous ghost distancies
        pacman.semaphore0 = SEMAPHORE.GREEN
        pacman.semaphore1 = SEMAPHORE.GREEN
        for cross in semaphores:
            semaphores[cross] = min(semaphores[cross], key=lambda x : x.dist_to_crossroad)

        # compare distance of Pac-Man and ghosts to crossroads and
        # convert semaphores to colors
        for cross in semaphores:
            #print(str(cross) + ' -> ' + str(semaphores[cross]))
            #print(str(cross) + ', ' + str(frozenset(pacman.crossroad0)))
            if cross == frozenset(pacman.crossroad0):
                self.pacman_info.ghost_at_crossroad0 = semaphores[cross]
                #print('ADVISOR: ' + str(semaphores[cross]))
                dist_to_end = pacman.dist_to_crossroad0
                pacman.dist_to_ghost_at_crossroad0 = semaphores[cross].dist_to_pacman
                if semaphores[cross].crossroad_to_pacman == pacman.crossroad0:
                    pacman.crossroad0_is_blocked = semaphores[cross].dist_to_crossroad <= 0
                    pacman.pursued_from_crossroad0 = semaphores[cross].dist_to_pacman < SAFE_DIST_TO_GHOST

                if semaphores[cross].dist_to_crossroad > dist_to_end + 1:
                    pacman.semaphore0 = SEMAPHORE.GREEN
                elif semaphores[cross].dist_to_crossroad == dist_to_end + 1:
                    pacman.semaphore0 = SEMAPHORE.YELLOW
                else:
                    pacman.semaphore0 = SEMAPHORE.RED

            else:
                self.pacman_info.ghost_at_crossroad1 = semaphores[cross]
                #print('ADVISOR: ' + str(semaphores[cross]))
                dist_to_end = pacman.dist_to_crossroad1
                pacman.dist_to_ghost_at_crossroad1 = semaphores[cross].dist_to_pacman
                if semaphores[cross].crossroad_to_pacman == pacman.crossroad1:
                    pacman.crossroad1_is_blocked = semaphores[cross].dist_to_crossroad <= 0
                    pacman.pursued_from_crossroad1 = semaphores[cross].dist_to_pacman < SAFE_DIST_TO_GHOST

                if semaphores[cross].dist_to_crossroad > dist_to_end + 1:
                    pacman.semaphore1 = SEMAPHORE.GREEN
                elif semaphores[cross].dist_to_crossroad == dist_to_end + 1:
                    pacman.semaphore1 = SEMAPHORE.YELLOW
                else:
                    pacman.semaphore1 = SEMAPHORE.RED


    def boosts_analyser(self):
        """

        Args:

        Returns:
        """
        pass
