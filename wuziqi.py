import numpy as np
import random
import math
import copy

# 默认的棋盘大小
BOARD_SIZE  = 15

# 棋子类，记录搜索过程中棋子的位置，访问次数，胜利次数，父节点，孩子节点和当前的ucb值
class Node:
    def __init__(self, value):
        self.chess = value
        self.experience = 0
        self.win = 0
        self.parent = None
        self.children = []
        self.ucb = 0

    def __repr__(self):
        return f"{self.chess}=>{self.win}/{self.experience} {self.ucb}"

# 棋盘类
class Board:
    def __init__(self, size=BOARD_SIZE):
        self.size = size
        self.board = np.zeros((size, size), int)
        

        self.latest = [None, None, 0]
        self.rule = 5

    # 获取某一位置的棋子
    def get_chess(self, value):
        return self.board[value[0], value[1]]

    # 针对某一个棋子获取棋子所在位置四个方向的棋子
    def check_all_direction(self, node, player):
        cur_board = copy.deepcopy(self.board)
        cur_board[node.chess[0]][node.chess[1]] = player
        chess_x = node.chess[0]
        chess_y = node.chess[1]
        direction_dict = {key: [] for key in [0, 1, 2, 3]}
        direction_dict[0] = cur_board[chess_x, :]
        direction_dict[1] = cur_board[:, chess_y]
        direction_dict[2] = cur_board.diagonal(chess_y-chess_x)
        board_reverse = np.fliplr(cur_board)
        reverse_chess_x = chess_x
        reverse_chess_y = self.size-1-chess_y
        direction_dict[3] = board_reverse.diagonal(
            reverse_chess_y-reverse_chess_x)
        return direction_dict

    # 判断是否胜负已定
    def is_win(self):
        x, y, player = self.latest
        cur_x, cur_y, cur_player = x, y, player
        count = 1
        # EW
        while count < self.rule and cur_x > 0 and self.board[cur_x-1][cur_y] == cur_player:
            cur_x -= 1
            count += 1
        cur_x, cur_y, cur_player = x, y, player
        while count < self.rule and cur_x < self.size - 1 and self.board[cur_x+1][cur_y] == cur_player:
            cur_x += 1
            count += 1
        if count == self.rule:
            return True

        cur_x, cur_y, cur_player = x, y, player
        count = 1
        while count < self.rule and cur_y > 0 and self.board[cur_x][cur_y-1] == cur_player:
            cur_y -= 1
            count += 1
        cur_x, cur_y, cur_player = x, y, player
        while count < self.rule and cur_y < self.size - 1 and self.board[cur_x][cur_y+1] == cur_player:
            cur_y += 1
            count += 1
        if count == self.rule:
            return True

        cur_x, cur_y, cur_player = x, y, player
        count = 1
        while count < self.rule and cur_x > 0 and cur_y > 0 and self.board[cur_x-1][cur_y-1] == cur_player:
            cur_x -= 1
            cur_y -= 1
            count += 1
        cur_x, cur_y, cur_player = x, y, player
        while count < self.rule and cur_x < self.size - 1 and cur_y < self.size - 1 and self.board[cur_x+1][cur_y+1] == cur_player:
            cur_x += 1
            cur_y += 1
            count += 1
        if count == self.rule:
            return True

        cur_x, cur_y, cur_player = x, y, player
        count = 1
        while count < self.rule and cur_x > 0 and cur_y < self.size - 1 and self.board[cur_x-1][cur_y+1] == cur_player:
            cur_x -= 1
            cur_y += 1
            count += 1
        cur_x, cur_y, cur_player = x, y, player
        while count < self.rule and cur_x < self.size - 1 and cur_y > 0 and self.board[cur_x+1][cur_y-1] == cur_player:
            cur_x += 1
            cur_y -= 1
            count += 1
        if count == self.rule:
            return True

        else:
            return False
    
    # 遍历棋盘上的所有可以下棋位置，获取危险情况的棋子位置
    def get_information(self, player, pattern_list):
        pattern_list = [2 if item == -1 else item for item in pattern_list]
        delta_len = len(pattern_list) - 1
        str_pattern = "".join([str(_) for _ in pattern_list])
        for _ in self.get_available():
            direction_dict = self.check_all_direction(Node(_), player)
            for direction, str_array in direction_dict.items():
                len_end = len(list(str_array)) - 1
                list_array = [2 if item == -1 else item for item in list(str_array)]
                str_total = "".join([str(int(_)) for _ in list_array])
                find_index = str_total.find(str_pattern)
                if find_index != -1:
                    result_dict = dict()
                    print(f"set {_}, str_total:{str_total}, str_pattern:{str_pattern}, direction: {direction}")
                    if direction == 0:
                        start_x = _[0]
                        start_y = find_index
                        end_x = start_x
                        end_y = start_y+delta_len
                        if is_in(_, (start_x, start_y), (end_x, end_y), direction):
                            ends = dict()
                            if find_index == 0:
                                ends['start'] = None
                            else:
                                ends['start'] = ((start_x, start_y-1), self.get_chess((start_x, start_y-1)))
                            if find_index+delta_len == len_end:
                                ends['end'] = None
                            else:
                                ends['end'] = ((end_x, end_y+1), self.get_chess((end_x, end_y+1)))
                            result_dict =  {"direction": direction, "zuobiao": [start_x, start_y, end_x, end_y], "ends": ends, "latest": _}
                    elif direction == 1:
                        start_x = find_index
                        start_y = _[1]
                        end_x = start_x+delta_len
                        end_y = start_y
                        if is_in(_, (start_x, start_y), (end_x, end_y), direction):
                            ends = dict()
                            if find_index == 0:
                                ends['start'] = None
                            else:
                                ends['start'] = ((start_x, start_y-1), self.get_chess((start_x-1, start_y)))
                            if find_index+delta_len == len_end:
                                ends['end'] = None
                            else:
                                ends['end'] = ((end_x+1, end_y), self.get_chess((end_x+1, end_y)))
                            result_dict =  {"direction": direction, "zuobiao": [start_x, start_y, end_x, end_y], "ends": ends, "latest": _}
                    elif direction == 2:
                        if _[1] - _[0] > 0:
                            start_x = find_index
                            start_y = _[1] + find_index - _[0]
                        elif _[1] - _[0] < 0:
                            start_x = _[0] + find_index - _[1]
                            start_y = find_index
                        else:
                            start_x = find_index
                            start_y = find_index
                        end_x = start_x+delta_len
                        end_y = start_y+delta_len
                        if is_in(_, (start_x, start_y), (end_x, end_y), direction):
                            ends = dict()
                            if find_index == 0:
                                ends['start'] = None
                            else:
                                ends['start'] = ((start_x-1, start_y-1), self.get_chess((start_x-1, start_y-1)))
                            if find_index+delta_len == len_end:
                                ends['end'] = None
                            else:
                                ends['end'] = ((end_x+1, end_y+1), self.get_chess((end_x+1, end_y+1)))
                            result_dict =  {"direction": direction, "zuobiao": [start_x, start_y, end_x, end_y], "ends": ends, "latest": _}
                    elif direction == 3:
                        if self.size - 1 - _[1] - _[0] > 0:
                            start_x = find_index
                            start_y = _[1] - find_index + _[0]
                        elif self.size - 1 - _[1] - _[0] < 0:
                            start_x = _[0] + find_index - (self.size - 1 - _[1])
                            start_y = self.size - 1 - find_index
                        else:
                            start_x = find_index
                            start_y = self.size - 1 - find_index
                        end_x = start_x+delta_len
                        end_y = start_y-delta_len
                        if is_in(_, (start_x, start_y), (end_x, end_y), direction):
                            ends = dict()
                            if find_index == 0:
                                ends['start'] = None
                            else:
                                ends['start'] = ((start_x-1, start_y+1), self.get_chess((start_x-1, start_y+1)))
                            if find_index+delta_len == len_end:
                                ends['end'] = None
                            else:
                                ends['end'] = ((end_x+1, end_y-1), self.get_chess((end_x+1, end_y-1)))
                            print(f"direction: {direction}, zuobiao: {[start_x, start_y, end_x, end_y]}, ends: {ends}, latest: {_}")
                            result_dict =  {"direction": direction, "zuobiao": [start_x, start_y, end_x, end_y], "ends": ends, "latest": _}
                    if result_dict != dict():
                        print(result_dict)
                        print(pattern_list)
                        if pattern_list == [1,1,1,1,1]:
                            return result_dict['latest']
                        if pattern_list == [2,2,2,2,2]:
                            return result_dict['latest']
                        if pattern_list == [2,2,2,2]:
                            if result_dict['ends']['start'] != None and result_dict['ends']['end'] != None and result_dict['ends']['start'][1] == 0 and result_dict['ends']['end'][1] == 0:
                                    return result_dict['latest']
                            if result_dict['ends']['start'] == None and result_dict['ends']['end'] != None and result_dict['ends']['end'][1] == 0:
                                return result_dict["ends"]['end'][0]
                            if result_dict['ends']['end'] == None and result_dict['ends']['start'] != None and result_dict['ends']['start'][1] == 0:
                                return result_dict["ends"]["start"][0]
                        if pattern_list == [1,1,1,1]:
                            if result_dict['ends']['start'] != None and result_dict['ends']['end'] != None and result_dict['ends']['start'][1] == 0 and result_dict['ends']['end'][1] == 0:
                                return result_dict["latest"]
                            if result_dict['ends']['end'] != None and result_dict['ends']['end'][1] == 0:
                                return result_dict['latest']
                            if result_dict['ends']['start']  != None and result_dict['ends']['start'][1] == 0:
                                return result_dict['latest']
                    
        return None

    # 获取当前棋盘所有下过棋的位置索引
    def get_settled(self):
        a = np.where(self.board != 0)[0]
        b = np.where(self.board != 0)[1]
        return list(zip(a, b))

    # 获取当前棋盘所有没有下棋的位置索引
    def get_available(self):
        a = np.where(self.board == 0)[0]
        b = np.where(self.board == 0)[1]
        return list(zip(a, b))

    # 在搜索之前，先根据策略对危险棋子位置作出响应
    def judge_before(self):
            # pass
        result_1 =self.get_information(1, [1,1,1,1,1])
        if result_1:
            return result_1
        result_2 =self.get_information(-1, [-1,-1,-1,-1,-1])
        if result_2:
            return result_2
        result_3 = self.get_information(-1, [-1,-1,-1,-1])
        if result_3:
            return result_3
        result_4 = self.get_information(1, [1,1,1,1])
        if result_4:
            return result_4
        return None

