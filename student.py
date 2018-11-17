#from tree_search import *
import random
import logging

#$ PORT=80 SERVER=pacman-aulas.ws.atnog.av.it.pt python client.py
# to kill server: fuser 8000/tcp

# for debug purposes
debug = True


# logs are written to file logger.log after the client is closed
# possible messages: debug, info, warning, error, critical 
# how to use: logging.typeOfMessage('message')

if (debug):
    logger = logging.getLogger('student_logger')
    logger_format = '[%(lineno)s - %(funcName)20s() - %(levelname)s]\n %(message)s\n'
    #logger_format = '%(levelname)s:\t%(message)' # simpler format

    # currently writing over the logger file, change filemode to a to append
    logging.basicConfig(format=logger_format, filename='logger.log', filemode='w', level=logging.DEBUG)

class Pacman_agent():
    """Creates the PACMAN agent that analyses the given 'Map' and 'state'
    to decide which direction to take and win the game 

    Args:
    map_: instance of Map for the current level

    Attr:
    map_: instance of Map for the current level
    pathways: list of all coordinates that are not walls
    adjacencies: list of pairs of adjacent pathways
    corridors: list of coordinates that create a corridor
    crossroads: list of all coordinates that separate corridors
    """


    def __init__(self, map_): 
        if debug:
            logger.warning('\n\n\n ========================== NEW EXECUTION ==========================\n')
            logger.debug('CREATING PACMAN AGENT\n')

        # static info from mapa.py Map
        self.map_ = map_
        print(self.map_.ghost_spawn)
        self.pathways = self.create_pathways_list()
        self.crossroads = self.create_crossroads_list(self.pathways)
        self.adjacencies, self.cae0ad115ec86ac73b730a6fa08032ebfe40afa71orridors = self.create_static_maps(self.pathways, self.crossroads)
        self.corr_adjacencies =self.create_corridor_adjacencies(self.corridors, self.crossroads)

        if debug:
            logger.debug('CREATED PACMAN AGENT')

        


    def get_next_move(self, state):
        """Objective of Pacman_agent - calculates the next position using
        multiple auxiliar methods

        Args:
        state: a list of lists with the state of every element in the game

        Returns: the key corresponding to the next move of PACMAN
        """

        #logger.debug(nt("\nEnergy size is : " + str(len(state['energy'])) + "\n")
        # create a vector for every element in the game
        # every element points pacman teh next move to get to it
        vectors = []
        #logger.debug(nt(state['energy'])
        
        pac_pos = (state['pacman'][0], state['pacman'][1])
        # if debug:
        #     logger.debug("\t pacman is in position " + str(pac_pos))

        ex, ey = self.get_vector(nodes_to_search=state['energy'], pac_pos=pac_pos)
        #(gx, gy) = self.get_vector(state['ghosts'], pac_pos)

        #sum the vectors
        vec_x = ex #+ (-10*gx)
        vec_y = ey #+ (-10*gy)

        # calculate the key to send
        if abs(vec_x) > abs(vec_y):
            if vec_x > 0:
                key = 'd'
            else:
                key = 'a'
        elif abs(vec_x) < abs(vec_y):
            if vec_y > 0:
                key = 's'
            else:
                key = 'w'
        elif abs(vec_x) == abs(vec_y):
            if vec_x > 0 and vec_y > 0:
                key = random.choice('sd')
            elif vec_x > 0 and vec_y < 0:
                key = random.choice('dw')
            elif vec_x < 0 and vec_y < 0:
                key = random.choice('aw')
            elif vec_x < 0 and vec_y > 0:
                key = random.choice('as')
            elif vec_x == 0:
                logger.warning("There is a problem not solved yet in this line of code!")
        
        if debug:
            logger.debug('The key is: ' + str(key))


        # x, y = state['pacman']
        # if x == cur_x and y == cur_y:
        #     if key in "ad":
        #         key = random.choice("ws")
        #     elif key in "ws":
        #         key = random.choice("ad")
        # cur_x, cur_y = x, y

        return key


    def get_vector(self, nodes_to_search, pac_pos):
        """Calculates the vector given by an element

        Args:
        nodes_to_search -- 
        pac_pos         -- coordinates of PACMAN position

        Returns:

        """
        i = 0
        next_pos = []
        vectors = []
        # if debug:
        #     logger.debug("***********************************************************")
        #     logger.debug('\t get vector was called! ')
        #     logger.debug("***********************************************************")

        # convert list to dictionary with zero weight for each element
        weight_dict = { (x,y):1 for [x,y] in nodes_to_search }

        for (x,y) in nodes_to_search:

            # if debug:
                # logger.debug("#######################################################")
                # logger.debug('\t calculating vector for pos: ' + str((x,y)))
                # logger.debug("#######################################################")
        
            # if debug:
            #     logger.debug("\t cycle  for position " + str((x,y)))

            # search the path
            # if debug:
            #     logger.debug("SearchDomain being called to create")
            domain = Pathways(self.adjacencies)

            # if debug:
            #     logger.debug("SearchProblem " + str(i) + " being called to create")
            my_prob = SearchProblem(domain,(x,y),pac_pos)
            
            # if debug:
            #     logger.debug("SearchTree " + str(i) + " being called to create")
            my_tree = SearchTree(my_prob, weight_dict, self.strategy)
            
            next_result = my_tree.search()

            if next_result != None:
                next_res, next_cost = next_result
                next_pos += [((x,y) , next_res, next_cost)]
            else:
                next_pos += [((x,y), pac_pos, 0)]

            #logger.debug((x,y))
            #logger.debug(next_result)
            
            #logger.debug("\t search " + str(i) + " was completed!")

            # if debug:
            #     logger.debug('\t Calculating next move for position: ' + str((x,y)))

        #logger.debug(next_pos)

        for i in range(len(next_pos)):
            if next_pos[i][1] != pac_pos:
                pac_x, pac_y = pac_pos
                next_x, next_y = (next_pos[i])[1]
                x = pac_x - next_x
                y = pac_y - next_y
                if (x == 1):
                    dir = ( ( -(1/next_pos[i][2])) , 0 )
                elif (x == -1):
                    dir = ( ( (1/next_pos[i][2])) , 0 )
                elif (y == 1):
                    dir = ( 0 , (-(1/next_pos[i][2])) )
                elif (y == -1):
                    dir = ( 0 , ((1/next_pos[i][2])) )
                elif (x > 1):
                    dir = ( ((1/next_pos[i][2])) , 0 )
                elif (x < 1):
                    dir = ( (-(1/next_pos[i][2])) , 0 )
                elif (y > 1):
                    dir = ( 0 , ((1/next_pos[i][2])) )
                elif (y < 1):
                    dir = ( 0 , (-(1/next_pos[i][2])) )
                vectors += [dir]

                logger.debug(str(next_pos[i][0]) + " : vector is: " + str(dir))
            
            # if debug:
            #     logger.debug("#######################################################")
            #     logger.debug('\t Vector is ' + str(dir))
            #     logger.debug("#######################################################")

        #logger.debug(weight_dict)



        # sum all the vectors
        vec_x = 0
        vec_y = 0
        for (x,y) in vectors:
            vec_x += x
            vec_y += y
        
        #logger.debug("\npacman is in position " + str(pac_pos[0], pac_pos[1]))
        #logger.debug('Sum of all vectors is: ' + str(vec_x) + ', ' + str(vec_y) + "\n")

        if debug:
            logger.debug("#######################################################")
            logger.debug('\t Vector is ' + str((vec_x, vec_y)))
            logger.debug("#######################################################")

        return [vec_x, vec_y]





    def calculate_key(self, vector):
        """Calculates the 'wasd' key that corresponds to the next move

        Keyword arguments:
        vector -- the vector that represents next PACMAN move
        """



    def calculate_next_move_direction(self, pac_pos, next_pos):
        """Calculates direction of next PACMAN move

        Keyword arguments:
        pac_pos     -- coordinates of PACMAN position
        next_pos    -- coordinates of next PACMAN move
        """



    def sum_vectors(self, vectors):
        """Sums all vectors

        Keyword arguments:
        vectors -- a list of vectors
        """



    def combinations(self, list_, n):
        """Generates all combinations of the elements in a list

        Keyword arguments:
        list_   -- a list
        n       -- number of elements per combination
        """
        if n==0: yield []
        else:
            for i in range(len(list_)):
                for elem in self.combinations(list_[i+1:],n-1):
                    yield [list_[i]] + elem

    

    def print_debug_block(self, string, var):
        """Prints a debug bar

        Keyword arguments:
        list_   -- a list
        n       -- number of elements per combination
        """
        #logger.debug("#######################################################")
        #logger.debug('\t ' + string + ' is: ')
        #logger.debug("#######################################################")
        #logger.debug(var)


