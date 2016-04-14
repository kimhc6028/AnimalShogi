from __future__ import division
import numpy as np
import cv2
import time
#import NoMovePlayer

class Piece :

    def __init__(self, x, y):
        self.x, self.y = x, y
            

class Lion(Piece) :

    def __init__(self, x, y):
        Piece.__init__(self, x, y)
        self.actions_possible = [True, True, True, True, True, True, True, True]


class Chick(Piece) :

    def __init__(self, x, y):
        Piece.__init__(self, x, y)
        self.status = "chick"
        self.actions_possible = [True, False, False, False, False, False, False, False]

    def change_action(self):
        if self.status == "chick":
            self.actions_possible = [True, False, False, False, False, False, False, False]
        elif self.status == "chicken":
            self.actions_possible = [True, True, True, True, True, True, False, False]
        else :
            raise SyntaxtError


class Elephant(Piece) :

    def __init__(self, x, y):
        Piece.__init__(self, x, y)
        self.actions_possible = [False, False, False, False, True, True, True, True]


class Giraffe(Piece) :

    def __init__(self, x, y):
        Piece.__init__(self, x, y)
        self.actions_possible = [True, True, True, True, False, False, False, False]



        
class Player(object):

    def __init__(self,goal_location, player):
        self.reward = 0
        self.goal_location = goal_location
        self.player = player ## 1 or 2
        self.actions_list = ["F","B","L","R","FL","FR","BL","BR"]

    def inform_other(self, other):
        self.other = other

    def lion_in_goal(self):

        for piece in self.pieces_alive:
            if isinstance(piece, Lion):
                location = piece.x, piece.y

                if location in self.goal_location:
                    return True
        return False

    def chick_transform(self):

        for piece in self.pieces_alive:
            if isinstance(piece, Chick):
                location = piece.x, piece.y
                if location in self.goal_location:
                    piece.status = "chicken"
                    piece.change_action()

        for piece in self.pieces_capture:
            if isinstance(piece, Chick):
                piece.status = "chick"
                piece.change_action()

    
    def get_pieces(self, lion, chick, elephant, giraffe):
        self.pieces_alive = [lion, chick, elephant, giraffe]
        self.pieces_capture = []
        self.other_alive = []
        self.other_capture = []
        self.lion_flag = False

        
    def lion_alive(self):

        for piece in self.pieces_alive:
            if isinstance(piece, Lion):
                return True
        return False

    def inform(self):
        self.other.other_alive = self.pieces_alive
        self.other.other_capture = self.pieces_capture

    def move(self, piece, direction):
        x,y = piece.x,piece.y

        if self.player == 1:
            if direction == "F":##forward
                x += 1
            elif direction == "B":##backward
                x -= 1
            elif direction == "L":##left
                y += 1
            elif direction == "R":##right
                y -= 1
            elif direction == "FL":
                x += 1
                y += 1
            elif direction == "FR":
                x += 1
                y -=1
            elif direction == "BL":
                x -= 1
                y += 1
            elif direction == "BR":
                x -= 1
                y -= 1
            else :
                raise SyntaxError

        if self.player == 2:
            if direction == "F":##forward
                x -= 1
            elif direction == "B":##backward
                x += 1
            elif direction == "L":##left
                y -= 1
            elif direction == "R":##right
                y += 1
            elif direction == "FL":
                x -= 1
                y -= 1
            elif direction == "FR":
                x -= 1
                y +=1
            elif direction == "BL":
                x += 1
                y -= 1
            elif direction == "BR":
                x += 1
                y += 1
            else :
                raise SyntaxError

        location = x,y
        boundary = self.boundary_detection(location)
        if boundary == False:
            piece_detection, enemy_piece = self.piece_detection(location)

            if piece_detection == "empty":
                ##ok to move
                pass
            elif piece_detection == "my":
                return False
            elif piece_detection == "enemy":
                self.capture(enemy_piece)
            else :
                raise SyntaxError

            piece.x, piece.y = location
            return True

        elif boundary == True:
            return False
        else :
            raise SyntaxError

    def remove_alive(self, piece):
        self.pieces_alive.remove(piece)

    def capture(self, piece):
        self.other.remove_alive(piece)
        self.pieces_capture.append(piece)


    def deploy(self, piece, location):

        if (self.piece_detection(location)[0] == "empty") and (self.boundary_detection(location) == False) and (piece in self.pieces_capture):

            piece.x, piece.y = location
            self.pieces_alive.append(piece)
            self.pieces_capture.remove(piece)
            return True
        else:
            return False

    def piece_detection(self, location):

        for piece in self.pieces_alive:
            piece_location = piece.x,piece.y
            if location == piece_location:
                return "my", piece

        for piece in self.other_alive:
            piece_location = piece.x,piece.y
            if location == piece_location:
                return "enemy", piece

        return "empty", None
            

    def boundary_detection(self, location):
        x,y = location

        if (x >= 0) and (x <= 3) and (y >= 0) and (y <= 2) :
            return False
        else:
            return True

        
