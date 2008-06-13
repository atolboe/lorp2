import os
import struct

data_dir = os.path.join('original/')
Map_max_x = 80
Map_max_y = 20

# Index gives the tile type
class Types:
    """Holds constants for terrain types."""
    unpassable = 0
    grass = 1
    rocky = 2
    water = 3
    forest = 4

    def __init__(self): raise Exception('cannot create an instance of this class')

class Screen:
    """Holds the data describing one map screen, i.e.: all the terrain,
    hotspots, etc.."""
    def __init__(self):
        self.tiles = list()
        self.pvp = False
        self.hotspots = list()

#TODO needs to be able to load all maps and probably move to another class..
    def load_file(self, filename):
        f = open(data_dir + filename, 'rb')

        name_size = struct.unpack('<B', f.read(1))[0] # Get first byte
        #print 'name_size:', name_size

        format = '<' + str(name_size) + 's'
        self.name = struct.unpack(format, f.read(name_size))[0] # Read map name
        #print 'name:', self.name

        # 001F - 259E Screen blocks in 6 block sections
        f.seek(0x1f) #TODO generalize this with f.tell()
#TODO check for blink
        for i in range((0x259f - 0x1f) / 6):
            vals = struct.unpack('<6B', f.read(6))
            #print values
            tile = Tile(False, vals[0], vals[1], vals[2], vals[5])
            self.tiles.append(tile)

        # 259F - 2AC6: Hot spots
        # Ten Hot spots supporting each 132 bytes in length
        for i in range((0x2ac7 - 0x259f) / 132):
            print ' --- Hotspot', i
            offset_start = f.tell()
            warp_map = struct.unpack('<2B', f.read(2))[0]
            print 'warp_map:', warp_map

            spot_x = struct.unpack('<B', f.read(1))[0]
            spot_y = struct.unpack('<B', f.read(1))[0]
            print 'spot:', spot_x, spot_y

            if (spot_x < 1 or spot_x > Map_max_x) or \
               (spot_y < 1 or spot_y > Map_max_y):
                f.seek(offset_start + 0x84) # Seek to next hotspot
                print 'Skipping hotspot', i
                continue

            warp_x = struct.unpack('<B', f.read(1))[0]
            warp_y = struct.unpack('<B', f.read(1))[0]
            print 'warp:', warp_x, warp_y

            ref_func = ref_file = None # Initialize these with nothing

            name_size = struct.unpack('<B', f.read(1))[0]
            #print 'name_size:', name_size
            if name_size is not 0:
                format = '<' + str(name_size) + 's'
                ref_func = struct.unpack(format, f.read(name_size))[0]
                print 'ref_func:', ref_func
            f.seek(offset_start + 0x13) # Skip to end of string field

            name_size = struct.unpack('<B', f.read(1))[0]
            #print 'name_size:', name_size
            if name_size is not 0:
                format = '<' + str(name_size) + 's'
                ref_file = struct.unpack(format, f.read(name_size))[0]
                print 'ref_file:', ref_file

            f.seek(offset_start + 0x84) # Skip a bit, Brother

            hotspot = Hotspot(warp_map, (spot_x, spot_y), (warp_x, warp_y), ref_func, ref_file)
            self.hotspots.append(hotspot)

#TODO additional map data from spec

        f.close()

class Tile:
    """An individual map square."""
    def __init__(self, blink, color, char, bgcolor, type):
        self.blink = blink
        self.char = char
        self.color = color
        self.bgcolor = bgcolor
        self.type = type

class Hotspot:
    """Marks the location and function of hotspots teleport a player to a
    specified location or execute some named script."""
    def __init__(self, warp_map, location, warp_location, ref_function, ref_file):
        self.warp_map = warp_map
        self.location = location  # tuple, (x, y)
        self.warp_location = warp_location # same as location
        self.ref_function = ref_function
        self.ref_file = ref_file

class World:
    """Defines how all map screens fit together"""
    pass
