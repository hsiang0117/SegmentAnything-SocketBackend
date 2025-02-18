import struct

import matplotlib.pyplot as plt

from tilemodifier import *
pos = get_watermask_pos("D:\\terrain\\yaohujichang-19J\\12\\6736\\2699.terrain")
origin_length,origin_watermask = read_watermask("D:\\terrain\\yaohujichang-19J\\12\\6736\\2699.terrain",pos)