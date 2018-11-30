from game_consts import *
from static_analysis import Static_Analysis
from pathways import Pathways
from tree_search import SearchTree, SearchProblem
from corridor import Corridor
from strategy_advisor import Strategy_Advisor
import logging
import sys
import json
import asyncio
import websockets
import os
from mapa import Map





#$ PORT=80 SERVER=pacman-aulas.ws.atnog.av.it.pt python client.py
# to kill server: fuser 8000/tcp

# logger
# logs are written to file student.log after the client is closed
# possible messages: debug, info, warning, error, critical 
# how to use: logger.typeOfMessage('message')
logger = setup_logger('student', 'student.log')

# for debug purposes
debug = True


#! ##########   PAC-MAN AGENT GLOBAL STRATEGY   ##########

    #! ###    CONCEPTS    ###

    #! Corridor
        #* A list of path coordinates with only two adjacent coordinates
        #* and two crossroads as ends

    #! Crossroad
        #* A coordinate that joins corridors. The crossroad belong to all
        #* corridors it joins

    #! Corridor SAFE vs UNSAFE
        #* SAFE - Has no ghosts
        #* UNSAFE - Has one or more ghosts

    #! Crossroad GREEN - YELLOW - RED
        #* Refers to the crossroads directly accessible to Pac-Man (the
        #* ends of it's corridor)
        #* GREEN - No ghosts in proximity
        #* YELLOW - There are ghosts at a dangerous distance of the crossroad
        #*          (default = 1). Pac-Man can escape if he goes directly through
        #*          that end
        #* RED - Considering that the ghosts is in pursuit of Pac-Man, it is
        #*       impossible for Pac-Man to escape from that end before the ghost
        #*       gets to it (or the ghost is already inside Pac-Man's Corridor)


    #! Strategy Game Modes
        #* EATING_MODE - Pac-Man is safe. Focus on eating energies. Tries to
        #*               find closest energies through safest paths
        #* COUNTER_MODE - Pac-Man is almost surrounded. Focus on eating boosts.
        #* PURSUIT_MODE - Pac-Man is safe and there are zombie ghosts.
        #*               Focus on eating ghosts.
        #* FLIGHT_MODE - Pac-Man is almost surrounded. There are no boosts
        #*               available. Focus on finding the closest safest Corridor.

    #! Static Analysis of Map provides
        #* pathways
        #* corridors
        #* crossroads
        #* corridor_adjacencies
    
    #! Strategy Guidelines
        #* Pac-Man Agent calls Strategy Advisor
        #*      Strategy Advisor analyses:
        #*          Corridor Safety
        #*          Crossroads Semaphores
        #*          Distance to ghosts
        #*      Strategy Advisor advises a Game Mode
        #* Pac-Man calls Game Mode Agent to get next move
        #*      Game Mode tries to find the next move
        #* Pac-Man analyses next move
        #*      Is it specific (only one solution)
        #*          Pac-Man accepts next move
        #*      It's not specific (strategy was not correct)
        #*          Pac-Man calls Strategy Adjuster
        #*              Strategy Adjuster evaluates new info and advises a new Game Mode
        #*          Pac-Man call Game Mode Agent to get next move
        #*              Game Mode tries to find a solution
        #*          Pac-Man accepts best solution found (if more than one)



