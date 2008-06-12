# The main loop for this

import sys
sys.path.append('src')

import Map

print 'Welcome to some lord2-like game!'

def main():
    map = 'map.dat'
    print 'Loading map from', map
    scr = Map.Screen()
    scr.load_file(map)

main()