################################################################################
#####################   STATIC ANALYSIS AUXILIAR METHODS   #####################
################################################################################
    
    #* ##########   TESTED AND VERIFIED   ##########"""
    def create_pathways_list(self):
        """Create a list with all coordinates that are not walls

        Returns:
        Tuple of lists (for efficiency purposes):
        pathways_hor: pathways organized by row
        pathways_ver: pathways organized by column
        """

        # find ghosts den. This area will not be used in any search or strategy
        # and should be avoided by PACMAN
        ghosts_den = self.get_ghosts_den(self.map_)

        pathways_hor = []
        for y in range(self.map_.ver_tiles):
            for x in range(self.map_.hor_tiles):
                
                if not self.map_.is_wall((x,y)): 
                    pathways_hor += [(x,y)]

        pathways_hor = [ p for p in pathways_hor if p not in ghosts_den ]
        pathways_ver = sorted(pathways_hor, key=lambda y: (x,y))

        if True:
            self.print_debug_block('ghosts_den', ghosts_den)
            self.print_debug_block('pathways_hor', pathways_hor)
            self.print_debug_block('pathways_ver', pathways_ver)

        return pathways_hor, pathways_ver

#------------------------------------------------------------------------------#
    
    def create_crossroads_list(self, pathways):
        """Create a list with all coordinates that are crossroads

        Args:
        pathways: tuple with two list with all coordinates that are not walls

        Returns:
        crossroads: list of all coordinates that are crossroads:
        """

        pathways_hor, _ = pathways
        crossroads = []
        for (x,y) in pathways_hor:
            adj = 0
            if x > 0 and not self.map_.is_wall((x-1,y)):
                adj += 1
            if x < self.map_.hor_tiles-1 and not self.map_.is_wall((x+1,y)):
                adj += 1
            if y > 0 and not self.map_.is_wall((x,y-1)):
                adj += 1
            if y < self.map_.ver_tiles-1 and not self.map_.is_wall((x,y+1)):
                adj += 1
            if adj > 2:
                crossroads += [(x,y)]

        if debug:
            self.print_debug_block('crossroads', crossroads)

        return crossroads