class RandomPlayer(Player):

    def __init__(self, goal_location, player):
        Player.__init__(self, goal_location, player)
        
    def register_pieces(self, lion1, chick1, elephant1, giraffe1, lion2, chick2, elephant2, giraffe2):
        pass

    def update_state(self):
        pass

    def update_action(self):
        pass
    
    def end_episode(self, reward):
        pass

    def action(self):
        actions = np.random.randint(2)

        if (actions == 0) and (len(self.pieces_capture) > 0):##deploy
            while True:
                choose_piece = np.random.randint(len(self.pieces_capture))
                location = np.random.randint(4), np.random.randint(3)
                if self.deploy(self.pieces_capture[choose_piece],location) == True:
                    break

        else:##move
            while True:
                choose_piece = np.random.randint(len(self.pieces_alive))

                while True:
                    direction_num = np.random.randint(8)
                    piece = self.pieces_alive[choose_piece]

                    if piece.actions_possible[direction_num] == True:
                        direction = self.actions_list[direction_num]
                        break
                if self.move(piece, direction) == True:
                    break
        

class Root:
    def __init__(self):
        self.children_state = []
        self.children = []

class Tree:

    def __init__(self, state, father):
        self.state = state
        self.register_father(father)
        self.children_state = []
        self.children = []
        #father.register_child(self.location, self)


    def register_father(self, father):
        if not(self.state in father.children_state):
            father.children_state.append(self.state)
            father.children.append(self)


class Leaf(Tree):

    def __init__(self, state, father):
        Tree.__init__(self, state, father)
        ##actions
        self.reward = np.zeros((8, 8 + 12))##F,B,L,R,FL,FR,BL,BR, 0,0~3,2
        self.counter = np.zeros((8, 8 + 12))
        self.ave = np.zeros((8, 8 + 12))

    def add_reward(self, action, reward):
        self.reward[action[0]][action[1]] += reward
        self.counter[action[0]][action[1]] += 1

    def average(self):
        self.ave = self.reward / self.counter


