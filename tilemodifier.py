import os
import struct
import threading
from math import floor

unsigned_int_format = '<I'
unsigned_char_format = 'B'


# convert mask from bool list to byte list.
def analyse_mask(mask):
    for i in range(len(mask)):
        for j in range(len(mask[0])):
            if mask[i][j]:
                mask[i][j] = b'\xff'
            else:
                mask[i][j] = b'\x00'
    return mask


# Seek for watermask extension.
# Returns the position of watermask in the terrain file.
# Returns -1 if there's no watermask.
def get_watermask_pos(file_path):
    file = open(file_path, "rb")
    file_size = os.fstat(file.fileno()).st_size
    file.seek(88)
    vertex_count = file.read(4)
    vertex_count = struct.unpack(unsigned_int_format, vertex_count)[0]
    file.seek(2 * vertex_count * 3, 1)
    triangle_count = file.read(4)
    triangle_count = struct.unpack(unsigned_int_format, triangle_count)[0]
    indices_size = 2 if triangle_count < 65536 else 4
    file.seek(indices_size * triangle_count * 3, 1)
    west_vertex_count = file.read(4)
    west_vertex_count = struct.unpack(unsigned_int_format, west_vertex_count)[0]
    file.seek(2 * west_vertex_count, 1)
    south_vertex_count = file.read(4)
    south_vertex_count = struct.unpack(unsigned_int_format, south_vertex_count)[0]
    file.seek(2 * south_vertex_count, 1)
    east_vertex_count = file.read(4)
    east_vertex_count = struct.unpack(unsigned_int_format, east_vertex_count)[0]
    file.seek(2 * east_vertex_count, 1)
    north_vertex_count = file.read(4)
    north_vertex_count = struct.unpack(unsigned_int_format, north_vertex_count)[0]
    file.seek(2 * north_vertex_count, 1)
    while file.tell() < file_size:
        extension_type = file.read(1)
        extension_type = struct.unpack(unsigned_char_format, extension_type)[0]
        if extension_type == 2:
            return file.tell()
        else:
            extension_length = file.read(4)
            extension_length = struct.unpack(unsigned_int_format, extension_length)[0]
            file.seek(extension_length, 1)
    return -1


def read_watermask(file_path, pos):
    file = open(file_path, 'rb')
    if pos == -1:
        return -1
    else:
        file.seek(pos)
        watermask_length = file.read(4)
        watermask_length = struct.unpack(unsigned_int_format, watermask_length)[0]
        watermask_bytearray = file.read(watermask_length)
        return watermask_length, watermask_bytearray


# Get watermask bytearray that will be written back to the terrain file.
# This bytearray obtains by originate watermask from the terrain file and the segment result through an algorithm
# which considers the relative position of target tile and the area covered by segment result.
def get_watermask(file_path, mask, corner, offset):
    pos = get_watermask_pos(file_path)
    new_mask = b''
    if pos == -1:
        if corner == 0:
            for i in range(0, 256):
                for j in range(0, 256):
                    if j >= offset[0] and i <= (255 - offset[1]):
                        new_mask += mask[i + offset[1]][j - offset[0]]
                    else:
                        new_mask += b'\x00'
        elif corner == 1:
            for i in range(0, 256):
                for j in range(0, 256):
                    if j <= offset[0] and i <= (255 - offset[1]):
                        new_mask += mask[i + offset[1]][j + 255 - offset[0]]
                    else:
                        new_mask += b'\x00'
        elif corner == 2:
            for i in range(0, 256):
                for j in range(0, 256):
                    if j >= offset[0] and i >= (255 - offset[1]):
                        new_mask += mask[i + offset[1] - 255][j - offset[0]]
                    else:
                        new_mask += b'\x00'
        elif corner == 3:
            for i in range(0, 256):
                for j in range(0, 256):
                    if j <= offset[0] and i >= (255 - offset[1]):
                        new_mask += mask[i + offset[1] - 255][j + 255 - offset[0]]
                    else:
                        new_mask += b'\x00'
    else:
        origin_length, origin_mask = read_watermask(file_path, pos)
        if origin_length == 1:
            if corner == 0:
                for i in range(0, 256):
                    for j in range(0, 256):
                        if j >= offset[0] and i <= (255 - offset[1]):
                            new_mask += mask[i + offset[1]][j - offset[0]]
                        else:
                            if origin_mask == 0:
                                new_mask += b'\x00'
                            else:
                                new_mask += b'\xff'
            elif corner == 1:
                for i in range(0, 256):
                    for j in range(0, 256):
                        if j <= offset[0] and i <= (255 - offset[1]):
                            new_mask += mask[i + offset[1]][j + 255 - offset[0]]
                        else:
                            if origin_mask == 0:
                                new_mask += b'\x00'
                            else:
                                new_mask += b'\xff'
            elif corner == 2:
                for i in range(0, 256):
                    for j in range(0, 256):
                        if j >= offset[0] and i >= (255 - offset[1]):
                            new_mask += mask[i + offset[1] - 255][j - offset[0]]
                        else:
                            if origin_mask == 0:
                                new_mask += b'\x00'
                            else:
                                new_mask += b'\xff'
            elif corner == 3:
                for i in range(0, 256):
                    for j in range(0, 256):
                        if j <= offset[0] and i >= (255 - offset[1]):
                            new_mask += mask[i + offset[1] - 255][j + 255 - offset[0]]
                        else:
                            if origin_mask == 0:
                                new_mask += b'\x00'
                            else:
                                new_mask += b'\xff'
        else:
            if corner == 0:
                for i in range(0, 256):
                    for j in range(0, 256):
                        if j >= offset[0] and i <= (255 - offset[1]):
                            new_mask += mask[i + offset[1]][j - offset[0]]
                        else:
                            new_mask += struct.pack(unsigned_char_format, origin_mask[i * 256 + j])
            elif corner == 1:
                for i in range(0, 256):
                    for j in range(0, 256):
                        if j <= offset[0] and i <= (255 - offset[1]):
                            new_mask += mask[i + offset[1]][j + 255 - offset[0]]
                        else:
                            new_mask += struct.pack(unsigned_char_format, origin_mask[i * 256 + j])
            elif corner == 2:
                for i in range(0, 256):
                    for j in range(0, 256):
                        if j >= offset[0] and i >= (255 - offset[1]):
                            new_mask += mask[i + offset[1] - 255][j - offset[0]]
                        else:
                            new_mask += struct.pack(unsigned_char_format, origin_mask[i * 256 + j])
            elif corner == 3:
                for i in range(0, 256):
                    for j in range(0, 256):
                        if j <= offset[0] and i >= (255 - offset[1]):
                            new_mask += mask[i + offset[1] - 255][j + 255 - offset[0]]
                        else:
                            new_mask += struct.pack(unsigned_char_format, origin_mask[i * 256 + j])
    return new_mask


