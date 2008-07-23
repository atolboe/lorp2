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

class World:
	"""Holds the data describing one map screen, i.e.: all the terrain,
	hotspots, etc.."""
	def __init__(self):
		self.maps = list()

	def load_world_file(self, filename):
		self.worlddata = list() #this should be here so if worlddata was used before it will not be empty

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
			print 'map:', map
			#extract map to block mapping
			f.seek(map_num_offset + (map * 2))
			
			#TODO: Fix me
			#for some reason map_loc is only picking up one byte instead of two
			map_loc = struct.unpack('<2B', f.read(2))[0]

			print 'map_loc:', map_loc
			
			#extract visibility
			f.seek(map_visible_offset + map)
			visible = struct.unpack('<B', f.read(1))[0]

			if ((map_loc > 0) and (visible == 0)):
				visible = True
			else:
				visible = False

			print 'visible: ',visible
			
			tmp = WorldData(map_loc, visible)
			self.worlddata.append(tmp)

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
					blink = True
				else:
					blink = False

				tile = Tile(blink, int(vals[0]) & 0x0F, vals[1], vals[2], vals[5])
				tiles.append(tile)

			# 259F - 2AC6: Hot spots
			# Ten Hot spots supporting each 132 bytes in length
			for i in range(((0x2ac7 + map_offset) - (map_offset + 0x259f)) / 132):
				#print ' --- Hotspot', i
				offset_start = f.tell()
				warp_map = struct.unpack('<2B', f.read(2))[0]
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
			
			rand = struct.unpack('<2B', f.read(2))[0]
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
				pvp = False
			else:
				pvp = True
			
			#print 'pvp:',pvp

			tmp = Map(name, tiles, hotspots, rand, ref_file, ref_function, pvp)
			self.maps.append(tmp)

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