class MonteCarloPlayer(Player):

    def __init__(self, goal_location, player):
        Player.__init__(self, goal_location, player)

        self.epsilon = .1
        #self.action_ = 0
        self.Q = Root()

    def get_pieces(self, lion, chick, elephant, giraffe):
        #super(MonteCarloPlayer, self).get_pieces(lion, chick, elephant, giraffe)
        super(MonteCarloPlayer, self).get_pieces(lion, chick, elephant, giraffe)
        self.states = []
        self.actions = []
        #self.action_ = (np.random.randint(branch.ave.shape[0]), np.random.randint(branch.ave.shape[1]))##initial action
        #############self.action_ = (np.random.randint(8), np.random.randint(20))##initial action

    def register_pieces(self, lion1, chick1, elephant1, giraffe1, lion2, chick2, elephant2, giraffe2):
        self.pieces_list = [lion1, chick1, elephant1, giraffe1, lion2, chick2, elephant2, giraffe2]

    def state_encoder(self, piece):
        #print "state_encoder"
        if piece in self.pieces_alive:
            state = ((piece.x, piece.y), 0)
        elif piece in self.pieces_capture:
            state = (None, 0)
        elif piece in self.other_alive:
            state = ((piece.x, piece.y), 1)
        elif piece in self.other_capture:
            state = (None, 1)
        else :
            raise SyntaxError

        if isinstance(piece, Chick):
            if piece.status == "chick":
                state + (0,)
                #state.append(0)
            elif piece.status == "chicken":
                state + (1,)
                #state.append(1)
            else:
                raise SyntaxError

        return state

    def update_state(self):
        state = [self.state_encoder(piece) for piece in self.pieces_list]
        self.states.append(state)

    def update_action(self):
        self.actions.append(self.action_)
        

    def action(self):
        ##step == state
        #print "action"
        state = [self.state_encoder(piece) for piece in self.pieces_list]
        while True:
            self.action_ = self.search_policy(state)
            ###################
            piece = self.pieces_list[self.action_[0]]
            
            if self.action_[1] < 8:##move
                if piece in self.pieces_alive:
                    if piece.actions_possible[self.action_[1]] == True :
                        move = self.actions_list[self.action_[1]]
                        if self.move(piece, move) == True:
                            break
            else:##deploy
                if piece in self.pieces_capture:
                    deploy = np.unravel_index(self.action_[1] - 8, (4,3))
                    if self.deploy(piece, deploy) == True:
                        break
            #################

    def search_policy(self, step):
        #print "search_policy"
        branch = self.Q
        branch_searched = True
        for state in step:
            try:
                index = branch.children_state.index(state)
                branch = branch.children[index]
            except :
                branch_searched = False
                #print "branch search failed"
                break

        if branch_searched == True:
            #print "branch search success"
            if np.random.uniform(0,1) > self.epsilon:
                ##action = np.unravel_index(np.argmax(branch.ave), branch.ave.shape)
                action = np.unravel_index(np.nanargmax(branch.ave), branch.ave.shape)###########THIS!!!!
                #print action
            else :
                action = (np.random.randint(8), np.random.randint(20))
        else:
            action = (np.random.randint(8), np.random.randint(20))

        return action

    def make_branch(self, step, action, reward):
        #print "make_branch"
        branch = self.Q

        for i, state in enumerate(step):
            try :
                ##if it is successful to follow down tree, follow it until the end, and update its value 
                index = branch.children_state.index(state)
                branch = branch.children[index]
                ## update value required
            except :
                ##if not, make new state
                if i <= 6:
                    left_branches = step[i:-1]
                    leaf = step[-1]
                    
                    for branch_state in left_branches:
                        new_branch = Tree(branch_state, branch)
                        branch = new_branch
                    branch = Leaf(leaf, branch)
                    
                elif i == 7:
                    leaf = step[-1]
                    branch = Leaf(leaf, branch)
                else:
                    raise SyntaxError
                break
                
        branch.add_reward(action,reward)
        branch.average()
        
    def end_episode(self, reward):
        #print "end_episode"
        self.reward += reward
        #################################
        #print self.states
        #################################
        #last = self.states[-1]
        #last_action = self.actions[-1]
        #self.make_branch(last, last_action, reward)
        #############
        #for step, action in zip(self.states[:-1][::-1], self.actions[:-1][::-1]):
        #self.make_branch(step, action, reward)
        #print "end_episode"
        #self.reward += reward
        #################################
        #print self.states
        #################################
        '''
        print "end...episode!"
        print self.states[::-1]
        print self.actions[::-1]
        print "......................."
        '''
        #print "at the end of episode.............................."
        #print self.actions
        #print self.states

        for step, action in zip(self.states[::-1], self.actions[::-1]):
            self.make_branch(step, action, reward)


            

