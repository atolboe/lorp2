import os
import struct
from pysqlite2 import dbapi2 as sqlite

data_dir = os.path.join('original/')
sql_dir = os.path.join('data/')
Map_max_x = 80
Map_max_y = 20

#Singleton object
class Singleton(object):
    def __new__(cls, *args, **kwargs):
        if '_inst' not in vars(cls):
            cls._inst = super(Singleton, cls).__new__(cls, *args, **kwargs)
        return cls._inst


# Index gives the tile type
class Types:
    """Holds constants for terrain types."""
    unpassable = 0
    grass = 1
    rocky = 2
    water = 3
    forest = 4

    def __init__(self): raise Exception('cannot create an instance of this class')

class World(Singleton):
    """Holds the data describing one map screen, i.e.: all the terrain,
    hotspots, etc.."""
    def __init__(self):
        if 'maps' not in vars(self):
            if os.path.isfile( sql_dir + 'world.dat' ):
                self.load_world_data()
            else:
                self.maps = list()

    def load_world_file(self, filename):
        self.worldata = list() #this should be here so if worldata was used before it will not be empty

        #set some useful values
        map_num_offset = 0x3D
        map_visible_offset = 0x108B

        f = open(data_dir + filename, 'rb')

        #first lets get the name
        name_size = struct.unpack('<B', f.read(1))[0] # Get first byte

        format = '<' + str(name_size) + 's'
        self.name = struct.unpack(format, f.read(name_size))[0] # Read world name

        #Now itterate through all of the possible world blocks
        for map in range(0,1600):
            #extract map to block mapping
            f.seek(map_num_offset + (map * 2))
            
            #for some reason map_loc is only picking up one byte instead of two
            map_loc = struct.unpack('<H', f.read(2))[0]
            
            #extract visibility
            f.seek(map_visible_offset + map)
            visible = struct.unpack('<B', f.read(1))[0]

            if ((map_loc > 0) and (visible == 0)):
                visible = 1 
            else:
                visible = 0

            
            tmp = WorldData(map_loc, visible)
            self.worldata.append(tmp)

        f.close()

    def load_map_file(self, filename):
        fsize = os.path.getsize(data_dir + filename)
        #print 'file_size:', fsize

        f = open(data_dir + filename, 'rb')

        for map in range(fsize / 0x2CBB):
            #print 'map:', map
            map_offset = map * 0x2CBB
            #print 'map_offset', map_offset
            
            #seek to the start of this map data
            f.seek(map_offset)
            tiles = list()
            hotspots = list()


            name_size = struct.unpack('<B', f.read(1))[0] # Get first byte
            #print 'name_size:', name_size

            format = '<' + str(name_size) + 's'
            name = struct.unpack(format, f.read(name_size))[0] # Read map name
            #print 'name:', name

            # 001F - 259E Screen blocks in 6 block sections
            f.seek(map_offset + 0x1f)
            
            #Proccess all of the tiles
            for i in range(((0x259f + map_offset) - ( map_offset + 0x1f)) / 6):
                vals = struct.unpack('<6B', f.read(6))
                #Check for the blink bit, if its set set to true
                if  ( int(vals[0]) & 0xF0 ) > 0:
                    blink = 1
                else:
                    blink = 0

                tile = Tile(blink, int(vals[0]) & 0x0F, vals[1], vals[2], vals[5])
                tiles.append(tile)

            # 259F - 2AC6: Hot spots
            # Ten Hot spots supporting each 132 bytes in length
            for i in range(((0x2ac7 + map_offset) - (map_offset + 0x259f)) / 132):
                #print ' --- Hotspot', i
                offset_start = f.tell()
                warp_map = struct.unpack('<H', f.read(2))[0]
                #print 'warp_map:', warp_map

                spot_x = struct.unpack('<B', f.read(1))[0]
                spot_y = struct.unpack('<B', f.read(1))[0]
                #print 'spot:', spot_x, spot_y

                if (spot_x < 1 or spot_x > Map_max_x) or \
                   (spot_y < 1 or spot_y > Map_max_y):
                    f.seek(offset_start + 0x84) # Seek to next hotspot
                    #print 'Skipping hotspot', i
                    continue

                warp_x = struct.unpack('<B', f.read(1))[0]
                warp_y = struct.unpack('<B', f.read(1))[0]
                #print 'warp:', warp_x, warp_y

                ref_func = ref_file = None # Initialize these with nothing

                name_size = struct.unpack('<B', f.read(1))[0]
                #print 'name_size:', name_size
                if name_size is not 0:
                    format = '<' + str(name_size) + 's'
                    ref_func = struct.unpack(format, f.read(name_size))[0]
                    #print 'ref_func:', ref_func
                
                f.seek(offset_start + 0x13) # Skip to end of string field

                name_size = struct.unpack('<B', f.read(1))[0]
                #print 'name_size:', name_size
                
                if name_size is not 0:
                    format = '<' + str(name_size) + 's'
                    ref_file = struct.unpack(format, f.read(name_size))[0]
                    #print 'ref_file:', ref_file

                f.seek(offset_start + 0x84) # Skip a bit, Brother

                hotspot = Hotspot(warp_map, (spot_x, spot_y), (warp_x, warp_y), ref_func, ref_file)
                hotspots.append(hotspot)

            f.seek(map_offset + 0x2AC7) #move to where the final map data is
            
            rand = struct.unpack('<H', f.read(2))[0]
            #print 'rand:', rand

            ref_file = ref_function = None #Init these with nothing
            f.seek(map_offset + 0x2ACB ); #Seek to the map file location
            ref_file_size =  struct.unpack('<B', f.read(1))[0]
            #print 'ref_file_size:', ref_file_size
            
            if ref_file_size is not 0:
                format = '<' + str(ref_file_size) + 's'
                ref_file = struct.unpack(format, f.read(ref_file_size))[0]
                #print 'ref_file:', ref_file

            #seek to the ref size element
            f.seek( map_offset + 0x2AD8 )

            ref_function_size =  struct.unpack('<B', f.read(1))[0]
            #print 'ref_function_size:', ref_function_size

            if ref_function_size is not 0:
                format = '<' + str(ref_function_size) + 's'
                ref_function = struct.unpack(format, f.read(ref_function_size))[0]
                #print 'ref_function:', ref_function
        
            #seek to the pvp section
            f.seek( map_offset + 0x2AE5 )
            pvp = struct.unpack('<B', f.read(1))[0]

            if pvp is 1:
                pvp = 0
            else:
                pvp = 1 
            
            #print 'pvp:',pvp

            tmp = Map(name, tiles, hotspots, rand, ref_file, ref_function, pvp)
            self.maps.append(tmp)

        f.close()

    def build_table_struct( self, sql ):
        cur = sql.cursor()

        cur.execute('SELECT name FROM sqlite_master WHERE type = \'table\'')

        #put all of the tables into a list
        tables = list()
        for table in cur:
            tables.append(str(table[0]))

        #check to see if each table is in the db and if its not then add it
        if 'hotspots' not in tables:
            hotspots_tbl="""create table hotspots
            (
                map     integer,
                x       integer,
                y       integer,
                warp_map    integer,
                warp_x      integer,
                warp_y      integer,
                ref_file        varchar(12),
                ref_function    varchar(12)
            );"""
            
            cur.execute(hotspots_tbl)

        if 'tiles' not in tables:
            tiles_tbl="""create table tiles
            (
                map     integer,
                x       integer,
                y       integer,
                blink       integer,
                char        integer,
                color       integer,
                bgcolor     integer,
                type        integer
            );"""

            cur.execute(tiles_tbl)

        if 'maps' not in tables:
            maps_tbl="""create table maps
            (
                map     integer,
                name        varchar(30),
                rand        integer,
                ref_file        varchar(12),
                ref_function    varchar(12),
                pvp     integer
            );"""

            cur.execute(maps_tbl)

        if 'world' not in tables:
            world_tbl="""create table world
            (
                key     varchar(4),
                val   varchar(60)
            );"""

            cur.execute(world_tbl)

        #clean up
        sql.commit()

    def load_world_data( self, file = 'world.dat' ):
        if not os.path.isfile( sql_dir + file ):
            return

        #clear the maps list
        self.maps = list()
        
        #load the file
        sql = sqlite.connect(sql_dir + file)

        cur = sql.cursor()

        #load all of the maps
        cur.execute("select * from maps where 1")

        #proccess all maps and put them in a dict since I'm not sure how it will come out
        tmpmaps = dict()
        for (mapid,name,rand,ref_file,ref_function,pvp) in cur:
            if ref_file:
                ref_file = str(ref_file)
            else:
                ref_file = ''
            if ref_function:
                ref_function = str(ref_function)
            else:
                ref_function = ''

            tmpmaps[(mapid-1)] = (str(name), int(rand), ref_file, ref_function, int(pvp))
        
        for index in range(0,len(tmpmaps)):
            #load all of the hotspots
            hotspots = list()
            cur.execute("select * from hotspots where map=" + str(index+1))
            
            for hotspot in cur:
                hotspots.append(Hotspot(int(hotspot[3]), (int(hotspot[1]), int(hotspot[2])), (int(hotspot[4]), int(hotspot[5])), str(hotspot[6]), str(hotspot[7])))
            #now load the tiles
            tilestmp = dict() #we have to fix this in a minute
            cur.execute("select * from tiles where map=" + str(index+1))
            for tiles in cur:
                x = int(tiles[1]) - 1
                y = int(tiles[2]) - 1
                indx = (x*20)+y
                tilestmp[indx] = Tile(int(tiles[3]),int(tiles[5]),int(tiles[4]),int(tiles[6]),int(tiles[7]))

            #now move it from the dict to the list
            tiles = list()
            for indx in range(0,1600):
                tiles.append(tilestmp[indx])

            self.maps.append(Map(tmpmaps[index][0], tiles, hotspots, tmpmaps[index][1], tmpmaps[index][2], tmpmaps[index][3],tmpmaps[index][4]))

        tmpworld = dict()
        
        #now load world data
        cur.execute("select * from world where 1")
        for key,val in cur:
            if str(key) == 'name':
                self.name = str(val)
            else:
                tmpworld[int(key)] = WorldData(int(str(val).split()[0]),int(str(val).split()[1]))
        
        self.worldata = list()
        #sort data
        for index in range(0,1600):
            self.worldata.append(tmpworld[index])

    def save_world_data( self, file = 'world.dat' ):
        #check to see if the file exists and if it does
        #delete it
        if os.path.isfile( sql_dir + file ):
            os.unlink( sql_dir + file )
        
        #load the file and lets populate the structure
        sql = sqlite.connect(sql_dir + file)

        self.build_table_struct( sql )

        cur = sql.cursor()
        
        #load maps
        for index,map in enumerate(self.maps):
            #calculate map id
            mapid = index+1

            #insert all of the map information
            cur.execute("insert into maps (map, name, rand, ref_file, ref_function, pvp) values (?, ?, ?, ?, ?, ?)", (mapid, map.name, map.rand, map.ref_file, map.ref_function, map.pvp))
            
            #now we need to insert tiles and hotspots
            for hotspot in map.hotspots:
                data = (mapid, hotspot.location[0], hotspot.location[1], hotspot.warp_map, hotspot.warp_location[0], hotspot.warp_location[1], hotspot.ref_file, hotspot.ref_function)
                cur.execute("insert into hotspots (map, x, y, warp_map, warp_x, warp_y, ref_file, ref_function) values (?, ?, ?, ?, ?, ?, ?, ?)", data)

            for index,tile in enumerate(map.tiles):
                x = (index/20) + 1
                y = (index%20) + 1
                data = ( mapid, x, y, tile.blink, tile.char, tile.color, tile.bgcolor, tile.type ) 
                cur.execute("insert into tiles (map, x, y, blink, char, color, bgcolor, type) values (?, ?, ?, ?, ?, ?, ?, ?)", data)
        
        #first store the name
        cur.execute("insert into world (key, val) values (?, ?)", ("name",self.name))
        
        for index,data in enumerate(self.worldata):
            key = str(index)
            val = str(data.map) + " " + str(data.visible)
            cur.execute("insert into world (key, val) values (?, ?)", (key,val))
        
        #commit changes
        sql.commit()


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
class Map:
    """Holds all of the data for a single map element"""
    def __init__(self, name, tiles, hotspots, rand, ref_file, ref_function, pvp):
        self.name = name
        self.tiles = tiles
        self.hotspots = hotspots
        self.rand = rand
        self.ref_file = ref_file
        self.ref_function = ref_function
        self.pvp = pvp
class WorldData:
    """Holds all of the map data for a world"""
    def __init__(self, map, visible):
        self.map = map
        self.visible = visible
