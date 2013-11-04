#!/usr/bin/python

# Made By TJ Corley
# Code under MIT License

import sys, getopt
import xml.etree.ElementTree as ET

def main(argv):
    """Converts svgs from www.mazegenerator.se into valid jkarel maps
       Usage: maze_converter.py -i <inputfile> -o <outputfile>
    """
    try:
        #get arguments from command line
        opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
    except getopt.GetoptError:
    #if the arguments aren't right print the usage
        print 'maze_converter.py -i <inputfile> -o <outputfile>'
        sys.exit(2)
    if not argv:
    #if no arguments print the usage
        print 'maze_converter.py -i <inputfile> -o <outputfile>'
        sys.exit(2) 
    for opt, arg in opts:
        if opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-o", "--ofile"):
            outputfile = arg
        else:
            #if misplaced arguments print usage
            print 'maze_converter.py -i <inputfile> -o <outputfile>'    
    #set up new .map file
    #every .map file has a root element called world
    jkarel_root = ET.Element("world")
    #in the root element there is a subelement called properties
    properties = ET.SubElement(jkarel_root, "properties")
    #all that is stored in properties is the defaultSize
    #defaultSize has two variables called height and weight
    #We get those values later on from the .svg
    default_size = ET.SubElement(properties, "defaultSize")
    #the world element also has a subelement called objects
    #objects stores all the info of the walls
    objects = ET.SubElement(jkarel_root, "objects")
    #Now we need to start parsing the inputted svg
    tree = ET.parse(inputfile)
    doc = tree.getroot()
    #the root element has height and weight attributes
    #Each block in the .svg is 16 pixels wide
    #so if we divivde each attribute by 16...
    #we should get the size of the map
    default_height = int(doc.attrib['height'])/16
    default_width = int(doc.attrib['width'])/16
    default_size.set('height',"%s" % default_height)
    default_size.set('width','%s' % default_width)
    #in the g tag there are a whole lot of line elements
    for line in doc.findall('{http://www.w3.org/2000/svg}g/*'):
        #each line has an x1,x2,y1,y2 attribute
        #we can calculate its coordinate on the jkarel map by dividing by 16
        #well almost...
        #Both formats have a different defintion of the origin
        #So we need to convert the y values so they can be usable
        x1 = (int(line.attrib['x1']) / 16)
        y1 = default_height - (int(line.attrib['y2']) / 16)
        x2 = (int(line.attrib['x2']) / 16)
        y2 = default_height -(int(line.attrib['y1']) / 16)
        #now that we have the coordinates we have to analyze what is happening
        #if both the x values are the same we are drawing a vertical line
        #the length then has to be the y2 - y1
        if x1 == x2:
            style = 'vertical'
            length = y2 - y1
        #if both of the y values are the same it is horizontal
        #and the lenght is x2 - x1
        else:
            style = 'horizontal'
            length = x2 - x1
        #This is the sort of annoying part
        #There is a length attribute in the jkarel format
        #So i thought it would make sense to use our calculated length
        #Instead that screws everything up
        #and we have to draw walls with a length of 1 calculated length times 
        while length > 0:
            #walls are subelements of object elements
            wall = ET.SubElement(objects, "wall")
            #if it is horizontal we draw right to left
            if style == 'horizontal':
                wall.set('x','%s' % (x1 + length))
                wall.set('y','%s' % (y1))
            #if vertical we draw up to down
            else:
                wall.set('x','%s' % (x1))
                wall.set('y','%s' % (y1 + length))
            #length is always one
            #it is like this in the map creator also
            #maybe something screwed up in jkarel?
            wall.set('length','1')
            #vertical or horizontal
            wall.set('style',style)
            length -= 1
    #now we get the finished .map and write it to disc
    tree = ET.ElementTree(jkarel_root)
    tree.write(outputfile)
    #all done
    print 'Successfully converted .svg into .map file'
if __name__ == "__main__":
    main(sys.argv[1:])
    