class DebugPlayer(MonteCarloPlayer):

    def __init__(self, goal_location, player):
        MonteCarloPlayer.__init__(self, goal_location, player)

    def action(self):

        self.action_ = input("action ==>")        
        state = [self.state_encoder(piece) for piece in self.pieces_list]
        action_ = self.search_policy(state)
        print "self.action_:{}".format(self.action_)
        print "self.actions:{}".format(self.actions)
        ####
        ###################
        piece = self.pieces_list[self.action_[0]]
        print "best action:"
        print piece
        print action_
        print "________________________________________"

        if self.action_[1] < 8:
            move = self.actions_list[self.action_[1]]
            self.move(piece, move)

        else:
            deploy = np.unravel_index(self.action_[1] - 8, (4,3))
            self.deploy(piece, deploy)
            #self.deploy(self.pieces_capture[piece], action_[1] - 8)





            
    def make_branch(self, step, action, reward):
        print "make_branch"
        branch = self.Q
        print " step :"
        print step
        print "action:"
        print action
        print "starting branch.."
        for i, state in enumerate(step):
            print "........................................................................."
            print i
            print state
            try :
                ##if it is successful to follow down tree, follow it until the end, and update its value 
                index = branch.children_state.index(state)
                branch = branch.children[index]

                print "trying...index:{}".format(index)
                ## update value required
            except :

                print "except"
                ##if not, make new state
                if i <= 6:
                    print "if"
                    left_branches = step[i:-1]
                    print "left_branches :{}".format(left_branches)
                    leaf = step[-1]
                    
                    for branch_state in left_branches:
                        new_branch = Tree(branch_state, branch)
                        branch = new_branch
                        print branch
                        print "......."
                        print branch_state
                    print "lolo"
                    print branch
                    old_branch = branch
                    branch = Leaf(leaf, branch)
                    print "lalala"
                    print branch
                    print old_branch.children_state

                elif i == 7:
                    print "elif"
                    print i
                    leaf = step[-1]
                    print leaf
                    print branch
                    branch = Leaf(leaf, branch)
                else:
                    raise SyntaxError
                break
                
        branch.add_reward(action,reward)
        branch.average()


    def update_state(self):
        #print "update_state"
        state = [self.state_encoder(piece) for piece in self.pieces_list]
        self.states.append(state)
        #self.actions.append(self.action_)        
        print "update_state<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
        print self.states

    def update_action(self):
        self.actions.append(self.action_)
        print self.actions

    def end_episode(self, reward):
        #print "end_episode"
        self.reward += reward
        #################################
        #print self.states
        #################################
        '''
        print "end...episode!"
        print self.states[::-1]
        print self.actions[::-1]
        print "......................."
        '''
        print "at the end of episode.............................."
        print self.actions
        print self.states

        for step, action in zip(self.states[::-1], self.actions[::-1]):
            self.make_branch(step, action, reward)
        
    def search_policy(self, step):
        #print "search_policy"
        branch = self.Q
        branch_searched = True
        print "len................"
        print len(step)
        print step
        for state in step:
            print "in branch"
            print branch.children_state

            try:
                print state
                print "yes branch!!!!!!!!!!!"
                print isinstance(branch, Tree)
                print isinstance(branch, Leaf)
                index = branch.children_state.index(state)
                print "ayasii"
                branch = branch.children[index]

            except :
                print state
                branch_searched = False
                print "no branch!!!!!!!"
                print isinstance(branch, Leaf)
                break

        if branch_searched == True:
            print "branch searched!!!!!!!!!!!!!!!!!!!"
            #if np.random.uniform(0,1) > self.epsilon:
            print "...................branch,reward.............................."
            print branch.ave
            ##action = np.unravel_index(np.nanmax(branch.ave), branch.ave.shape)###########
            action = np.unravel_index(np.nanargmax(branch.ave), branch.ave.shape)###########
            #else :
            #action = (np.random.randint(8), np.random.randint(20))
        else:
            action = (np.random.randint(8), np.random.randint(20))

        return action

            
class ManPlayer(Player):

    def __init__(self, goal_location, player):
        Player.__init__(self, goal_location, player)

    def action(self):
        action_ = input("action:D,M  ==>  ")
        
        if action_ == "D":##deploy
            print self.pieces_capture
            piece = input("piece:  ==>  ")
            location = input("location:  ==>  ")
            print self.deploy(self.pieces_capture[piece],location)
        elif action_ == "M":##move
            print self.pieces_alive
            piece = input("piece:  ==>  ")
            direction = input("direction:F,B,L,R,FL,FR,BL,BR  ==>  ")
            print self.move(self.pieces_alive[piece], direction)

    def register_pieces(self, lion1, chick1, elephant1, giraffe1, lion2, chick2, elephant2, giraffe2):
        pass

    def update_state(self):
        pass
    
    def update_action(self):
        pass

    def end_episode(self, reward):
        pass

            

class NoMovePlayer(Player):

    def __init__(self, goal_location, player):
        Player.__init__(self, goal_location, player)

    def action(self):
        pass

    def register_pieces(self, lion1, chick1, elephant1, giraffe1, lion2, chick2, elephant2, giraffe2):
        pass

    def update_state(self):
        pass
    
    def update_action(self):
        pass

    def end_episode(self, reward):
        pass

