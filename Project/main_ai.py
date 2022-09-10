from graphics import *
from math import *
import time

GRID_WIDTH = 35     # 一格宽度
CHESS_WIDTH = 17    # 棋子半径
BOARD_HEIGHT = 50   # 公告板高度
SHRINK_RATE = 0.7   # 子界面缩小比例

COLUMN = 15 # 列数
ROW = 15    # 行数

list1 = []  # AI棋表
list2 = []  # 人棋表
list3 = []  # all棋表

list_all = []  # 整个棋盘的点
next_point = [0, 0]  # AI下一步最应该下的位置

ratio = 0.5     # 进攻的系数(>1进攻型，<1防守型)
play_ratio = 1  # 水平因子
DEPTH = 3       # 搜索深度

# 棋型的评估分数
shape_score = [(20, (0, 1, 1, 0, 0)),
               (20, (0, 0, 1, 1, 0)),
               (20, (1, 1, 0, 1, 0)),
               (20, (1, 1, 1, 1, 0)),
               (20, (0, 1, 1, 1, 1)),
               (50, (0, 0, 1, 1, 1)),
               (50, (1, 1, 1, 0, 0)),
               (200, (1, 1, 1, 0, 1)),
               (200, (1, 1, 0, 1, 1)),
               (200, (1, 0, 1, 1, 1)),
               (5000, (0, 1, 1, 1, 0)),
               (5000, (0, 1, 0, 1, 1, 0)),
               (5000, (0, 1, 1, 0, 1, 0)),
               (900000, (0, 1, 1, 1, 1, 0)),
               (9999999, (1, 1, 1, 1, 1))]

# 每个方向上的分值计算
def cal_score(m, n, x_decrict, y_derice, enemy_list, my_list, score_all_arr):
    add_score = 0  # 加分项
    # 在一个方向上， 只取最大的得分项
    max_score_shape = (0, None)

    # 如果此方向上，该点已经有得分形状，不重复计算
    for item in score_all_arr:
        for pt in item[1]:
            if m == pt[0] and n == pt[1] and x_decrict == item[2][0] and y_derice == item[2][1]:
                return 0

    # 在落子点 左右方向上循环查找得分形状
    for offset in range(-5, 1):
        # offset = -2
        pos = []
        for i in range(0, 6):
            if (m + (i + offset) * x_decrict, n + (i + offset) * y_derice) in enemy_list:
                pos.append(2)
            elif (m + (i + offset) * x_decrict, n + (i + offset) * y_derice) in my_list:
                pos.append(1)
            else:
                pos.append(0)
        tmp_shap5 = (pos[0], pos[1], pos[2], pos[3], pos[4])
        tmp_shap6 = (pos[0], pos[1], pos[2], pos[3], pos[4], pos[5])

        for (score, shape) in shape_score:
            if tmp_shap5 == shape or tmp_shap6 == shape:
                if score > max_score_shape[0]:
                    max_score_shape = (score, ((m + (0+offset) * x_decrict, n + (0+offset) * y_derice),
                                               (m + (1+offset) * x_decrict, n + (1+offset) * y_derice),
                                               (m + (2+offset) * x_decrict, n + (2+offset) * y_derice),
                                               (m + (3+offset) * x_decrict, n + (3+offset) * y_derice),
                                               (m + (4+offset) * x_decrict, n + (4+offset) * y_derice)), (x_decrict, y_derice))

    # 计算两个形状相交， 如两个3活 相交， 得分增加 一个子的除外
    if max_score_shape[1] is not None:
        for item in score_all_arr:
            for pt1 in item[1]:
                for pt2 in max_score_shape[1]:
                    if pt1 == pt2 and max_score_shape[0] > 10 and item[0] > 10:
                        add_score += item[0] + max_score_shape[0]

        score_all_arr.append(max_score_shape)

    return add_score + max_score_shape[0]

