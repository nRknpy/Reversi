from pyexpat import model
import numpy as np
import pickle

white=1
black=-1
blank=0

class Board(object):
    def __init__(self):
        self.board_arr=np.zeros((8,8)).astype(int)
        self.board_arr[3][3]=self.board_arr[4][4]=white
        self.board_arr[3][4]=self.board_arr[4][3]=black
        self.turn=-1
        self.__directions=((1,0),(1,1),(0,1),(-1,1),(-1,0),(-1,-1),(0,-1),(1,-1))
        self.black_count=2
        self.white_count=2
        self.blank_count=60

    def show_board(self):
        print('==='*10)
        print('   ',end='')
        for i in ('a','b','c','d','e','f','g','h'): print(i,end='  ')
        print('\n',end='')
        for x in range(8):
            print(x+1,end='  ')
            for y in range(8):
                if self.board_arr[x][y] == white:
                    print('○', end = '  ')
                elif self.board_arr[x][y] == black:
                    print('●', end = '  ')
                else:
                    print('-', end = '  ')
            print('\n', end = '')

    def turn_change(self):
        self.turn*=-1

    def is_in_board(self,col,row):
        return 0<=col<8 and 0<=row<8

    def can_reverse_d(self,col,row,dir):
        if not self.is_in_board(col+dir[0],row+dir[1]):
            return False
        if self.board_arr[row+dir[1]][col+dir[0]]==self.turn:
            return False
        col+=dir[0]
        row+=dir[1]
        while self.is_in_board(col,row):
            if self.board_arr[row][col]==self.turn:
                return True
            if self.board_arr[row][col]==blank:
                return False
            if self.board_arr[row][col]==-self.turn:
                col+=dir[0]
                row+=dir[1]
                continue
            assert False, f"instance.board_arr[{row}][{col}] is invalid value"
        return False

    def can_reverse(self,col,row):
        return any([self.can_reverse_d(col,row,d) for d in self.__directions])

    def can_put(self,col,row):
        if not self.is_in_board(col,row):
            return False
        if self.board_arr[row][col]!=blank:
            return False
        if not self.can_reverse(col,row):
            return False
        return True

    def reverse_stones_d(self,col,row,dir):
        col+=dir[0]
        row+=dir[1]
        while self.board_arr[row][col]!=self.turn:
            assert self.board_arr[row][col]==-self.turn, f"instance.board_arr[{row}][{col}] is blank or not opponent stone"
            self.board_arr[row][col]*=-1
            if self.turn==-1:
                self.black_count+=1
                self.white_count-=1
            else:
                self.black_count-=1
                self.white_count+=1
            col+=dir[0]
            row+=dir[1]

    def reverse_stones(self,col,row):
        for d in self.__directions:
            if not self.can_reverse_d(col,row,d): continue
            self.reverse_stones_d(col,row,d)

    def put_stone(self,col,row):
        if self.can_put(col,row):
            self.board_arr[row,col]=self.turn
            if self.turn==-1: self.black_count+=1
            else: self.white_count+=1
            self.blank_count-=1
            self.reverse_stones(col,row)
            self.turn_change()
            return True
        else:
            #print("cannot put")
            return False

    def is_pass(self):
        for i in range(8):
            for j in range(8):
                assert any([self.board_arr[i][j]==k for k in (-1,0,1)]), f"instance.board_arr[{i}][{j}] is invalid value"
                if self.can_put(i,j):
                    return False
        return True

class Reversi(Board):
    def __init__(self, is_human_first=True, model=None):
        super().__init__()
        self.two_pass_count=0
        self.__player_list=['human','human']
        if model!=None:
            self.com_model=model
            if is_human_first:
                self.__player_list=['human','com']
                self.com_color=1
            else:
                self.__player_list=['com','human']
                self.com_color=-1

    def is_gameset(self):
        if self.blank_count<=0:
            return True
        if self.two_pass_count==2:
            return True
        if self.blank_count*self.white_count==0:
            return True
        return False

    def input_place(self):
        col=input("column(a-f) >> ")
        row=input("   row(1-8) >> ")
        if len(col)!=1 or not row.isdigit():
            print("invalid input")
            return self.input_place()
        return ord(col)-ord('a'),int(row)-1

    def one_turn(self,player='human'):
        assert player=='human' or player=='com', "the argument 'player' must be 'human' or 'com'"
        if super().is_pass():
            print("This turn is passed")
            self.two_pass_count+=1
            super().turn_change()
            return False
        self.two_pass_count=0
        if player=='human':
            col,row=self.input_place()
            if not super().put_stone(col,row):
                print(f"You cannot put at {chr(col+ord('a'))}{row+1}")
                return self.one_turn(player=player)
        else:
            x_com=(np.reshape(self.board_arr,[-1,64])==self.com_color).astype(np.int8)[0]
            x_hum=(np.reshape(self.board_arr,[-1,64])==-self.com_color).astype(np.int8)[0]
            x=np.array([x_com,x_hum])
            x=np.reshape(x,[-1,128])
            y=self.com_model.predict_proba(x)
            y=np.insert(y,27,[-1,-1])
            y=np.insert(y,35,[-1,-1])
            pos_arr=np.argsort(y)[::-1]
            for pos in pos_arr:
                col=pos//8
                row=pos%8
                if super().put_stone(col,row):
                    return True
            print("debug")
        return True

    def play(self):
        turn_num=0
        while not self.is_gameset():
            super().show_board()
            print(f"●: {self.black_count}, ○: {self.white_count}")
            print(f"turn: {'○' if self.turn==1 else '●'}")
            self.one_turn(player=self.__player_list[turn_num%2])
            turn_num+=1
        self.gameset()

    def gameset(self):
        print("game set")
        super().show_board()
        print(f"●: {self.black_count}, ○: {self.white_count}")
        if self.black_count>self.white_count:
            print("winner: black")
        elif self.black_count<self.white_count:
            print("winner: white")
        else:
            print("draw")
        exit()


if __name__=="__main__":
    with open("mlp_model_dep4",'rb') as f:
        model=pickle.load(f)
    reversi=Reversi(model=model)
    reversi.play()