#------------------------------------------------------------------------------#

    def get_ghosts_den(self, map_, pos=(-1, -1), den=[], ):
        """delimit the coordinates that make up the ghosts den

        Args:
        ghost_spawn: coordinates where ghosts spawn (usually the center of den)
        dirs       : directions to search into (by default left, right, up, down)

        Returns:
        crossroads: list of coordinates that make up the ghosts den:
        """

        # get ghots spawn point (which is a point part of the den)
        spawn = self.map_.ghost_spawn
        if pos == (-1,-1):
            pos = spawn
        
        logger.debug("SPAWN POINT IS: " + str(pos))
        
        possible_dirs =[(-1,0), (1,0), (0, 1), (0, -1)]
        pos_x, pos_y = pos
        den_corners = []

        # to_visit is a queue with positions to visit
        # each position is a tuple (pos_x, pos_y, list of possible directions)
        to_visit = [(pos_x, pos_y, possible_dirs)]     
        
        #DEBUG
        add = 0
        COUNTING = 0

        while len(to_visit) > 0:
            # "pop" element from queue to_visit
            x, y, dirs = to_visit[0]
            to_visit = to_visit[1:] 

            logger.debug("===============================================================================================")
            logger.debug("Removed " + str((x, y, dirs)))
            
            count = 0
            adj_walls = []

            for direction in dirs:
                dir_x, dir_y = direction    
                remaining_dirs = [dir for dir in dirs if dir != direction]

                logger.debug("==========================")
                logger.debug("Following direction " + str(direction) + " from " + str((x, y)))
                logger.debug("Remaining directions: " + str(remaining_dirs))

                #* OK
                new_pos = x + dir_x, y + dir_y
                logger.debug("New pos to analyze: " + str(new_pos))

                if (self.map_.is_wall(new_pos)):
                    logger.debug("Detected wall at " + str(new_pos) + " dir " + str(direction))

                    # clean up the list based on zones
                    # todo can only cleanup when valid adjacencies are found!
                    if (direction == (1, 0)): #clean up right part
                        logger.debug(to_visit)
                        logger.debug("Clean right part")
                        #to_visit = [visit for visit in to_visit if visit[0] == x or visit[0] < spawn[0]]
                        logger.debug(to_visit)
                    elif (direction == (-1, 0)): #clean up left part
                        logger.debug(to_visit)
                        logger.debug("Clean left part")
                        #to_visit = [visit for visit in to_visit if visit[0] == x or visit[0] > spawn[0]]
                        logger.debug(to_visit)
                    elif (direction == (0, 1)): #clean up down part
                        logger.debug(to_visit)
                        logger.debug("Clean down part")
                        #to_visit = [visit for visit in to_visit if visit[1] == y or visit[1] > spawn[1]]
                        logger.debug(to_visit)
                    elif (direction == (0, -1)): #clean up up part
                        logger.debug(to_visit)
                        logger.debug("Clean up part")
                        #to_visit = [visit for visit in to_visit if visit[1] == y or visit[1] < spawn[1]]
                        logger.debug(to_visit)
                    
                    count += 1
                    adj_walls += [new_pos]
                  

                else:
                    # todo improve comments
                    # if it's not a wall, we add the position to the positions to visit. 
                    # from that position we can go to the remaning_dirs + the oposite direction of where it came from
                    logger.debug("No Detected wall.\n Adding " +  str (new_pos) + " to visit")
                    #to_visit += list(set([(x + dir_x, y + dir_y, [(dir_x * -1, dir_y * -1)] + remaining_dirs)]))
                    #if COUNTING < 8:
                    possible_dirs = [direction] + [direct for direct in remaining_dirs if direct != (dir_x * -1, dir_y * -1)]
                    to_visit += [(x + dir_x, y + dir_y, possible_dirs)]
                        #COUNTING =0
                    logger.debug("Result is: " + str(to_visit))
            
            if count == 2: # corner has 2 adjacent walls

                # verify if adjacent walls are valid
                wall1_x, wall1_y = adj_walls[0]
                wall2_x, wall2_y = adj_walls[1]
                print((wall1_x, wall1_y))
                print((wall2_x, wall2_y))
                if (abs(wall1_x - wall2_x) == 1 and abs(wall1_y - wall2_y) == 1):
                # we can have repeteaded corners 
                # we can reach corners from different paths
                    print("ADDING CORNER")
                    print(den_corners + [(x, y)])
                    den_corners = list(set( den_corners + [(x, y)] ) )
                    # clean up to_visit

                    # identify corner
                    if (x < spawn[0]):
                        if (y > spawn[0]): # left up corner
                            print("Clean left up")
                            to_visit = [visit for visit in to_visit if visit[0] > spawn[0] or (visit[0] < spawn[0] and visit[1] < spawn[1])]
                        if (y < spawn[0]): # left down corner
                            print("Clean left down")
                            to_visit = [visit for visit in to_visit if visit[0] > spawn[0] or (visit[0] < spawn[0] and visit[1] > spawn[1])]
                    elif (x > spawn[0]):
                        if (y > spawn[0]): # right up corner
                            print("Clean right up")
                            to_visit = [visit for visit in to_visit if visit[0] < spawn[0] or (visit[0] > spawn[0] and visit[1] < spawn[1])]
                        if (y < spawn[0]): # right down corner
                            print("Clean right down")
                            to_visit = [visit for visit in to_visit if visit[0] < spawn[0] or (visit[0] > spawn[0] and visit[1] > spawn[1])]
                    
                    if (len(den_corners) == 4):
                        print("FOUND ALL 4 CORNERS! ")
                        print("RETURNING " + str(den_corners))
                        return den_corners
                
          
                    

            #DEBUG
            if (add == 1 and len(to_visit) == 0 ):
                to_visit += [(8, 15, possible_dirs)]
                to_visit += [(10, 15, possible_dirs)]
                to_visit += [(9, 14, possible_dirs)]
                to_visit += [(9, 15, possible_dirs)]
                add = 0
        
        return []
        
    