# 估值函数
def eval(ai_flag):
    total_score = 0

    if ai_flag:
        me = list1
        enemy = list2
    else:
        me = list2
        enemy = list1

    # 算自己的得分
    score_my_arr = []  # 得分形状的位置 用于计算如果有相交 得分翻倍
    my_score = 0
    for pt in me:
        m = pt[0]
        n = pt[1]
        my_score += cal_score(m, n, 0, 1, enemy, me, score_my_arr)
        my_score += cal_score(m, n, 1, 0, enemy, me, score_my_arr)
        my_score += cal_score(m, n, 1, 1, enemy, me, score_my_arr)
        my_score += cal_score(m, n, -1, 1, enemy, me, score_my_arr)

    #  算敌人的得分
    score_enemy_arr = []
    enemy_score = 0
    for pt in enemy:
        m = pt[0]
        n = pt[1]
        enemy_score += cal_score(m, n, 0, 1, me, enemy, score_enemy_arr)
        enemy_score += cal_score(m, n, 1, 0, me, enemy, score_enemy_arr)
        enemy_score += cal_score(m, n, 1, 1, me, enemy, score_enemy_arr)
        enemy_score += cal_score(m, n, -1, 1, me, enemy, score_enemy_arr)

    total_score = my_score - enemy_score*ratio*play_ratio

    return total_score

# 离最后落子的邻居位置最有可能是最优点
def order(blank_list):
    last_pt = list3[-1]
    for item in blank_list:
        for i in range(-1, 2):
            for j in range(-1, 2):
                if i == 0 and j == 0:
                    continue
                if (last_pt[0] + i, last_pt[1] + j) in blank_list:
                    blank_list.remove((last_pt[0] + i, last_pt[1] + j))
                    blank_list.insert(0, (last_pt[0] + i, last_pt[1] + j))

# 有临近棋子的位置更适合落子
def not_alone(pt):
    for i in range(-1, 2):
        for j in range(-1, 2):
            if i == 0 and j == 0:
                continue
            if (pt[0] + i, pt[1]+j) in list3:
                return True
    return False

# 判断游戏是否终止
def end_game(list):
    for i in range(COLUMN):
        for j in range(ROW):
            if j < ROW - 4 and (i, j) in list and (i, j + 1) in list and (i, j + 2) in list and (i, j + 3) in list and (i, j + 4) in list:
                return True     #一行
            elif i < ROW - 4 and (i, j) in list and (i + 1, j) in list and (i + 2, j) in list and (i + 3, j) in list and (i + 4, j) in list:
                return True     #一列
            elif i < ROW - 4 and j < ROW - 4 and (i, j) in list and (i + 1, j + 1) in list and (i + 2, j + 2) in list and (i + 3, j + 3) in list and (i + 4, j + 4) in list:
                return True     #主对角线
            elif i < ROW - 4 and j > 3 and (i, j) in list and (i + 1, j - 1) in list and (i + 2, j - 2) in list and (i + 3, j - 3) in list and (i + 4, j - 4) in list:
                return True     #副对角线
    return False

# AB剪枝算法
def alphabeta(ai_flag, depth, alpha, beta):
    global win_ab
    global v_msg
    global a_msg
    global b_msg

    # 游戏是否结束 | | 探索的递归深度是否到边界
    if end_game(list1) or end_game(list2) or depth == 0:
        return eval(ai_flag)

    blank_list = list(set(list_all).difference(set(list3)))
    order(blank_list)   # 搜索顺序排序，提高剪枝效率

    # 遍历每一个候选步
    for next_step in blank_list:
        global ab_search_count
        ab_search_count += 1

        # 如果要评估的位置没有相邻的子， 则不去评估，减少计算
        if not not_alone(next_step):
            continue

        piece = Circle(Point(GRID_WIDTH * next_step[0]*SHRINK_RATE, GRID_WIDTH * next_step[1]*SHRINK_RATE), CHESS_WIDTH*SHRINK_RATE)
        if ai_flag:
            list1.append(next_step)
            piece.setFill('white')
            piece.draw(win_ab)
        else:
            list2.append(next_step)
            piece.setFill('black')
            piece.draw(win_ab)
        list3.append(next_step)

        # 如果能一步制胜
        if depth == DEPTH and end_game(list1):
            next_point[0] = next_step[0]
            next_point[1] = next_step[1]
            list1.remove(next_step)
            list3.remove(next_step)
            return 99999999

        value = -alphabeta(not ai_flag, depth - 1, -beta, -alpha)
        piece.undraw()
        if ai_flag:
            list1.remove(next_step)
        else:
            list2.remove(next_step)
        list3.remove(next_step)

        if value > alpha:
            # 更新状态值
            a_txt = [[str(round(alpha)),"- INF"][alpha<=-999999],"INF"][alpha>=999999]
            b_txt = [[str(round(beta)),"- INF"][beta<=-999999],"INF"][beta>=999999]
            v_msg.setText("Value: " + str(round(value)))
            a_msg.setText("Alpha: " + a_txt)
            b_msg.setText("Beta: " + b_txt)
            if depth == DEPTH:
                next_point[0] = next_step[0]
                next_point[1] = next_step[1]
            # alpha + beta剪枝点
            if value >= beta:
                global cut_count
                cut_count += 1
                return beta
            alpha = value

    return alpha

