import numpy as np

def point_in_polygon(x, y, poly):
    """
    使用射线法（奇偶规则）判断点 (x, y) 是否在由 poly 定义的多边形内部。
    poly 是一个[(x0, y0), (x1, y1), ..., (xn-1, yn-1)]的列表，按顺序构成闭合路径。
    返回 True 表示内部，False 表示外部。
    """
    inside = False
    n = len(poly)
    # 从第一个顶点开始
    p1x, p1y = poly[0]
    for i in range(1, n + 1):
        p2x, p2y = poly[i % n]
        # 如果 y 在 p1y 和 p2y 之间（注意严格判断下界）
        if min(p1y, p2y) < y <= max(p1y, p2y):
            # 计算交点的 x 坐标
            # 注意：当 p1y==p2y 时避免除0
            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y + 1e-10) + p1x
            if x <= xinters:
                inside = not inside
        p1x, p1y = p2x, p2y
    return inside

def fill_polygon(poly, size=(256, 256)):
    """
    给定多边形 poly（一个顶点列表）以及画布尺寸，返回一个 numpy 数组，
    数组内所有位于多边形内部的点置为 1，其它点保持为 0。
    为了更精确判断，我们检测的是每个像素中心点 (x+0.5, y+0.5)。
    """
    height, width = size
    canvas = np.zeros((height, width), dtype=np.uint8)
    for y in range(height):
        for x in range(width):
            if point_in_polygon(x + 0.5, y + 0.5, poly):
                canvas[y, x] = 1
    return canvas

# 示例：定义一个正方形多边形（按顺序给出顶点）
polygon = [(50, 50), (200, 50), (50, 200), (200, 200) ]

if __name__ == '__main__':
    filled = fill_polygon(polygon)
    # 可以用 matplotlib 显示结果
    import matplotlib.pyplot as plt
    plt.imshow(filled, cmap='gray')
    plt.title("Filled Polygon using Even-Odd Rule")
    plt.show()