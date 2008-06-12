import os
import struct

data_dir = os.path.join('original/')

# Index gives the tile type
class Types:
    """Holds constants for terrain types."""
    unpassable = 0
    grass = 1
    rocky = 2
    water = 3
    forest = 4

    def init(self): raise Exception('cannot create an instance of this class')

class Screen:
    """Holds the data describing one map screen, i.e.: all the terrain,
    hotspots, etc.."""
    def init(self):
        self.tiles = list()

    def load_file(self, filename):
        f = open(data_dir + filename, 'rb')

        name_size = struct.unpack('<B', f.read(1))[0] # Get first byte
        #print 'name_size:', name_size

        format = '<' + str(name_size) + 's'
        self.name = struct.unpack_from(format, f.read(name_size))[0] # Read map name
        #print 'name:', self.name

        # 001F - 259E Screen blocks in 6 block sections
        f.seek(0x1f)
#TODO check for blink
        for tile in range((0x259e - 0x1f) / 6, 6):
            vals = struct.unpack('<6B', f.read(6))
            #print values
            tile = Tile(False, vals[0], vals[1], vals[2], vals[5])

        f.close()

class Tile:
    """An individual map square."""
    def init(self, blink, color, char, bgcolor, type):
        self.blink = blink
        self.char = char
        self.color = color
        self.bgcolor = bgcolor
        self.type = type

class World:
    """Defines how all map screens fit together"""
    pass