# 判断一个棋子是否在两个棋子的连线之间的棋盘交叉点上
def is_in(v1, v_s, v_e, direction):
    candidate_list = []
    if direction == 0:
        cur_v = v_s
        while cur_v != v_e:
            candidate_list.append(cur_v)
            cur_v = (cur_v[0], cur_v[1]+1)
        candidate_list.append(cur_v)
    elif direction == 1:
        cur_v = v_s
        while cur_v != v_e:
            candidate_list.append(cur_v)
            cur_v = (cur_v[0]+1, cur_v[1])
        candidate_list.append(cur_v)
    elif direction == 2:
        cur_v = v_s
        while cur_v != v_e:
            candidate_list.append(cur_v)
            cur_v = (cur_v[0]+1, cur_v[1]+1)
        candidate_list.append(cur_v)
    elif direction == 3:
        cur_v = v_s
        while cur_v != v_e:
            candidate_list.append(cur_v)
            cur_v = (cur_v[0]+1, cur_v[1]-1)
        candidate_list.append(cur_v)
    if v1 in candidate_list:
        print(f"{v1} is in {v_s} - {v_e}")
        return True
    print(f"{v1} is not {v_s} - {v_e}")
    return False

# 蒙特卡洛搜索树
class UTC_TREE:
    def __init__(self, size=BOARD_SIZE):
        self.root = Node((None, None))
        self.computational_budget = 3000 # 迭代次数
        self.board = Board(size)
        self.CP = 0.17
        self.first_player = 1
        self.player = self.first_player
        self.reward = 1
        self.punish = 0

    # 在棋盘上下棋，记录最近一次提交结果，并且交换玩家
    def set(self, v):
        self.board.board[v.chess[0]][v.chess[1]] = self.player
        self.board.latest = [v.chess[0], v.chess[1], self.player]
        self.player = -self.player

    # 撤回棋子
    def unset(self, v):
        if v.parent == None:
            self.latest = [None, None, 0]
            self.player = self.first_player
        else:
            self.player = self.board.board[v.chess[0], v.chess[1]]
            self.board.latest = [v.parent.chess[0],
                                 v.parent.chess[1], -self.player]
            self.board.board[v.chess[0], v.chess[1]] = 0

    # utc搜索：选择->扩展->仿真->回溯
    def utc_search(self):
        v0 = self.root
        i = 0
        while i < self.computational_budget:
            v1 = self.tree_policy(v0)
            if not self.board.is_win():
                delta = self.default_policy()
            else:
                delta = 1
            self.backup(v1, delta)
            i += 1
        best = self.best_child(self.root, self.CP)
        children = self.root.children
        # print(children)
        children.sort(key=lambda x: x.ucb, reverse=True)
        print(children[:5])
        print(len(children))
        # print([f"{_.chess}-{_.ucb}\n" for _ in children])
        print(best)
        return best.chess
        # print(len(set([_.chess for _ in self.root.children])))
        # print()


    def tree_policy(self, v):
        while len(v.children) == len(self.board.get_available()):
            if len(v.children) == 0:
                return v
            v = self.best_child(v, self.CP)
            self.set(v)
            if self.board.is_win():
                return v
        return self.expand(v)

    # 选择
    def best_child(self, v, c):
        max_ucb = float("-inf")
        max_index = -1
        for index in range(len(v.children)):
            cur_ucb = self.UCB(v, v.children[index], self.CP)
            v.children[index].ucb = cur_ucb
            if cur_ucb > max_ucb:
                max_ucb = cur_ucb
                max_index = index
        return v.children[max_index]

    # 扩展
    def expand(self, v):
        available = list(set(self.board.get_available()) -
                         set([_.chess for _ in v.children]))
        next_index = random.randint(0, len(available)-1)
        v_new = Node(available[next_index])
        self.set(v_new)
        v.children.append(v_new)
        v_new.parent = v
        return v_new
        
    # 仿真
    def default_policy(self):
        cur_board = copy.deepcopy(self.board)
        cur_player = self.player
        available = cur_board.get_available()
        while len(available) != 0:
            next_index = random.randint(0, len(available)-1)
            next_chess = Node(available[next_index])
            cur_board.board[next_chess.chess[0],
                            next_chess.chess[1]] = cur_player
            cur_board.latest = [next_chess.chess[0],
                                next_chess.chess[1], cur_player]
            cur_player = -cur_player
            if cur_board.latest[2] == 1:
                if cur_board.is_win():
                    return self.reward
            elif cur_board.latest[2] == -1:
                if cur_board.is_win():
                    return self.punish
            available.pop(next_index)
        return self.punish

    # 回溯
    def backup(self, v, delta):
        while v is not None:
            v.experience += 1
            v.win += delta
            self.unset(v)
            v = v.parent


    # UCB计算方法
    def UCB(self, v_parent, v_child, c):
        part_1 = v_child.win/v_child.experience
        if self.player == -1:
            part_1 = 1 - part_1
        return part_1 + c*math.sqrt((2*np.log(self.root.experience))/(v_child.experience))


