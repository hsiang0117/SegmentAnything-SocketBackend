import os
import struct

unsigned_int_format = '<I'
unsigned_char_format = 'B'

path = "E:/terrain/yaohujichang-19J/18/431208/172968.terrain"

# seek for the watermask extension
# returns the position of watermask in the terrain file
# if there's no watermask returns -1
def get_watermask_pos(file_path):
    file = open(file_path,"rb")
    file_size = os.fstat(file.fileno()).st_size
    file.seek(88)
    vertex_count = file.read(4)
    vertex_count = struct.unpack(unsigned_int_format,vertex_count)[0]
    file.seek(2*vertex_count*3,1)
    triangle_count = file.read(4)
    triangle_count = struct.unpack(unsigned_int_format,triangle_count)[0]
    indices_size = 2 if triangle_count<65536 else 4
    file.seek(indices_size*triangle_count*3,1)
    west_vertex_count = file.read(4)
    west_vertex_count = struct.unpack(unsigned_int_format,west_vertex_count)[0]
    file.seek(2*west_vertex_count,1)
    south_vertex_count = file.read(4)
    south_vertex_count = struct.unpack(unsigned_int_format,south_vertex_count)[0]
    file.seek(2*south_vertex_count,1)
    east_vertex_count = file.read(4)
    east_vertex_count = struct.unpack(unsigned_int_format,east_vertex_count)[0]
    file.seek(2*east_vertex_count,1)
    north_vertex_count = file.read(4)
    north_vertex_count = struct.unpack(unsigned_int_format,north_vertex_count)[0]
    file.seek(2*north_vertex_count,1)
    while file.tell()<file_size:
        extension_type = file.read(1)
        extension_type = struct.unpack(unsigned_char_format,extension_type)[0]
        if(extension_type == 2):
            return file.tell()
        else:
            extension_length = file.read(4)
            extension_length = struct.unpack(unsigned_int_format,extension_length)[0]
            file.seek(extension_length,1)
    return -1

# determines if the whole tile is covered by water
# returns
# 0 if whole tile is not covered by water
# a bytearray that indicates the mask if partially water
# 1 if whole tile is covered by water
def analyse_mask(mask):

    return

# modify watermask with a 255*255 mask
# if there's no watermask (input pos = -1)
# then add watermask to the terrain file
def modify_watermask(file_path,mask):
    pos = get_watermask_pos(file_path)
    new_mask = analyse_mask(mask)
    if pos == -1:
        with open(file_path,'ab') as file:
            file.write(b'\x02')
        if new_mask == 0:
            file.write(b'\x01\x00\x00\x00\x00')
        elif new_mask == 1:
            file.write(b'\x01\x00\x00\x00\x01')
        else:
            file.write(new_mask)
        file.close()
    else:
        with open(file_path,'rb+') as file:
            data_before_water = bytearray(file.read(pos))
            data_remain = bytearray(file.read())
            watermask_length = data_remain[0:4]
            watermask_length = struct.unpack(unsigned_int_format,watermask_length)[0]
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
                data_remain.insert(4,new_mask)
            else:
                del data_remain[4:65540]
                data_remain.insert(4,new_mask)
            return
        file.close()

        # write back
        with open(file_path,'wb') as file:
            data = data_before_water + data_remain
            file.write(data)





print(get_watermask_pos(path))