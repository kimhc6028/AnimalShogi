
import numpy as np
import cv2
import time
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


class Player:

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

        if (self.piece_detection(location)[0] == "empty") and (self.boundary_detection(location) == False):
            
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
        

class MonteCarloPlayer(Player):

    def __init__(self, goal_location, player):
        Player.__init__(self, goal_location, player)

        self.epsilon = .1
        self.action_ = 0
        self.Q = Root()

    def get_pieces(self, lion, chick, elephant, giraffe):
        super(MonterCarloPlayer, self).get_pieces(lion, chick, elephant, giraffe)
        self.states = []
        self.actions = []
        self.action_ = (np.random.randint(branch.ave.shape[0]), np.random.randint(branch.ave.shape[1]))##initial action

    def register_pieces(self, lion1, chick1, elephant1, giraffe1, lion2, chick2, elephant2, giraffe2):
        self.pieces_list = [lion1, chick1, elephant1, giraffe1, lion2, chick2, elephant2, giraffe2]


    def state_encoder(self, piece):

        if piece in self.pieces_alive:
            state = ((piece.x, piece.y), 0)
        elif piece in self.pieces_capture:
            state = (None, 0)
        elif piece in self.others_alive:
            state = ((piece.x, piece.y), 1)
        elif piece in self.others_capture:
            state = (None, 1)
        else :
            raise SyntaxError

        if isinstance(piece, Chick):
            if piece.status == "chick":
                state.append(0)
            elif piece.status == "chicken":
                state.append(1)
            else:
                raise SyntaxError

        return status

    def update_state(self, action):
        state = [self.state_encoder(piece) for piece in self.pieces_list]
        self.states.append(state)
        self.actions.append(action)

    def action(self):
        ##step == state
        state = [self.state_encoder(piece) for piece in self.pieces_list]
        self.action_ = search_policy(state)


    def search_policy(self, step):
        branch = self.Q
        branch_searched = True
        for state in step:
            try:
                index = branch.children_state.index(state)
                branch = branch.children[index]
            except :
                branch_searched = False
                break

        if branch_searched == True:
            if np.random.uniform(0,1) > self.epsilon:
                action = np.unravel_index(branch.ave, branch.ave.shape)
            else :
                action = (np.random.randint(branch.ave.shape[0]), np.random.randint(branch.ave.shape[1]))
        else:
            action = (np.random.randint(branch.ave.shape[0]), np.random.randint(branch.ave.shape[1]))

        return action

    def make_branch(self, step, action, reward):
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
                    left_branches = states[i:-1]
                    leaf = states[-1]
                    
                    for branch_state in left_branches:
                        new_branch = Tree(branch_state, branch)
                        branch = new_branch
                    branch = Leaf(leaf, branch)
                    
                elif i == 7:
                    leaf = state[-1]
                    branch = Leaf(leaf, branch)
                else:
                    raise SyntaxError
                break
                
        branch.add_reward(action,reward)
        
    def end_episode(self, reward):
        self.reward += reward
        last = self.states[-1]
        last_action = self.actions[-1]
        self.make_branch(last, last_action, reward)
        #############
        for step, action in zip(self.states[:-1][::-1], self.actions[:-1][::-1]):
            self.make_branch(step, action, reward)
            

class Root:
    def __init__(self):
        self.children_state = []

class leaf(Tree):

    def __init__(self, state, father):
        Tree.__init__(state, father)
        ##actions
        self.reward = np.zeros((8, 8 + 12))##F,B,L,R,FL,FR,BL,BR, 0,0~3,2
        self.counter = np.zeros((8, 8 + 12))
        self.ave = np.zeros((8, 8 + 12))

    def add_reward(self, action, reward):
        self.reward[action[0]][action[1]] += reward
                
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

class Game:

    def __init__(self):

        self.player1 = RandomPlayer([(3,0),(3,1),(3,2)], 1)
        self.player2 = RandomPlayer([(0,0),(0,1),(0,2)], 2)
        
        self.player1.inform_other(self.player2)
        self.player2.inform_other(self.player1)
        

    def show(self):
        map = [["          ","          ","          "],
               ["          ","          ","          "],
               ["          ","          ","          "],
               ["          ","          ","          "]]

        for piece in self.player1.pieces_alive:
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

        for piece in self.player2.pieces_alive:
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
            player.end_episode(1)
            other.end_episode(-1)
            ##player.reward += 1
            ##other.reward -= 1
            return True

        if player.lion_flag == True:
            player.end_episode(1)
            other.end_episode(-1)
            ##player.reward += 1
            ##other.reward -= 1
            return True

        if player.lion_in_goal() == True:
            player.lion_flag = True

        return False

    def learn_episode(self, episode):

        for i in range(episode):
            if i % 1000 == 0:
                print("episode {} passed".format(i))
            #print "........start game........"
                
            self.lion1 = Lion(0,1)
            self.lion2 = Lion(3,1)
            chick1 = Chick(1,1)
            chick2 = Chick(2,1)
            elephant1 = Elephant(0,0)
            elephant2 = Elephant(3,2)
            giraffe1 = Giraffe(0,2)
            giraffe2 = Giraffe(3,0)

            self.player1.get_pieces(self.lion1, chick1, elephant1, giraffe1)
            self.player2.get_pieces(self.lion2, chick2, elephant2, giraffe2)
            
            self.player1.inform()
            self.player2.inform()

            self.player1.register_pieces(self.lion1, chick1, elephant1, giraffe1, self.lion2, chick2, elephant2, giraffe2)
            self.player2.register_pieces(self.lion2, chick2, elephant2, giraffe2, self.lion1, chick1, elephant1, giraffe1)

            while True:
                self.player1.action()
                self.player1.chick_transform()
                self.player1.inform()

                self.player2.update_state()###

                ##do game

                if self.win_detection(self.player1, self.player2)== True:
                    #print "player1 win"
                    break
                #self.show()
                #time.sleep(1)
                ##do game
                self.player2.action()
                self.player2.chick_transform()
                self.player2.inform()

                self.player1.update_state()###

                if self.win_detection(self.player2, self.player1)== True:
                    #print "player2 win"
                    break
                #self.show()
                #time.sleep(1)
def main():
    game = Game()
    game.learn_episode(100000)

    if __name__=="__main__":
    main()