if __name__ == "__main__":

    # obj = UTC_TREE()
    # print(obj.board.board)
    # obj.utc_search()

    # 测试board的judge_before()方法，提前判断危险棋子位置
    board = Board()
    # board.board[3][5] = -1
    # board.board[3][4] = 1
    # board.board[3][6] = -1
    # board.board[3][7] = -1
    # board.board[4][5] = -1
    # board.board[4][6] = -1
    # board.board[4][7] = -1
    # board.board[4][8] = -1
    # board.board[5][7] = -1
    # board.board[6][6] = -1

    # board.board[1][1] = -1
    # board.board[2][2] = -1
    # board.board[3][3] = -1
    # board.board[0][0] = 1
    # board.board[0][1] = -1
    # board.board[0][2] = -1
    # board.board[0][3] = -1
    # board.board[1][1] = -1
    # board.board[1][2] = -1
    # board.board[1][3] = -1

    board.board[1][0] = -1
    board.board[2][0] = -1
    board.board[3][0] = -1
    print(board.board)
    print(board.judge_before())
    
    # 无GUI前提下，下棋模拟
    # board = np.zeros((BOARD_SIZE, BOARD_SIZE))
    # while True:
    #     x_y = input()
    #     x = int(x_y.split()[0])
    #     y = int(x_y.split()[1])
    #     print(f"({x},{y})")
    #     board[x][y] = -1
    #     obj = UTC_TREE()
    #     obj.board.board = board
    #     print("human~~~~~~~~~~~~~~~~~~~~~~~`")
    #     print(obj.board.board)
    #     judge_befored = obj.board.judge_before()
    #     print(judge_befored)
    #     if judge_befored:
    #         board[judge_befored[0], judge_befored[1]] = 1
    #     else:
    #         check_x, check_y = obj.utc_search()
    #         board[check_x][check_y] = 1
    #     print("machine~~~~~~~~~~~~~~~~~~~~~")
    #     print(board)