#------------------------------------------------------------------------------#

    def create_static_maps(self, pathways, crossroads):
        """Creates a list with all adjacencies of coordinates that are not walls
        Uses two cycles for horizontal and vertical adjacencies for efficiency
        purposes

        Args:
        pathways: a tuple of list of the coordinates that are not walls

        Returns: A tuple with 2 lists
        adjacencies: list with pairs of adjacent coordinates
        corridors: list with groups of horizontal and vertical Corridors
        """

        pathways_hor, pathways_ver = pathways
        adjacencies = []
        corridors = []
        tunnel_points = []

        # horizontal search
        (x,y) = pathways_hor[0]
        corridor = [(x,y)]
        i = 0
        for i in range(1,len(pathways_hor)):

            (a,b) = pathways_hor[i]

            # check for row change (coordinates are not adjacent)
            if b != y:
                if len(corridor) > 1: # length 1 is a section of a vertical corridor
                    corridors += [corridor]
                corridor = [(a,b)]
                (x,y) = (a,b)
                continue

            # if horizontally adjacent, add to adjacencies, add to current
            # horizontal corridor
            if a == x+1:
                adjacencies += [((x,y),(a,b))]
                corridor += [(a,b)]
                if (a,b) in crossroads:
                    corridors += [corridor]
                    corridor = [(a,b)]
            else:
                if len(corridor) > 1: # length 1 is a section of a vertical corridor
                    corridors += [corridor]
                corridor = [(a,b)]

            # check for spherical map adjacencies
            if a == self.map_.hor_tiles-1:
                (i,j) = [ (i,j) for (i,j) in pathways_hor if i == 0 and j == b ][0]
                adjacencies += [((i,j),(a,b))]
                tunnel_points += [(i,j)]
                tunnel_points += [(a,b)]

            (x,y) = (a,b)
        
        # add last horizontal adjacency
        if i == len(pathways_hor) -1:
            adjacencies += [(pathways_hor[len(pathways_hor) -2], pathways_hor[len(pathways_hor) -1])]
        if len(corridor) > 1:
            corridors += [corridor]

        if debug:
            self.print_debug_block('horizontal corridors', corridors)

        # vertical search
        (x,y) = pathways_ver[0]
        corridor = [(x,y)]
        i = 0
        for i in range(1,len(pathways_ver)):

            (a,b) = pathways_ver[i]

            # check for column change (coordinates are not adjacent)
            if a != x:
                if len(corridor) > 1:
                    corridors += [corridor] # length 1 is a section of a horizontal corridor
                corridor = [(a,b)]
                (x,y) = (a,b)
                continue

            # if vertically adjacent, add to adjacencies, add to current
            # vertical corridor
            if b == y+1:
                adjacencies += [((x,y),(a,b))]
                corridor += [(a,b)]
                if (a,b) in crossroads:
                    corridors += [corridor]
                    corridor = [(a,b)]
            else:
                if len(corridor) > 1: # length 1 is a section of a vertical corridor
                    corridors += [corridor]
                corridor = [(a,b)]

            # check for spherical map adjacencies
            if b == self.map_.ver_tiles-1:
                (i,j) = [ (i,j) for (i,j) in pathways_ver if j == 0 and i == a ][0]
                adjacencies += [((i,j),(a,b))]
                tunnel_points += [(i,j)]
                tunnel_points += [(a,b)]

            (x,y) = (a,b)

        if debug:
            self.print_debug_block('horizontal + vertical corridors', corridors)

        # add last vertical adjacency and last vertical corridor
        if i == len(pathways_ver) -1:
            adjacencies += [(pathways_ver[len(pathways_ver) -2], pathways_ver[len(pathways_ver) -1])]
        if len(corridor) > 1:
            corridors += [corridor]        

        # connect corridors
        corridors = self.connect_corridors(corridors, tunnel_points, crossroads)

        if debug:
            self.print_debug_block('adjacencies', adjacencies)
            self.print_debug_block('corridors', corridors)

        return adjacencies, corridors