# 极大极小值
def minmax(ai_flag, depth):
    global win_mm
    global vm_msg
    global s_msg

    bestvalue = 0
    value = 0

    # 判断游戏是否结束||判断是否已经搜完
    if end_game(list1) or end_game(list2) or depth == 0:
        return eval(ai_flag)

    if ai_flag:  # 极大值点
        bestvalue = -9999999
    else:   # 极小值点
        bestvalue = 9999999
    
    # 创建可行位置表
    blank_list = list(set(list_all).difference(set(list3)))
    order(blank_list)   # 搜索顺序排序，提高剪枝效率

    # 遍历每一个候选步
    for next_step in blank_list:
        global mm_search_count
        mm_search_count += 1

        # 如果要评估的位置没有相邻的子，则不去评估，减少计算
        if not not_alone(next_step):
            continue
        
        # 下棋
        piece = Circle(Point(GRID_WIDTH * next_step[0]*SHRINK_RATE, GRID_WIDTH * next_step[1]*SHRINK_RATE), CHESS_WIDTH*SHRINK_RATE)
        if ai_flag:
            list1.append(next_step)
            piece.setFill('white')
            piece.draw(win_mm)
        else:
            list2.append(next_step)
            piece.setFill('black')
            piece.draw(win_mm)
        list3.append(next_step)

        value = minmax(not ai_flag, depth - 1)
        piece.undraw()
        if ai_flag:
            list1.remove(next_step)
        else:
            list2.remove(next_step)
        list3.remove(next_step)

        if ai_flag:
            bestvalue = [bestvalue,value][value>bestvalue]
            vm_msg.setText("Value: " + str(round(value)))
            s_msg.setText("State: Max")
        else:
            bestvalue = [bestvalue,value][value<bestvalue]
            vm_msg.setText("Value: " + str(round(value)))
            s_msg.setText("State: Min")
        
    return bestvalue

# AI下棋程序
def ai():
    # 更新两种博弈算法状态字符
    global mm_msg
    mm_msg.setText("MinMax: Calculating")
    global ab_msg
    ab_msg.setText("AlphaBeta: Calculating")

    # 统计搜索数据
    global mm_search_count   # minmax搜索次数
    mm_search_count = 0
    global cut_count   # 剪枝次数
    cut_count = 0
    global ab_search_count   # AB搜索次数
    ab_search_count = 0

    # 两种算法分别计算
    time_0 = time.process_time()
    alphabeta(True, DEPTH, -99999999, 99999999)
    time_ab = time.process_time()
    minmax(True, DEPTH)
    time_mm = time.process_time()

    # 更新两种博弈算法状态字符
    ab_msg.setText("AlphaBeta: " + str(round(time_ab-time_0,2)) +"s\nCut=" + str(cut_count) + "      Search=" + str(ab_search_count))
    mm_msg.setText("MinMax: " + str(round(time_mm-time_ab,2)) +"s\nSearch=" + str(mm_search_count))
    
    return next_point[0], next_point[1]

