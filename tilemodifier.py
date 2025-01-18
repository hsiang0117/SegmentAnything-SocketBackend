import os
import struct

unsigned_int_format = '<I'
unsigned_char_format = 'B'


# Seek for the watermask extension.
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
        return watermask_bytearray

def tmp_get_new_mask():
    new_mask = b''


    return new_mask

# Get watermask bytearray that will be written back to the terrain file.
# This bytearray obtains by originate watermask from the terrain file and the segment result through an algorithm
# which considers the relative position of target tile and the area covered by segment result.
# returns
# 0 if whole tile is not covered by water.
# a bytearray with 256*256 bytes if partially water.
# 1 if whole tile is covered by water.
def get_watermask(mask, north, south, west, east):
    mask_bytearray = b''
    mask = mask.tolist()[0]

    for i in range(north, south):
        for j in range(west, east):
            if mask[i][j]:
                mask_bytearray += b'\xff'
            else:
                mask_bytearray += b'\x00'

    return mask_bytearray

def tmp(file_path, new_mask):
    pos = get_watermask_pos(file_path)
    if pos == -1:
        file = open(file_path, 'ab')
        file.write(b'\x02')
        if new_mask == 0:
            file.write(b'\x01\x00\x00\x00\x00')
        elif new_mask == 1:
            file.write(b'\x01\x00\x00\x00\x01')
        else:
            file.write(b'\x00\x00\x01\x00')
            file.write(new_mask)
        file.close()
    else:
        file = open(file_path, 'rb+')
        data_before_water = bytearray(file.read(pos))
        data_remain = bytearray(file.read())
        watermask_length = data_remain[0:4]
        watermask_length = struct.unpack(unsigned_int_format, watermask_length)[0]
        if new_mask == 0:
            if watermask_length == 1:
                data_remain[4] = b'\x00'
            else:
                data_remain[0:4] = b'\x01\x00\x00\x00'
                del data_remain[4:65540]
                data_remain[4] = b'\x00'
        elif new_mask == 1:
            if watermask_length == 1:
                data_remain[4] = b'\x01'
            else:
                data_remain[0:4] = b'\x01\x00\x00\x00'
                del data_remain[4:65540]
                data_remain[4] = b'\x01'
        else:
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

# Modify watermask within a single tile with segment result.
# If there's no watermask (input pos = -1) then add watermask to the terrain file.
def modify_watermask(file_path, mask, north, south, west, east):
    pos = get_watermask_pos(file_path)
    origin_watermask = read_watermask(file_path, pos)
    new_mask = get_watermask(mask, north, south, west, east)
    if pos == -1:
        file = open(file_path, 'ab')
        file.write(b'\x02')
        if new_mask == 0:
            file.write(b'\x01\x00\x00\x00\x00')
        elif new_mask == 1:
            file.write(b'\x01\x00\x00\x00\x01')
        else:
            file.write(b'\x00\x00\x01\x00')
            file.write(new_mask)
        file.close()
    else:
        file = open(file_path, 'rb+')
        data_before_water = bytearray(file.read(pos))
        data_remain = bytearray(file.read())
        watermask_length = data_remain[0:4]
        watermask_length = struct.unpack(unsigned_int_format, watermask_length)[0]
        if new_mask == 0:
            if watermask_length == 1:
                data_remain[4] = b'\x00'
            else:
                data_remain[0:4] = b'\x01\x00\x00\x00'
                del data_remain[4:65540]
                data_remain[4] = b'\x00'
        elif new_mask == 1:
            if watermask_length == 1:
                data_remain[4] = b'\x01'
            else:
                data_remain[0:4] = b'\x01\x00\x00\x00'
                del data_remain[4:65540]
                data_remain[4] = b'\x01'
        else:
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

def modify_tiles(lodLevel, mask, south, west, north, east):
    mask = mask.tolist()[0]
    folder_path = "E:/terrain/yaohujichang-19J/"
    folder_path += lodLevel
    folder_path += '/'

    for i in range(west,east+1):
        for j in range(north,south+1):
            new_mask = tmp_get_new_mask()
            file_path = folder_path + i + '/' + j + ".terrain"
            tmp(file_path, new_mask)
    return