#------------------------------------------------------------------------------#

    def connect_corridors(self, corridors, tunnel_points, crossroads):
        """connects horizontal and vertical subcorridors that make up the
        same corridor

        Args:
        corridors: a list of horizontal and vertical subcorridors

        Returns:
        a list of complete corridors
        """

        # TODO turn this into a function to be utilized to sort corridors and to sort tunnels
        # connect vertical and horizontal adjacent corridors
        connected = []
        while corridors != []:
            self.print_debug_block('corridors', corridors)
            corr = corridors.pop()
            
            found = True
            while found:
                found = False
                self.print_debug_block('corr', corr)
                end0 = corr[0]
                end1 = corr[len(corr)-1]
                for c in corridors[:]: # copy of list to allow removals while iterating

                    #if end0 == (0,_)

                    if end0 == c[0] and end0 not in crossroads:
                        corr = corr[::-1] + c[1:]
                        self.print_debug_block('removed c', c)
                        corridors.remove(c)
                        found = True
                        break
                    elif end0 == c[len(c)-1] and end0 not in crossroads:
                        corr = c + corr[1:]
                        self.print_debug_block('removed c', c)
                        corridors.remove(c)
                        found = True
                        break
                    elif end1 == c[0] and end1 not in crossroads:
                        corr = corr + c[1:]
                        self.print_debug_block('removed c', c)
                        corridors.remove(c)
                        found = True
                        break
                    elif end1 == c[len(c)-1] and end1 not in crossroads:
                        corr = c[0:len(c)-1] + corr[::-1]
                        self.print_debug_block('removed c', c)
                        corridors.remove(c)
                        found = True
                        break

            connected += [corr]

        # TODO complete this part
        # connect corridors that form a tunnel (spherical map)
        tunnels = self.find_tunnels(corridors, tunnel_points)
        corridors = [ c for c in corridors if c not in tunnels]
        tunnels = self.connect_tunnels(tunnels, crossroads)
        corridors += tunnels

        return [ Corridor(corr) for corr in connected ]