# 五子棋实际落子界面
def gobangwin():
    win = GraphWin("Gobang game", GRID_WIDTH*COLUMN, GRID_WIDTH*ROW+BOARD_HEIGHT*1.5)
    win.setBackground("gray")

    # 绘制两种博弈算法状态框
    h1 = GRID_WIDTH*ROW+BOARD_HEIGHT*0.5
    h2 = GRID_WIDTH*ROW+BOARD_HEIGHT*1.5
    w = GRID_WIDTH*COLUMN/2
    minmax_box = Rectangle(Point(0, h1),Point(w, h2))
    minmax_box.setFill('white')
    minmax_box.draw(win)
    ab_box = Rectangle(Point(w, h1),Point(w*2, h2))
    ab_box.setFill('white')
    ab_box.draw(win)

    # 添加两种博弈算法状态字符
    global mm_msg
    mm_msg = Text(Point(w/2, (h1+h2)/2), "MinMax: Waiting")
    mm_msg.draw(win)
    global ab_msg
    ab_msg = Text(Point(w*3/2, (h1+h2)/2), "AlphaBeta: Waiting")
    ab_msg.draw(win)

    # 绘制棋盘线条
    i1 = 0
    while i1 <= GRID_WIDTH * COLUMN:
        l = Line(Point(i1, 0), Point(i1, GRID_WIDTH * COLUMN))
        l.draw(win)
        i1 = i1 + GRID_WIDTH
    i2 = 0
    while i2 <= GRID_WIDTH * ROW:
        l = Line(Point(0, i2), Point(GRID_WIDTH * ROW, i2))
        l.draw(win)
        i2 = i2 + GRID_WIDTH
    return win

# AB剪枝算法演示界面
def alphabetawin():
    win = GraphWin("Alphabeta", GRID_WIDTH*COLUMN*SHRINK_RATE, (GRID_WIDTH*ROW+BOARD_HEIGHT*1.5)*SHRINK_RATE)
    win.setBackground("green")

    # 三个状态框
    h1 = (GRID_WIDTH*ROW+BOARD_HEIGHT*0.5)*SHRINK_RATE
    h2 = (GRID_WIDTH*ROW+BOARD_HEIGHT*1.5)*SHRINK_RATE
    w = SHRINK_RATE*GRID_WIDTH*COLUMN/3
    value_box = Rectangle(Point(0, h1),Point(w, h2))
    value_box.setFill('white')
    value_box.draw(win)
    alpha_box = Rectangle(Point(w, h1),Point(w*2, h2))
    alpha_box.setFill('white')
    alpha_box.draw(win)
    beta_box = Rectangle(Point(w*2, h1),Point(w*3, h2))
    beta_box.setFill('white')
    beta_box.draw(win)

    # 添加三种状态字符
    global v_msg
    v_msg = Text(Point(w/2, (h1+h2)/2), "Value: 0")
    v_msg.draw(win)
    global a_msg
    a_msg = Text(Point(w*3/2, (h1+h2)/2), "Alpha: - INF")
    a_msg.draw(win)
    global b_msg
    b_msg = Text(Point(w*5/2, (h1+h2)/2), "Beta: INF")
    b_msg.draw(win)

    # 绘制棋盘线条
    i1 = 0
    while i1 <= (GRID_WIDTH * COLUMN)*SHRINK_RATE:
        l = Line(Point(i1, 0), Point(i1, (GRID_WIDTH * COLUMN)*SHRINK_RATE))
        l.draw(win)
        i1 = i1 + GRID_WIDTH*SHRINK_RATE
    i2 = 0
    while i2 <= (GRID_WIDTH * ROW)*SHRINK_RATE:
        l = Line(Point(0, i2), Point((GRID_WIDTH * ROW)*SHRINK_RATE, i2))
        l.draw(win)
        i2 = i2 + GRID_WIDTH*SHRINK_RATE
    return win

# minmax算法演示界面
def minmaxwin():
    win = GraphWin("MinMax", GRID_WIDTH*COLUMN*SHRINK_RATE, (GRID_WIDTH*ROW+BOARD_HEIGHT*1.5)*SHRINK_RATE)
    win.setBackground("green")

    # 2个状态框
    h1 = (GRID_WIDTH*ROW+BOARD_HEIGHT*0.5)*SHRINK_RATE
    h2 = (GRID_WIDTH*ROW+BOARD_HEIGHT*1.5)*SHRINK_RATE
    w = SHRINK_RATE*GRID_WIDTH*COLUMN/2
    value_box = Rectangle(Point(0, h1),Point(w, h2))
    value_box.setFill('white')
    value_box.draw(win)
    state_box = Rectangle(Point(w, h1),Point(w*2, h2))
    state_box.setFill('white')
    state_box.draw(win)

    # 添加三种状态字符
    global vm_msg
    vm_msg = Text(Point(w/2, (h1+h2)/2), "Value: 0")
    vm_msg.draw(win)
    global s_msg
    s_msg = Text(Point(w*3/2, (h1+h2)/2), "State: Begin")
    s_msg.draw(win)

    # 绘制棋盘线条
    i1 = 0
    while i1 <= (GRID_WIDTH * COLUMN)*SHRINK_RATE:
        l = Line(Point(i1, 0), Point(i1, (GRID_WIDTH * COLUMN)*SHRINK_RATE))
        l.draw(win)
        i1 = i1 + GRID_WIDTH*SHRINK_RATE
    i2 = 0
    while i2 <= (GRID_WIDTH * ROW)*SHRINK_RATE:
        l = Line(Point(0, i2), Point((GRID_WIDTH * ROW)*SHRINK_RATE, i2))
        l.draw(win)
        i2 = i2 + GRID_WIDTH*SHRINK_RATE
    return win