class Pacman_agent():
    """Creates the PACMAN agent that analyses the given 'Map' and 'state'
    to decide which direction to take and win the game 

    Args:
    map_: instance of Map for the current level

    Attr:
    map_: instance of Map for the current level
    static_analysis: instance of Static_Analysis containing:
                - pathways: list of all coordinates that are not walls
                - adjacencies: list of pairs of adjacent pathways
                - corridors: list of coordinates that create a corridor
                - crossroads: list of all coordinates that separate corridors
    """

    def __init__(self, map_,): 
        logger.warning('\n\n\n ========================== NEW EXECUTION ==========================\n')
        logger.debug('CREATING PACMAN AGENT\n')

        self.map_ = Static_Analysis(map_)
        self.debug = False

        logger.debug('CREATED PACMAN AGENT')


    def get_next_move(self, state):
        """Objective of Pacman_agent - calculates the next position using
        multiple auxiliar methods

        Args:
        state: a list of lists with the state of every element in the game

        Returns: the key corresponding to the next move of PACMAN
        """

        #logger.debug(nt("\nEnergy size is : " + str(len(state['energy'])) + "\n")

        

        # get advice on the next move
        strategy_advisor = Strategy_Advisor(self.map_, state)
        mode_handler = strategy_advisor.advise()
        if mode_handler == MODE.PURSUIT:
            mode_handler = MODE.EATING
        next_move = self.mode(mode_handler, strategy_advisor, state)



        # if advice is not specific, adjustments to the strategy may be needed
        if (next_move[1] == False): # correct when methods are implemented

            if mode_handler == MODE.EATING:
                if len(state['energy']) == 0:
                    return 'w' # w for win
                else:
                    if (len(state['boost']) > 0):
                        self.mode(MODE.COUNTER, strategy_advisor, state)
                    else:
                        self.mode(MODE.COUNTER, strategy_advisor, state)
            elif mode_handler == MODE.PURSUIT:
                next_move = self.mode(MODE.EATING, strategy_advisor, state)
            elif mode_handler == MODE.COUNTER:
                pass
            elif mode_handler == MODE.FLIGHT:
                pass
            else: # GARBAGE CODE
                strategy_adjuster = Strategy_Adjuster()
                mode_handler = strategy_adjuster.adjustStrategy()
                next_move = self.mode(mode_handler, state)
        
        # calculate and return the key
        # if (next_move == [5,23] or next_move == [6,7]):
        #     print("KEY IS " + str(self.calculate_key(state['pacman'], next_move)))

        # logger.debug("KEY IS " + str(self.calculate_key(state['pacman'], next_move)) + "\n\n")
        return self.calculate_key(state['pacman'], next_move[0][0][0])



    def mode(self, mode_handler, advisor, state):
        if mode_handler != MODE.EATING:
            print(mode_handler)
        if mode_handler == MODE.EATING:
            return  self.eating_agent(advisor, state, state['energy'] + state['boost'])
        elif mode_handler == MODE.FLIGHT:
            return  self.flight_agent(advisor)
        elif mode_handler == MODE.PURSUIT:
            return self.pursuit_agent_through_eating(advisor, state)
        else: # next_move == MODE.COUNTER
            return self.counter_agent(advisor, state)
        



    def calculate_key(self, pacman, next_move):
        """Calculates the 'wasd' key that corresponds to the next move

        Args:
        pacman: the coordinates of Pac-Man position
        next_move: the coordinates of the position to go to

        Returns:
        The 'wasd' key for moving from pacman to next_move
        """
        #print("NEXT MOVE: " + str(pacman) + ", " + str(next_move))
        px, py = pacman
        nx, ny = next_move



        if nx == px + 1:
            key = 'd'
        elif nx == px -1:
            key = 'a'
        elif ny == py + 1:
            key = 's'
        elif ny == py -1:
            key = 'w'
        elif nx > px:
            key = 'a'
        elif nx < px:
            key = 'd'
        elif ny > py:
            key = 'w'
        else:
            key = 's'
        
        return key



    def eating_agent(self, advisor, state, targets):

        pacman = advisor.pacman_info
        acessible_energies = []
        domain = Pathways(self.map_.corr_adjacencies, targets)
        possible_moves = []

    #--------------------------------------------------------------------------#
    # SEARCH FOR ENERGIES
  
        for energy in targets:
            
            # create domain to search
            
            # print("Energy #######################################")
            # print(energy)
            # print("#######################################")

            # find this energy corridor
            corridor = None
            for corr in self.map_.corridors:
                if energy in corr.coordinates:
                    corridor = corr
                    break

            # print("Corridor #######################################")
            # print(corridor)
            # print("#######################################")
            if (self.debug):
                pass
            
            # create problem and search
            my_prob = SearchProblem(domain, corridor, energy, pacman.corridor, pacman.position)
            my_tree = SearchTree(my_prob, "a*")
            search_results = my_tree.search()
            
            # filter valid results and store them in possible_moves
            if search_results != None:
                acessible_energies += [energy]
                possible_moves += [search_results]

        # if there are no possible moves, everything is eaten
        print(len(possible_moves))
        if len(possible_moves) == 0:
            return (possible_moves, False)

    #-------------------------------------------------------------------------#
    # SORT MOVES BY COST
        possible_moves = sorted(possible_moves,key=lambda res: res[1])


    #--------------------------------------------------------------------------#
    # SORT MOVES BY WHERE A GHOST IS BLOCKING THE NEXT CORRIDOR
        f_moves = []
        for move in possible_moves:
            if move[2][-3].safe == True:
                f_moves += [move]

        possible_moves = [move for move in possible_moves if move not in f_moves]
        possible_moves += f_moves


    #--------------------------------------------------------------------------#
    # SORT MOVES BY WHERE A GHOST IN PURSUIT IS CLOSER TO THE ENERGY THAN PAC-MAN
        f_moves = []
        BEST_GHOST_DIST_TO_ENERGY = 1000
        for move in possible_moves:

            next_move, cost, path = move
            energy_inside_corr = False
            clear_path = True
            
            # verify which ghost is blocking the path or if the path is clear
            if pacman.ghost_at_crossroad0 != None:
                #print('A: ' + str(pacman.ghost_at_crossroad0.position))
                #print('B: ' + str([c for lcoor in corr.coordinates for corr in path for c in lcoor]))
                if pacman.ghost_at_crossroad0.position in [c for lcoor in corr.coordinates for corr in path for c in lcoor]:
                    clear_path = False
                    ghost = pacman.ghost_at_crossroad0
                    
            if pacman.ghost_at_crossroad1 != None:
                if pacman.ghost_at_crossroad1.position in [ c for lcoor in corr.coordinates for corr in path for c in lcoor]:
                    clear_path = False
                    ghost = pacman.ghost_at_crossroad1

            if clear_path:
                f_moves += [move]
                continue

            # verify which crossroad is in the path
            crossroad = None
            if pacman.crossroad0 in [ c for lcoor in corr.coordinates for corr in path for c in lcoor]:
                crossroad = pacman.crossroad0
                #print('ps_cross0: ' + str(pacman.crossroad0))
            elif pacman.crossroad1 in [ c for lcoor in corr.coordinates for corr in path for c in lcoor]:
                crossroad = pacman.crossroad1
                #print('ps_cross1: ' + str(pacman.crossroad1))

            # if no crossroad is in the path, then the energy is inside the corridor
            # it's needed to verify from which crossroad is the energy will be accessed
            if crossroad == None:
                energy_inside_corr = True
                sub_corr0 = pacman.corridor.sub_corridors(pacman.position)[0].coordinates
                sub_corr1 = pacman.corridor.sub_corridors(pacman.position)[0].coordinates
                if any([ c in path for c in sub_corr0]):
                    crossroad = pacman.crossroad0
                elif any([ c in path for c in sub_corr1]):
                    crossroad = pacman.crossroad1

            # calculate distances of pacman and ghost to energy, according to
            # if energy is inside or outside pacman corridor

            # calculate distancies for when energy is in pacman corridor
            if energy_inside_corr:
                cross_to_energy = pacman.dist_to_crossroad(crossroad) - cost
                ghost_dist_to_energy = ghost.dist_to_crossroad + cross_to_energy
                #print(ghost_dist_to_energy)
                BEST_GHOST_DIST_TO_ENERGY = ghost_dist_to_energy if ghost_dist_to_energy < BEST_GHOST_DIST_TO_ENERGY else BEST_GHOST_DIST_TO_ENERGY
            # calculate distancies for when energy is NOT in pacman corridor
            else:
                cross_to_energy = cost - pacman.dist_to_crossroad(crossroad)
                ghost_dist_to_energy = ghost.dist_to_crossroad - cross_to_energy
                #print(ghost_dist_to_energy)
                BEST_GHOST_DIST_TO_ENERGY = ghost_dist_to_energy if ghost_dist_to_energy < BEST_GHOST_DIST_TO_ENERGY else BEST_GHOST_DIST_TO_ENERGY
            
            # if pacman distance to energy is smaller than ghost's, discard move
            if cost < ghost_dist_to_energy:
                f_moves += [move]

            # sort
            possible_moves = [move for move in possible_moves if move not in f_moves]
            possible_moves += f_moves

    #--------------------------------------------------------------------------#
    # FAKE ADJUSTER

        option = possible_moves[0]
        #print('closer ghosts: ' + str(BEST_GHOST_DIST_TO_ENERGY) + 'cost: ' + str(option[1]))
        if BEST_GHOST_DIST_TO_ENERGY < option[1]:
            return possible_moves, False



    #--------------------------------------------------------------------------#
    # RETURN OPTIONS

        return possible_moves, True
    

    def flight_agent(self, advisor):
        '''
        args:
        advisor: instance of Strategy_Advisor
                self.map_ = map_
                self.state = state
                self.unsafe_corridors = self.set_corridors_safety()
                self.pacman_info = Pacman_Info(state['pacman'])
                self.calculate_pacman_corridor()
                self.ghosts_info = self.calculate_ghosts_info()
        '''
                
        pac_info = advisor.pacman_info
        pac_crossroads = pac_info.crossroads

        pac_adj0, pac_safe_corr0 = self.calc_adj_and_safe(pac_info.corridor, pac_crossroads[0])
        print("---")
        print(pac_adj0)
        print("---")
        print(pac_safe_corr0)
        print("---")

        pac_adj1, pac_safe_corr1 = self.calc_adj_and_safe(pac_info.corridor, pac_crossroads[1])
        print(pac_adj1)
        print("---")
        print(pac_safe_corr1)
        ########################################################################
        ## PAC CORR UNSAFE #####################################################
        ########################################################################

        #corr pacman tem ghost do lado do crossroad0       
        if pac_info.crossroad0_is_blocked == True:

            #pacman esta encurralado (corr do pacman tem ghosts dos 2 lados)
            if pac_info.crossroad1_is_blocked == True:
                
                #escolhe lado com ghost mais afastado
                if pac_info.dist_to_ghost_at_crossroad0 >= pac_info.dist_to_ghost_at_crossroad1:
                    #escolhe crossroad0
                    return self.calc_next_coord(pac_info, pac_info.crossroad0, [])
                else:
                    #escolhe crossroad1
                    return self.calc_next_coord(pac_info, pac_info.crossroad1, [])

            #ghost no corr do pacman apenas do lado do crossroad0 -> crossroad0 is RED
            else:
    
                #pacman consegue fugir pelo crossroad1
                if pac_info.semaphore1 == SEMAPHORE.YELLOW:   

                    #ha corr safe
                    if pac_safe_corr1 != []:
                        #escolhe pac_safe_corr1[0]
                        return self.calc_next_coord(pac_info, pac_info.crossroad1, pac_safe_corr1)
                    
                    #NAO ha corr safe
                    else:
                        #escolhe corr com ghost mais afastado
                        #?return self.calc_corridor_ghost_farther(pac_info, pac_adj1, ghosts_info)
                        return self.calc_next_coord(pac_info, pac_info.crossroad1, pac_adj1)

                #pacman NAO consegue fugir pelo crossroad1 -> crossroad1 is RED
                else:
                    #escolhe crossroad1
                    return self.calc_next_coord(pac_info, pac_info.crossroad1, [])

        #corr do pacman NAO tem ghost do lado crossroad0
        else:

            #corr do pacman tem ghost apenas do lado crossroad1 -> crossroad1 is RED
            if pac_info.crossroad1_is_blocked == True:

                #pacman consegue fugir apenas pelo crossroad0
                if pac_info.semaphore0 == SEMAPHORE.YELLOW:
                    #crossroad0 liga a corr SAFE
                    if pac_safe_corr0 != []:
                        #escolhe pac_safe_corr0[0]
                        return self.calc_next_coord(pac_info, pac_info.crossroad0, pac_safe_corr0)
                    
                    #NAO ha corr SAFE pelo crossroad0
                    else:
                        #escolhe corr com ghost mais afastado
                        #?return self.calc_corridor_ghost_farther(pac_info, pac_adj0, ghosts_info)
                        return self.calc_next_coord(pac_info, pac_info.crossroad0, pac_adj0)

                #pacman NAO consegue fugir por nenhum crossroad -> crossroad0 is RED
                else:
                    #escolhe lado com ghost mais afastado
                    #?return self.calc_corridor_ghost_farther(pac_info, pac_adj0 + pac_adj1, ghosts_info)
                    return self.calc_next_coord(pac_info, pac_info.crossroad0, [])


            ####################################################################
            ## PAC CORR SAFE ###################################################
            ####################################################################

            #corr do pacman NAO tem ghosts -> crossroad[0].SAFE and crossroad[1].SAFE
            else:
                
                #pacman consegue fugir pelo crossroad0
                if pac_info.semaphore0 == SEMAPHORE.YELLOW:
                
                    #pacman consegue fugir por qualquer crossroad
                    if pac_info.semaphore1 == SEMAPHORE.YELLOW:

                        #crossroad0 liga a corr SAFE
                        if pac_safe_corr0 != []:
                            #ambos os crossroads ligam a corr SAFE
                            if pac_safe_corr1 != []:
                                #escolhe o crossroad mais longe
                                #crossroad0 mais longe do pacman
                                if pac_info.dist_to_crossroad0 >= pac_info.dist_to_crossroad1:
                                    #escolhe pac_safe_corr0[0]
                                    return self.calc_next_coord(pac_info, pac_info.crossroad0, pac_safe_corr0)

                                #crossroad1 mais longe do pacman    
                                else:
                                    #escolhe pac_safe_corr1[0]
                                    return self.calc_next_coord(pac_info, pac_info.crossroad1, pac_safe_corr1)

                            #apenas crossroad0 liga a corr SAFE
                            else:
                                #escolhe pac_safe_corr0[0]
                                return self.calc_next_coord(pac_info, pac_info.crossroad0, pac_safe_corr0)
                        
                        #crossroad0 nao liga a corr SAFE
                        else:
                            #apenas crossroad1 liga a corr SAFE
                            if pac_safe_corr1 != []:
                                #escolhe pac_safe_corr1[0]
                                return self.calc_next_coord(pac_info, pac_info.crossroad1, pac_safe_corr1)

                            #NAO ha corr SAFE        
                            else:
                                #escolhe corr com ghost mais afastado
                                #?return self.calc_corridor_ghost_farther(pac_info, pac_adj0 + pac_adj1, ghosts_info)
                                return self.calc_next_coord(pac_info, pac_info.crossroad0, pac_adj0)#, return self.calc_next_coord(pac_info.position, pac_info.crossroad1)
                    
                    #pacman consegue fugir apenas pelo crossroad0
                    else:

                        #crossroad0 liga a corr SAFE
                        if pac_safe_corr0 != []:
                            #escolhe pac_safe_corr0[0]
                            return self.calc_next_coord(pac_info, pac_info.crossroad0, pac_safe_corr0)
                        
                        #NAO ha corr SAFE pelo crossroad0
                        else:
                            #escolhe corr com ghost mais afastado
                            #?return self.calc_corridor_ghost_farther(pac_info, pac_adj0, ghosts_info)
                            return self.calc_next_coord(pac_info, pac_info.crossroad0, pac_adj0)
                
                #pacman NAO consegue fugir pelo crossroad0
                else:

                    #pacman consegue fugir apenas pelo crossroad1
                    if pac_info.semaphore1 == SEMAPHORE.YELLOW:
                        #crossroad1 liga a corr SAFE
                        if pac_safe_corr1 != []:
                            #escolhe pac_safe_corr1[0]
                            return self.calc_next_coord(pac_info, pac_info.crossroad1, pac_safe_corr1)
                        
                        #NAO ha corr SAFE pelo crossroad1
                        else:
                            #escolhe corr com ghost mais afastado
                            #?return self.calc_corridor_ghost_farther(pac_info, pac_adj1, ghosts_info)
                            return self.calc_next_coord(pac_info, pac_info.crossroad1, pac_adj1)

                    #pacman NAO consegue fugir por nenhum crossroad
                    else:
                        #escolhe lado com ghost mais afastado
                        #?return self.calc_corridor_ghost_farther(pac_info, pac_adj0 + pac_adj1, ghosts_info)
                        return self.calc_next_coord(pac_info, pac_info.crossroad0, [])


    def calc_adj_and_safe(self, pac_corr, crossroad):
        adj = [[cA, cB] for [cA, cB] in self.map_.corr_adjacencies\
                                        if crossroad in cA.ends\
                                        or crossroad in cB.ends]
           
        safe = [[cA, cB] for [cA, cB] in adj\
                            if (cA.coordinates == pac_corr.coordinates and cB.safe == CORRIDOR_SAFETY.SAFE)\
                            or (cB.coordinates == pac_corr.coordinates and cA.safe == CORRIDOR_SAFETY.SAFE)]

        return adj, safe
                

    def calc_next_coord(self, pac_info, end, adj_end):
        '''
            Args:
            pac_info:   advisor.pacman_info
            end     :   crossroad do lado escolhido para o pacman fugir
            adj_end :   lista de corredores adjacentes ao end
                        - adj_end == [] é porque o pacman não consegue fugir pelo end
                                        tanto por existir um fantasma no mesmo corredor desse lado
                                        tanto por o end ser RED
        '''

        [px, py] = pac_info.position
        
        next_move_pac_corr = [ coord for coord in pac_info.corridor.coordinates\
                                        if coord == [px-1, py]\
                                        or coord == [px+1, py]\
                                        or coord == [px, py-1]\
                                        or coord == [px, py+1]]

        #pacman esta num crossroad
        if len(next_move_pac_corr) == 1:
            print(adj_end)
            next_moves = [ coord for corridor in adj_end\
                                    for coord in [corridor.get_coord_next_to_end(end)]]

            return next_moves[0]

        #pacman NAO está num crossroad
        else:      

            [ex, ey] = end

            next_coord = next_move_pac_corr[0]
            dx = abs(ex - next_coord[0])
            dy = abs(ey - next_coord[1])

            for i in range(1, len(next_move_pac_corr)):

                [a,b] = next_move_pac_corr[i]
                da = abs(ex-a)
                db = abs(ey-b)

                if py == ey:
                    next_coord, dx, dy = [[a,b], da, db] if da<dx else [next_coord, dx, dy]
                elif px == ex:
                    next_coord, dx, dy = [[a,b], da, db] if db<dy else [next_coord, dx, dy]
                else:
                    next_coord, dx, dy = [[a,b], da, db] if (da==dx and db<dy)\
                                                            or (db==dy and da<dx)\
                                                         else [next_coord, dx, dy]

            return next_coord




    #escolhe corr com ghost mais afastado
    #TODO not done
    def calc_corridor_ghost_farther(self, pac_info, pac_adj, ghosts_info):
        dist = 0
        corr = []
        for adj_corr in pac_adj:
            for g_info in ghosts_info:
                if g_info.corridor == adj_corr and dist < g_info.dist_to_pacman:
                    dist = g_info.dist_to_pacman
                    corr = g_info.corridor                                                   
        
        #TODO devolver prox coord
        pass

    
    def pursuit_agent(self, advisor, state):
        """Calculates the next position of the next move, when in pursuit mode.
        In Counter Mode, Pac-Man is must focus on eating zombie ghosts.
        
        Args:
        advisor
        state

        Returns:
        The [x,y] position of the next_move
        """

        #<pathways.Pathways object at 0x7fc182823208> [[2, 26], [2, 25], [2, 24], [2, 23], [1, 23], [1, 22], [1, 21], [1, 20], [2, 20], [3, 20], [4, 20]] [1, 22] [[14, 15], [15, 15], [16, 15], [17, 15], [18, 15], [0, 15], [1, 15], [2, 15], [3, 15], [4, 15]] [3, 15]
       
        eatable_ghosts = state['ghosts'].copy()
        eatable_ghosts[1][1] = True # FOR TESTING PURPOSES
        
        eatable_ghosts = [ghost[0] for ghost in eatable_ghosts if ghost[1]]    #only get the positions
        
        acessible_ghosts = []
        possible_moves   = []
        safeties         = []

        
        for ghost in eatable_ghosts:
            domain = Pathways(self.map_.corr_adjacencies.copy(), eatable_ghosts)

            corridor = None
            for corr in self.map_.corridors:
                if ghost in corr.coordinates:
                    corridor = corr
                    safety = corridor.safe
            
            #print(domain, corridor, ghost, advisor.pacman_info.corridor, advisor.pacman_info.position)
            my_prob = SearchProblem(domain, corridor, ghost, advisor.pacman_info.corridor, advisor.pacman_info.position)
            my_tree = SearchTree(my_prob, "a*")
            search_results = my_tree.search()
            
            if search_results != None:
                #? avoid repetead boosts
                if ghost not in acessible_ghosts:
                    acessible_ghosts += [ghost]
                    possible_moves   += [(search_results[0], search_results[1])]
                    safeties         += [safety]

        if len([safety for safety in safeties if safety == CORRIDOR_SAFETY.SAFE]): #if any corridor is safe
            #remove unsafe corridors info
            for i in range(0, len(acessible_ghosts)):
                if safeties[i] == CORRIDOR_SAFETY.UNSAFE:
                    del safeties[i]
                    del acessible_ghosts[i]
                    del possible_moves[i]        

        # should not be on this mode (no more zombie ghost)
        if (len(possible_moves) == 0):
            return False
        
        # choose the closest zombie ghost 
        # either there are several ghost in a safe corridor 
        # OR there are only ghost in unsafe corridors)
        possible_moves = sorted(possible_moves,key=lambda elem: elem[1])
        return possible_moves[0][0]







    def pursuit_agent_through_eating(self, advisor, state):
        """Calculates the next position of the next move, when in pursuit mode.
        In Counter Mode, Pac-Man is must focus on eating zombie ghosts.
        
        Args:
        advisor
        state

        Returns:
        The [x,y] position of the next_move
        """
        
        zombie_ghosts = [ghost for ghost in state['ghosts'] if ghost[1]]    #only get the positions
        possible_moves   = []

        # call eating agent for zombies not in den
        for ghost in zombie_ghosts:
            for corr in self.map_.corridors:
                if ghost[0] in corr.coordinates:
                    possible_moves += self.eating_agent(advisor, state, [ghost[0]])[0]
                    break


    #--------------------------------------------------------------------------#
    # SORT MOVES BY ZOMBIES TIMEOUT

        f_moves = []
        for move in possible_moves:
            _, cost, path = move
            ghosts = [ghost for ghost in zombie_ghosts if ghost[0] == path[0].coordinates[0]]
            ghost = sorted(ghosts, key=lambda g: g[2])[0]
            if cost > ghost[2] * 2:
                f_moves += [move]
                    
        # sort
        possible_moves = [move for move in possible_moves if move not in f_moves]

    #--------------------------------------------------------------------------#
    # IF THERE ARE NO POSSIBLE MOVES, RETURN NONE

        if possible_moves == []:
            return possible_moves, False
        return possible_moves, True
                






    def counter_agent(self, advisor, state):
        """Calculates the next position of the next move, when in counter mode.
        In Counter Mode, Pac-Man is almost surrounded by ghosts and must focus on eating boosts.
        
        Args:
        advisor
        state

        Returns:
        The [x,y] position of the next_move

        Considerations/Strategy:
        -> For each corridor where the boosts are, check for safe ones
        -> From the safest ones, choose the closest (if no one is safe, choose the closest one)
        
        ghost [[9, 15], False, 0],
        """
        boosts = state['boost']
        acessible_boosts = []
        possible_moves   = []
        safeties         = []

        domain = Pathways(self.map_.corr_adjacencies, boosts)

        for boost in boosts:
            
            corridor = None
            for corr in self.map_.corridors:
                if boost in corr.coordinates:
                    corridor = corr

            my_prob = SearchProblem(domain, corridor, boost, advisor.pacman_info.corridor, advisor.pacman_info.position)
            my_tree = SearchTree(my_prob, "a*")
            search_results = my_tree.search()
            
            if search_results != None:
                acessible_boosts += [boost]
                possible_moves += [(search_results[0], search_results[1])]
                safeties         += [search_results[2][len(search_results[2]) - 3].safe]        #safety of two to last corridor

        # print("BOOSTS"   + str(acessible_boosts) + "\n")
        # print("MOVES"    + str(possible_moves)+ "\n")
        # print("SAFETIES" + str(safeties)+ "\n")
        
    #-------------------------------------------------------------------------#
    # SORT MOVES BY COST
        possible_moves = sorted(possible_moves,key=lambda res: res[1])



        other_choices = []
        blocked = True

        if len([safety for safety in safeties if safety == CORRIDOR_SAFETY.SAFE]) > 1: #if any corridor is safe
            blocked = False
            #remove unsafe corridors info
            for i in range(0, len(acessible_boosts)):
                if safeties[i] == CORRIDOR_SAFETY.UNSAFE:
                    other_choices += possible_moves[i]
                    
                    del safeties[i]
                    del acessible_boosts[i]
                    del possible_moves[i]        

        # should not be on this mode (no more boosts)
        if (len(possible_moves) == 0):
            return possible_moves, False
        
        # choose the closest boost 
        # either there are several boosts in a safe corridor 
        # OR there are only boosts in unsafe corridors)
        
        possible_moves = sorted(possible_moves,key=lambda elem: elem[1])
        other_choices += [possible_move[0] for possible_move in possible_moves[1:]]
        #response = ModeResponse(possible_moves[0][0], other_choices, blocked)
        #print(response)
        return possible_moves, True