class Game:

    def __init__(self):
        
        self.player1 = MonteCarloPlayer([(3,0),(3,1),(3,2)], 1)
        #self.player2 = DebugPlayer([(0,0),(0,1),(0,2)], 2)
        #self.player1 = NoMovePlayer([(3,0),(3,1),(3,2)], 1)
        #self.player1 = RandomPlayer([(3,0),(3,1),(3,2)], 1)
        self.player2 = MonteCarloPlayer([(0,0),(0,1),(0,2)],2)
        self.test_player = RandomPlayer([(3,0),(3,1),(3,2)], 1)        
        self.man_player = ManPlayer([(3,0),(3,1),(3,2)], 1)
        self.player1.inform_other(self.player2)
        self.player2.inform_other(self.player1)
        
    def show(self,player1,player2):
        map = [["          ","          ","          "],
               ["          ","          ","          "],
               ["          ","          ","          "],
               ["          ","          ","          "]]

        for piece in player1.pieces_alive:
            x,y = piece.x, piece.y
            if isinstance(piece,Lion):
                map[x][y] = "   Lion1  "
            elif isinstance(piece,Elephant):
                map[x][y] = " Elephant1"
            elif isinstance(piece,Giraffe):
                map[x][y] = " Giraffe1 "
            elif isinstance(piece,Chick):
                if piece.status == "chick":
                    map[x][y] = "  Chick1  "
                elif piece.status == "chicken":
                    map[x][y] =" Chicken1 "

        for piece in player2.pieces_alive:
            x,y = piece.x, piece.y
            if isinstance(piece,Lion):
                map[x][y] = "   Lion2  "
            elif isinstance(piece,Elephant):
                map[x][y] = " Elephant2"
            elif isinstance(piece,Giraffe):
                map[x][y] = " Giraffe2 "
            elif isinstance(piece,Chick):
                if piece.status == "chick":
                    map[x][y] = "  Chick2  "
                elif piece.status == "chicken":
                    map[x][y] =" Chicken2 "
        print "-------------------Animal Shogi---------------------"
        print map[0]
        print map[1]
        print map[2]
        print map[3]
        print "----------------------------------------------------"


    def win_detection(self,player,other):

        if other.lion_alive() == False:
            #player.update_state()####last update
            player.end_episode(1)
            other.end_episode(-1)
            ##player.reward += 1
            ##other.reward -= 1
            return True

        if player.lion_flag == True:
            #player.update_state()
            player.end_episode(1)
            other.end_episode(-1)
            ##player.reward += 1
            ##other.reward -= 1
            return True

        if player.lion_in_goal() == True:
            player.lion_flag = True

        return False
    def test(self, test_episode):

        self.player2.inform_other(self.test_player)
        self.test_player.inform_other(self.player2)
        start_score = self.player2.reward
        for i in range(test_episode):
            self.game(self.test_player, self.player2)
        end_score = self.player2.reward
        print "MonteCarloPlayer's Score : {}".format((end_score - start_score) / test_episode)
        self.player2.inform_other(self.player1)

    def play(self):

        self.player2.inform_other(self.man_player)
        self.man_player.inform_other(self.player2)
        self.game(self.man_player, self.player2, show = True)



    def game(self, player1, player2, show = False):
        #print ".............game start!................."
        self.lion1 = Lion(0,1)
        self.lion2 = Lion(3,1)
        chick1 = Chick(1,1)
        chick2 = Chick(2,1)
        elephant1 = Elephant(0,0)
        elephant2 = Elephant(3,2)
        giraffe1 = Giraffe(0,2)
        giraffe2 = Giraffe(3,0)

        player1.get_pieces(self.lion1, chick1, elephant1, giraffe1)
        player2.get_pieces(self.lion2, chick2, elephant2, giraffe2)
            
        player1.inform()
        player2.inform()

        player1.register_pieces(self.lion1, chick1, elephant1, giraffe1, self.lion2, chick2, elephant2, giraffe2)
        player2.register_pieces(self.lion2, chick2, elephant2, giraffe2, self.lion1, chick1, elephant1, giraffe1)


        player1.update_state()
        player1.action()
        player1.update_action()
        player1.chick_transform()
        player1.inform()
        while True:
            #time.sleep(1)
            ##do game
            player2.update_state()
            player2.action()
            player2.update_action()
            player2.chick_transform()
            player2.inform()

            #player1.update_state()###
            if show == True:
                self.show(player1, player2)
            if self.win_detection(player2, player1)== True:
                #print "player2 win"
                break

            #time.sleep(1)
            player1.update_state()
            player1.action()
            player1.update_action()
            player1.chick_transform()
            player1.inform()
            #player2.update_state()###
            ##do game
            if show == True:
                self.show(player1, player2)
            if self.win_detection(player1, player2)== True:
                #print "player1 win"
                break




    def learn_episode(self, episode):
        
        for i in range(episode):
            #print "score:{}".format(self.player2.reward / (i + 1))
            #print "reward:{}".format(self.player2.reward)
            if i % 1000 == 0:
                print("episode {} passed".format(i))
                self.test(100)
                print "player2's reward:{}".format(self.player2.reward)
                #print "........start game........"
            self.game(self.player1, self.player2)        
            #self.search_tree()
        
        print "Learning Finished!!"
        print "Last test..."
        self.test(1000)
        self.play()

    def search_tree(self):
        branch = self.player2.Q
        for i in range(8):
            print i, branch.children_state[0]
            branch = branch.children[0]

        print "reward..................."
        print branch.reward
        print "action"
        action = np.unravel_index(np.argmax(branch.reward), branch.reward.shape)
        print action

def main():
    game = Game()
    game.learn_episode(1000000)

if __name__=="__main__":
    main()