#------------------------------------------------------------------------------#

    def find_tunnels(self, corridors, tunnel_points):
        return [ corr for corr in corridors \
                            if corr[0] in tunnel_points \
                            or corr[1] in tunnel_points ]

#------------------------------------------------------------------------------#

    def connect_tunnels(self, tunnels, crossroads):

        connected = []
        while tunnels != []:

            tun = tunnels.pop()

            found = True
            while found:
                found = False
                #self.print_debug_block('tun', tun)
                end0 = tun[0]
                end1 = tun[len(tun)-1]
                for t in tunnels[:]: # copy of list to allow removals while iterating

                    #if end0 == (0,_)

                    if end0 == t[len(t)-1] and end0 not in crossroads:
                        tun = t + tun[1:]
                        self.print_debug_block('removed t', t)
                        tunnels.remove(t)
                        found = True
                        break
                    elif end1 == t[0] and end1 not in crossroads:
                        tun = tun + t[1:]
                        self.print_debug_block('removed t', t)
                        tunnels.remove(t)
                        found = True
                        break

            connected += [tun]
        
        return connected

#------------------------------------------------------------------------------#

    def create_corridor_adjacencies(self, corridors, crossroads):
        """Creates pairs of adjacent corridors

        Args:
        corridors: a list of corridors

        Returns:
        a list of sorted tuples of adjacent corridors (with adjacency in the middle)
        """

        # connect vertical and horizontal adjacent corridors
        buffer = corridors
        corridors = []
        while buffer != []:

            corr = buffer.pop()
            found = True
            while found:
                found = False
                end0 = corr[0]
                end1 = corr[len(corr)-1]
                for c in buffer[:]: # copy of list to allow removals while iterating
                    if end0 == c[0] and end0 not in crossroads:
                        corr = corr[::-1] + c[1:]
                        buffer.remove(c)
                        found = True
                        break
                    elif end0 == c[len(c)-1] and end0 not in crossroads:
                        corr = c[1:] + corr
                        buffer.remove(c)
                        found = True
                        break
                    elif end1 == c[0] and end1 not in crossroads:
                        corr = corr + c[1:]
                        buffer.remove(c)
                        found = True
                        break
                    elif end1 == c[len(c)-1] and end1 not in crossroads:
                        corr = c[1:len(c)-1] + corr[::-1]
                        buffer.remove(c)
                        found = True
                        break

            corridors += [corr]

        corridors = [ Corridor(corr) for corr in corridors ]

        if debug:
            self.print_debug_block('corridors', corridors)

        return corridors


################################################################################
#############################   AUXILIAR CLASSES   #############################
################################################################################

class Corridor():
    """Represents an uninterrupted path of adjacente coordinates with a
    crossroad at each end

    Args:
        coordinates: list of coordinates of the Corridor

    Attr:
        coordinates: list of coordinates of the Corridor
        length: length of coordinates without crossroad ends

    """
    def __init__(self, coordinates):
        self.coordinates = coordinates
        self.length = len(coordinates) -2
        self.ends = (coordinates[0], coordinates[len(coordinates)-1])
        
    def dist_end0(self, coord):
        return len(self.coordinates[0:coord])

    def dist_end1(self, coord):
        return len(self.coordinates[coord:self.length])

    def dist_end(self, coord, end):
        if end == self.ends[0]:
            return self.dist_end0(coord)
        return self.dist_end1(coord)

    def closest_end(self, coord):
        return self.dist_end0(coord) \
            if self.dist_end0(coord) <= self.dist_end1(coord) \
            else self.dist_end1(coord)

    def sub_corridors(self, coord):
        index = self.coordinates.index(coord)
        return Corridor(self.coordinates[:index+1]), Corridor(self.coordinates[index:])

    def __str__(self):
        return str(self.coordinates)

    def __repr__(self):
        return self.__str__()
        