#------------------------------------------------------------------------------#
#------------------------------------------------------------------------------#
async def agent_loop(server_address = "localhost:8000", agent_name="student"):
    async with websockets.connect("ws://{}/player".format(server_address)) as websocket:

        #----------------------------------------------------------------------#
        # Receive information about static game properties 
        await websocket.send(json.dumps({"cmd": "join", "name": agent_name}))
        msg = await websocket.recv()
        game_properties = json.loads(msg)
        #----------------------------------------------------------------------#
        
        
        # Create the pacman agent
        pacman = Pacman_agent(Map(game_properties['map']))

        # play!
        while True:
            #------------------------------------------------------------------#
            r = await websocket.recv()
            state = json.loads(r) #receive game state

            # game over (unnecessary for actual play
            if state['lives'] == 0:
                print("GAME OVER")
                return
            #------------------------------------------------------------------#

            
            #print(state)
            # get next move from pacman agent
            key = pacman.get_next_move(state)

            
            #-send new key-----------------------------------------------------#
            await websocket.send(json.dumps({"cmd": "key", "key": key}))
            #------------------------------------------------------------------#

loop = asyncio.get_event_loop()
SERVER = os.environ.get('SERVER', 'localhost')
PORT = os.environ.get('PORT', '8000')
NAME = os.environ.get('NAME', 'student')
loop.run_until_complete(agent_loop("{}:{}".format(SERVER,PORT), NAME))

#------------------------------------------------------------------------------#
#------------------------------------------------------------------------------#