def write_back(file_path, new_mask):
    pos = get_watermask_pos(file_path)
    if pos == -1:
        file = open(file_path, 'ab')
        file.write(b'\x02\x00\x00\x01\x00')
        file.write(new_mask)
        file.close()
    else:
        file = open(file_path, 'rb+')
        data_before_water = bytearray(file.read(pos))
        data_remain = bytearray(file.read())
        watermask_length = data_remain[0:4]
        watermask_length = struct.unpack(unsigned_int_format, watermask_length)[0]
        if watermask_length == 1:
            data_remain[0:4] = b'\x00\x00\x01\x00'
            del data_remain[4]
            data_remain += new_mask
        else:
            del data_remain[4:]
            data_remain += new_mask
        file.close()

        # write back
        with open(file_path, 'wb') as file:
            data = data_before_water + data_remain
            file.write(data)
    print(file_path + " done")


# Modify watermask within a single tile with the new mask which come from get_watermask().
# If there's no watermask (input pos = -1) then add watermask to the terrain file.
def modify_watermask(file_path, mask, corner, offset):
    new_mask = get_watermask(file_path, mask, corner, offset)
    write_back(file_path, new_mask)


# Expand a mask by nearest interpolation.
# For example from 128*128 to 256*256.
def mask_interpolation(mask):
    expanded_mask = b''
    for i in range(256):
        for j in range(256):
            expanded_mask += struct.pack(unsigned_char_format, mask[floor(i / 2) * 128 + floor(j / 2)])
    return expanded_mask


def modify_child(parent_path, file_path, corner):
    parent_pos = get_watermask_pos(parent_path)
    parent_length, parent_mask = read_watermask(parent_path, parent_pos)
    origin_mask = b''
    if corner == 0:
        for i in range(128, 256):
            origin_mask += parent_mask[i * 256:i * 256 + 128]
    elif corner == 1:
        for i in range(128, 256):
            origin_mask += parent_mask[i * 256 + 128:i * 256 + 256]
    elif corner == 2:
        for i in range(128):
            origin_mask += parent_mask[i * 256:i * 256 + 128]
    else:
        for i in range(128):
            origin_mask += parent_mask[i * 256 + 128:i * 256 + 256]
    new_mask = mask_interpolation(origin_mask)
    write_back(file_path, new_mask)


# Modify child tiles of higher lod level after modifying a tile
def recursive_downward_modify(terrain_folder_path, lod, X, Y):
    parent_path = terrain_folder_path + str(lod) + "\\" + str(X) + "\\" + str(Y) + ".terrain"
    for i in range(2):
        for j in range(2):
            child_path = terrain_folder_path + str(lod + 1) + "\\" + str(X * 2 + j) + "\\" + str(Y * 2 + i) + ".terrain"
            if os.path.exists(child_path):
                modify_child(parent_path, child_path, 2 * i + j)
                recursive_downward_modify(terrain_folder_path, lod + 1, X * 2 + j, Y * 2 + i)


class multi_thread(threading.Thread):
    def __init__(self, mask, terrain_folder_path, lod, X, Y, offset, corner):
        threading.Thread.__init__(self)
        self.mask = mask
        self.terrain_folder_path = terrain_folder_path
        self.lod = lod
        self.X = X
        self.Y = Y
        self.offset = offset
        self.corner = corner

    def run(self):
        file_path = self.terrain_folder_path + self.lod + "\\" + self.X + "\\" + self.Y + ".terrain"
        if (os.path.exists(file_path)):
            modify_watermask(file_path, self.mask, self.corner, self.offset)
            recursive_downward_modify(self.terrain_folder_path, int(self.lod), int(self.X), int(self.Y))
        print("thread-" + str(self.corner) + " down")


# modify tiles that are covered by the segment result.
def modify_tiles(mask, terrain_folder_path, lod, bottom_left_and_top_right, offset):
    thread0 = multi_thread(mask,terrain_folder_path,lod,bottom_left_and_top_right[0],bottom_left_and_top_right[1],offset,0)
    thread1 = multi_thread(mask,terrain_folder_path,lod,bottom_left_and_top_right[2],bottom_left_and_top_right[1],offset,1)
    thread2 = multi_thread(mask,terrain_folder_path,lod,bottom_left_and_top_right[0],bottom_left_and_top_right[3],offset,2)
    thread3 = multi_thread(mask,terrain_folder_path,lod,bottom_left_and_top_right[2],bottom_left_and_top_right[3],offset,3)

    thread0.start()
    thread1.start()
    thread2.start()
    thread3.start()

    thread0.join()
    thread1.join()
    thread2.join()
    thread3.join()

    print("modify finished")