from tkinter import *
from tkinter.messagebox import *
from wuziqi import UTC_TREE, Board
import numpy as np

from multiprocessing import Queue
import multiprocessing


class Chess(object):
    def __init__(self):
        self.size = 15
        self.mesh = 45
        self.ratio = 0.9
        self.board_color = "#CDBA96"
        self.header_bg = "#CDC0B0"
        self.btn_font = ("黑体", 12, "bold")
        self.step = self.mesh / 2
        self.chess_r = self.step * self.ratio
        self.point_r = self.step * 0.2
        self.is_start = False
        self.player = -1
        self.board = Board(self.size)
        self.queue = Queue()

        self.root = Tk()
        self.root.title("wuziqi")
        self.root.resizable(width=True, height=True)

        self.f_header = Frame(self.root, highlightthickness=0, bg=self.header_bg)
        self.f_header.pack(fill=BOTH, ipadx=10)

        self.b_start = Button(self.f_header, text="开始", command=self.bf_start, font=self.btn_font)
        self.b_lose = Button(self.f_header, text="认输", command=self.bf_lose, state=DISABLED, font=self.btn_font)
        self.l_info = Label(self.f_header, text="未开始", bg=self.header_bg, font=("楷体", 18, "bold"), fg="white")

        self.b_start.pack(side=LEFT, padx=20)
        self.b_lose.pack(side=RIGHT, padx=20)
        self.l_info.pack(side=LEFT, expand=YES, fill=BOTH, pady=10)


        self.c_chess = Canvas(self.root,
                              bg=self.board_color,
                              width=(self.size + 1) * self.mesh,
                              height=(self.size + 1) * self.mesh,
                              highlightthickness=0)
        self.draw_board()
        self.c_chess.bind("<Button-1>", self.cf_board)
        self.c_chess.pack()
        self.root.mainloop()

    # 绘制网格
    def draw_mesh(self, x, y):
        ratio = (1 - self.ratio) * 0.99 + 1
        center_x, center_y = self.mesh * (x + 1), self.mesh * (y + 1)
        self.c_chess.create_rectangle(center_y - self.step,
                                      center_x - self.step,
                                      center_y + self.step,
                                      center_x + self.step,
                                      fill=self.board_color,
                                      outline=self.board_color)
        a, b = [0, ratio] if y == 0 else [-ratio, 0] if y == self.size - 1 else [-ratio, ratio]
        c, d = [0, ratio] if x == 0 else [-ratio, 0] if x == self.size - 1 else [-ratio, ratio]
        self.c_chess.create_line(center_y + a * self.step, center_x, center_y + b * self.step, center_x)
        self.c_chess.create_line(center_y, center_x + c * self.step, center_y, center_x + d * self.step)
        #  显示坐标
        # [self.c_chess.create_text(self.mesh * (i + 1), self.mesh * 0.8, text=f'{i}') for i in range(self.size)]
        # [self.c_chess.create_text(self.mesh * 0.8, self.mesh * (i + 1), text=f'{i}') for i in range(self.size)]

        if ((x == 3 or x == 11) and (y == 3 or y == 11)) or (x == 7 and y == 7):
            self.c_chess.create_oval(center_y - self.point_r, center_x - self.point_r, center_y + self.point_r, center_x + self.point_r, fill="black")

    # 绘制棋子
    def draw_chess(self, x, y, color):
        center_x, center_y = self.mesh * (x + 1), self.mesh * (y + 1)
        self.c_chess.create_oval(center_y - self.chess_r, center_x - self.chess_r, center_y + self.chess_r, center_x + self.chess_r, fill=color)

    # 绘制棋盘
    def draw_board(self):
        [self.draw_mesh(x, y) for y in range(self.size) for x in range(self.size)]

    # 棋盘中间显示文字
    def center_show(self, text):
        width, height = int(self.c_chess['width']), int(self.c_chess['height'])
        self.c_chess.create_text(int(width / 2), int(height / 2), text=text, font=("黑体", 30, "bold"), fill="red")

    # 初始化棋盘
    def bf_start(self):
        self.set_btn_state("start")
        self.is_start = True
        self.board = Board(self.size)
        self.draw_board()
        self.l_info.config(text="黑方下棋")
        self.player = -1

    # 认输显示
    def bf_lose(self):
        self.set_btn_state("init")
        self.is_start = False
        text = self.ternary_operator("黑方认输", "白方认输")
        self.l_info.config(text=text)
        self.center_show("黑方认输")


    def cf_board(self, e):
        if self.player != -1:
            return
        # 根据点击寻找索引
        x, y = int((e.y - self.step) / self.mesh), int((e.x - self.step) / self.mesh)
        center_x, center_y = self.mesh * (x + 1), self.mesh * (y + 1)
        distance = ((center_x - e.y)**2 + (center_y - e.x)**2)**0.5
        if distance > self.step * 0.95 or self.board.board[x][y] != 0 or not self.is_start:
            return
        print(f"self.player: {self.player}")
        tag = self.ternary_operator(1, -1)
        self.draw_chess(x, y, "black")
        self.board.board[x][y] = tag
        self.trans_identify()
        
        
        # 如果赢了，则游戏结束，修改状态，中心显示某方获胜
        if self.is_win(x, y, tag):
            self.is_start = False
            self.set_btn_state("init")
            text = self.ternary_operator("黑方获胜", "白方获胜")
            self.center_show(text)
            return

        # 如果下满了，则游戏结束，修改状态，中心显示平局
        if np.where(self.board.board==0)[0] == []:
            self.is_start = False
            self.set_btn_state("init")
            text = self.ternary_operator("平局")
            self.center_show(text)
            return


        multiprocessing.Process(target=self.play_chess).start()
        self.root.after(1000, self.calculate_next)
        
    
    def calculate_next(self):
        if self.queue.empty():
            self.root.after(1000, self.calculate_next)
        else:
            next_x, next_y = self.queue.get()
            print(f"self.player: {self.player}")
            tag = self.ternary_operator(1, -1)
            color = self.ternary_operator("white", "black")
            self.draw_chess(next_x, next_y, color)
            self.board.board[next_x][next_y] = tag
            self.trans_identify()
            

            # 如果赢了，则游戏结束，修改状态，中心显示某方获胜
            if self.is_win(next_x, next_y, tag):
                self.is_start = False
                self.set_btn_state("init")
                text = self.ternary_operator("黑方获胜", "白方获胜")
                self.center_show(text)
                return
            # 如果下满棋盘，则游戏结束，修改状态，中心显示平局
            if np.where(self.board.board==0)[0] == []:
                self.is_start = False
                self.set_btn_state("init")
                text = "平局"
                self.center_show(text)
                return
                

        
    def play_chess(self):
         # 如果游戏继续，则交换棋手
        utc_tree = UTC_TREE(self.size)
        utc_tree.board = self.board
        print(self.board.board)
        judged_before = self.board.judge_before()
        print(judged_before)
        if judged_before:
            next_x = judged_before[0]
            next_y = judged_before[1]
        else:
            next_x, next_y = utc_tree.utc_search()
        self.queue.put((next_x, next_y))
        
    

    def is_win(self, x, y, tag):
        # 获取斜方向的列表
        def direction(i, j, di, dj, row, column, matrix):
            temp = []
            while 0 <= i < row and 0 <= j < column:
                i, j = i + di, j + dj
            i, j = i - di, j - dj
            while 0 <= i < row and 0 <= j < column:
                temp.append(matrix[i][j])
                i, j = i - di, j - dj
            return temp

        four_direction = []
        # 获取水平和竖直方向的列表
        four_direction.append([self.board.board[i][y] for i in range(self.size)])
        four_direction.append([self.board.board[x][j] for j in range(self.size)])
        # 获取斜方向的列表
        four_direction.append(direction(x, y, 1, 1, self.size, self.size, self.board.board))
        four_direction.append(direction(x, y, 1, -1, self.size, self.size, self.board.board))

        for v_list in four_direction:
            count = 0
            for v in v_list:
                if v == tag:
                    count += 1
                    if count == 5:
                        return True
                else:
                    count = 0
        return False

    # 设置四个按钮是否可以点击
    def set_btn_state(self, state):
        state_list = [NORMAL, DISABLED, DISABLED, DISABLED] if state == "init" else [DISABLED, NORMAL, NORMAL, NORMAL]
        self.b_start.config(state=state_list[0])
        # self.b_restart.config(state=state_list[1])
        # self.b_regret.config(state=state_list[2])
        self.b_lose.config(state=state_list[3])

    # 因为有很多和self.black相关的三元操作，所以就提取出来
    def ternary_operator(self, true, false):
        return true if self.player==1 else false

    # 交换棋手
    def trans_identify(self):
        text = self.ternary_operator("黑方下棋", "白方下棋")
        self.l_info.config(text=text)
        self.player = - self.player



if __name__ == '__main__':
    Chess()