# 主函数
def main():
    global win_ab
    global win_mm
    win_final = gobangwin()
    win_ab = alphabetawin()
    win_mm = minmaxwin()

    for i in range(COLUMN+1):
        for j in range(ROW+1):
            list_all.append((i, j))

    change = 0
    is_end = 0

    while is_end == 0:
        # AI落子
        if change % 2 == 1:
            pos = ai()

            if pos in list3:
                message = Text(Point(GRID_WIDTH*COLUMN*0.5, GRID_WIDTH*ROW+BOARD_HEIGHT*0.25), "WRONG POSITION" + str(pos[0]) + "," + str(pos[1]))
                message.draw(win_final)
                is_end = 1

            list1.append(pos)
            list3.append(pos)

            piece = Circle(Point(GRID_WIDTH * pos[0], GRID_WIDTH * pos[1]), CHESS_WIDTH)
            piece.setFill('white')
            piece.draw(win_final)
            piece_ab = Circle(Point(GRID_WIDTH * pos[0]*SHRINK_RATE, GRID_WIDTH * pos[1]*SHRINK_RATE), CHESS_WIDTH*SHRINK_RATE)
            piece_ab.setFill('white')
            piece_ab.draw(win_ab)
            piece_mm = Circle(Point(GRID_WIDTH * pos[0]*SHRINK_RATE, GRID_WIDTH * pos[1]*SHRINK_RATE), CHESS_WIDTH*SHRINK_RATE)
            piece_mm.setFill('white')
            piece_mm.draw(win_mm)

            if end_game(list1):
                message = Text(Point(GRID_WIDTH*COLUMN*0.5, GRID_WIDTH*ROW+BOARD_HEIGHT*0.25), "White win! Click anywhere to quit.")
                message.draw(win_final)
                is_end = 1
            change = change + 1
        
        # 人类落子
        else:
            p2 = win_final.getMouse()
            if p2.getY() <= GRID_WIDTH*COLUMN and not ((round((p2.getX()) / GRID_WIDTH), round((p2.getY()) / GRID_WIDTH)) in list3):

                a2 = round((p2.getX()) / GRID_WIDTH)
                b2 = round((p2.getY()) / GRID_WIDTH)
                list2.append((a2, b2))
                list3.append((a2, b2))

                piece = Circle(Point(GRID_WIDTH * a2, GRID_WIDTH * b2), CHESS_WIDTH)
                piece.setFill('black')
                piece.draw(win_final)
                piece_ab = Circle(Point(GRID_WIDTH * a2*SHRINK_RATE, GRID_WIDTH * b2*SHRINK_RATE), CHESS_WIDTH*SHRINK_RATE)
                piece_ab.setFill('black')
                piece_ab.draw(win_ab)
                piece_mm = Circle(Point(GRID_WIDTH * a2*SHRINK_RATE, GRID_WIDTH * b2*SHRINK_RATE), CHESS_WIDTH*SHRINK_RATE)
                piece_mm.setFill('black')
                piece_mm.draw(win_mm)
                
                if end_game(list2):
                    message = Text(Point(GRID_WIDTH*COLUMN*0.5, GRID_WIDTH*ROW+BOARD_HEIGHT*0.25), "Black win! Click anywhere to quit.")
                    message.draw(win_final)
                    is_end = 1

                change = change + 1

    win_final.getMouse()
    win_final.close()
    win_ab.close()
    win_mm.close()

# 程序入口
main()