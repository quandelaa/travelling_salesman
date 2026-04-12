def mha_distance(point_a, point_b):
    return abs(point_a[0] - point_b[0]) + abs(point_a[1] - point_b[1])

def walk(start_pos, end_pos):
    path = []

    c1, r1 = start_pos
    c2, r2 = end_pos

    cur_r, cur_c = r1, c1

    while cur_r != r2:
        if r1 > r2:
            cur_r -= 1
        else:
            cur_r += 1

        path.append((cur_c, cur_r))

    while cur_c != c2:
        if c1 > c2:
            cur_c -= 1
        else:
            cur_c += 1

        path.append((cur_c, cur_r))

    return path