from random import randint

class Algos:
    def __init__(self):
        self.path = []
        self.cur_c, self.cur_r = None, None
        
    def mha_distance(self, point_a, point_b):
        return abs(point_a[0] - point_b[0]) + abs(point_a[1] - point_b[1])

    def mha_distance_for_overall_path(self, overall_path):
        overall_distance = 0
            
        for i in range(len(overall_path)-1):
            overall_distance += self.mha_distance(overall_path[i], overall_path[i+1])

        return overall_distance

    def walk(self, start_pos, end_pos):
        self.path.clear()

        self.c1, self.r1 = start_pos
        self.c2, self.r2 = end_pos

        chooser = randint(0,1)

        self.cur_r, self.cur_c = self.r1, self.c1
        
        if chooser:
            self.row()
            self.col()
        else:
            self.col()
            self.row()    

        return self.path

    def row(self):
        while self.cur_r != self.r2:
            if self.r1 > self.r2:
                self.cur_r -= 1
            else:
                self.cur_r += 1

            self.path.append((self.cur_c, self.cur_r))

    def col(self):
        while self.cur_c != self.c2:
            if self.c1 > self.c2:
                self.cur_c -= 1
            else:
                self.cur_c += 1

            self.path.append((self.cur_c, self.cur_r))