import os
import struct

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
def get_watermask(file_path, pos, mask, corner, offset):
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


# Modify watermask within a single tile with the new mask which come from get_watermask().
# If there's no watermask (input pos = -1) then add watermask to the terrain file.
def modify_watermask(file_path, mask, corner, offset):
    pos = get_watermask_pos(file_path)
    new_mask = get_watermask(file_path, pos, mask, corner, offset)
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


# modify tiles that are covered by the segment result.
def modify_tiles(mask, terrain_folder_path, lod, bottom_left_and_top_right, offset):
    file_path = terrain_folder_path + lod + "\\" + bottom_left_and_top_right[0] + "\\" + \
                bottom_left_and_top_right[1] + ".terrain"
    if os.path.exists(file_path):
        modify_watermask(file_path, mask, 0, offset)
    file_path = terrain_folder_path + lod + "\\" + bottom_left_and_top_right[2] + "\\" + \
                bottom_left_and_top_right[1] + ".terrain"
    if os.path.exists(file_path):
        modify_watermask(file_path, mask, 1, offset)
    file_path = terrain_folder_path + lod + "\\" + bottom_left_and_top_right[0] + "\\" + \
                bottom_left_and_top_right[3] + ".terrain"
    if os.path.exists(file_path):
        modify_watermask(file_path, mask, 2, offset)
    file_path = terrain_folder_path + lod + "\\" + bottom_left_and_top_right[2] + "\\" + \
                bottom_left_and_top_right[3] + ".terrain"
    if os.path.exists(file_path):
        modify_watermask(file_path, mask, 3, offset)
