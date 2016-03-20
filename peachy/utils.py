import os
import pygame
import xml.dom.minidom
from pygame.locals import *

import peachy
from peachy import DEBUG

class Point(object):
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y
    def __str__(self):
        return "({0}, {1})".format(self.x, self.y)

def open_xml(path):
    try:
        xml_file = open(path, 'r')
        data = xml_file.read()
        xml_file.close()
        return xml.dom.minidom.parseString(data)
    except IOError:
        DEBUG('[ERROR] could not load xml file: ' + path)


class Camera(object):
    
    def __init__(self, view_width, view_height, speed=1):
        self.x = 0
        self.y = 0

        self.view_width = view_width
        self.view_height = view_height
        self.max_width = -1
        self.max_height = -1

        self.speed = speed
        self.target_x = 0
        self.target_y = 0

    def snap(self, target_x, target_y, center=False):
        self.snap_x(target_x, center)
        self.snap_y(target_y, center)

    def snap_x(self, target_x, center=False):
        if center:
            target_x -= self.view_width / 2
        self.x = target_x
        if self.x < 0:
            self.x = 0
        elif self.x + self.view_width > self.max_width:
            self.x = self.max_width - self.view_width

    def snap_y(self, target_y, center=False):
        if center:
            target_y -= self.view_height / 2
        self.y = target_y
        if self.y < 0:
            self.y = 0
        elif self.y + self.view_height > self.max_height:
            self.y = self.max_height - self.view_height

    def pan(self, target_x, target_y, center=False):
        self.pan_x(target_x, center)
        self.pan_y(target_y, center)

    def pan_x(self, target_x, center=False, speed=None):
        if speed is None:
            speed = self.speed
        if center:
            target_x -= self.view_width / 2

        if target_x < 0:
            target_x = 0
        elif target_x + self.view_width > self.max_width:
            target_x = self.max_width - self.view_width

        if self.x + speed < target_x:
            self.x += speed
        elif self.x - speed > target_x:
            self.x -= speed
        else:
            self.x = target_x

    def pan_y(self, target_y, center=False, speed=None):
        if speed is None:
            speed = self.speed
        if center:
            target_y -= self.view_height / 2

        if target_y < 0:
            target_y = 0
        elif target_y + self.view_height > self.max_height:
            target_y = self.max_height - self.view_height

        if self.y + speed < target_y:
            self.y += speed
        elif self.y - speed > target_y:
            self.y -= speed
        else:
            self.y = target_y

    def translate(self):
        peachy.graphics.translate(self.x, self.y)


class Input(object):

    curr_key_state = []
    prev_key_state = []

    @staticmethod
    def init():
        Input.curr_key_state = pygame.key.get_pressed()
        Input.prev_key_state = pygame.key.get_pressed()

    @staticmethod
    def down(key):
        code = Input.get_key_code(key)
        if code != -1:
            return Input.curr_key_state[code]
        return False

    @staticmethod
    def pressed(key):
        if key == 'any':
            for code in xrange(len(Input.curr_key_state)):
                if Input.curr_key_state[code] and not Input.prev_key_state[code]:
                    return True
            return False
        else:
            code = Input.get_key_code(key)
            if code != -1:
                return Input.curr_key_state[code] and not Input.prev_key_state[code]
            return False
    
    @staticmethod
    def released(key):
        code = Input.get_key_code(key)
        if code != -1:
            return not Input.curr_key_state[code] and Input.prev_key_state[code]
        return False

    @staticmethod
    def poll_keyboard():
        Input.prev_key_state = Input.curr_key_state
        Input.curr_key_state = pygame.key.get_pressed()
    
    @staticmethod
    def get_key_code(key):
        if key == 'enter': 
            return K_RETURN
        elif key == 'escape': 
            return K_ESCAPE
        elif key == 'lshift': 
            return K_LSHIFT
        elif key == 'rshift': 
            return K_RSHIFT
        elif key == 'space': 
            return K_SPACE
        elif key == 'left': 
            return K_LEFT
        elif key == 'right': 
            return K_RIGHT
        elif key == 'up': 
            return K_UP
        elif key == 'down': 
            return K_DOWN

        elif key == '1':
            return K_1;
        elif key == '2':
            return K_2;
        elif key == '3':
            return K_3;
        elif key == '4':
            return K_4;
        elif key == '5':
            return K_5;
        elif key == '6':
            return K_6;
        elif key == '7':
            return K_7;
        elif key == '8':
            return K_8;
        elif key == '9':
            return K_9;
        elif key == '0':
            return K_0;

        elif key == 'F1':
            return K_F1;
        elif key == 'F2':
            return K_F2;
        elif key == 'F3':
            return K_F3;
        elif key == 'F4':
            return K_F4;
        elif key == 'F5':
            return K_F5;
        elif key == 'F6':
            return K_F6;
        elif key == 'F7':
            return K_F7;
        elif key == 'F8':
            return K_F8;
        elif key == 'F9':
            return K_F9;
        elif key == 'F10':
            return K_F10;
        elif key == 'F11':
            return K_F11;
        elif key == 'F12':
            return K_F12;

        elif key == 'a':
            return K_a
        elif key == 'b':
            return K_b
        elif key == 'c':
            return K_c
        elif key == 'd':
            return K_d
        elif key == 'e':
            return K_e
        elif key == 'f':
            return K_f
        elif key == 'g':
            return K_g
        elif key == 'h':
            return K_h
        elif key == 'i':
            return K_i
        elif key == 'j':
            return K_j
        elif key == 'k':
            return K_k
        elif key == 'l':
            return K_l
        elif key == 'm':
            return K_m
        elif key == 'n':
            return K_n
        elif key == 'o':
            return K_o
        elif key == 'p':
            return K_p
        elif key == 'q':
            return K_q
        elif key == 'r':
            return K_r
        elif key == 's':
            return K_s
        elif key == 't':
            return K_t
        elif key == 'u':
            return K_u
        elif key == 'v':
            return K_v
        elif key == 'w':
            return K_w
        elif key == 'x':
            return K_x
        elif key == 'y':
            return K_y
        elif key == 'z':
            return K_z
        else:
            return -1


class SoundEffect(object):

    def __init__(self, sound):
        self.sound = sound
        self.channel = None

    def play(self):
        if self.channel:
            if self.channel.get_sound() == self.sound:
                self.channel.stop()
        self.channel = self.sound.play()

    def playing(self):
        if self.channel:
            if self.channel.get_sound() == self.sound:
                return self.channel.get_busy()
        else:
            return False

    def stop(self):
        if self.channel:
            if self.channel.get_sound() == self.sound:
                self.channel.stop()
                self.channel = None


class Stage(object):

    def __init__(self):
        self.width = 0
        self.height = 0
        self.tile_width = 0
        self.tile_height = 0

        # TODO make layers in dict where layer_name is key
        self.layers = []
        self.objects = []
        self.tilesets = []
        self.tileset_images = []

        self.properties = {}

        self.path = ''
        self.name = ''  # optional

    def clear(self):
        del self.layers[:]
        del self.tilesets[:]
        del self.tileset_images[:]
        del self.objects[:]
        self.properties.clear()

    @staticmethod
    def load_tiled(path):
        xml = open_xml(path)
        if xml is None:
            raise IOError('stage "{0}" not found'.format(path))
        
        stage_raw = xml.getElementsByTagName('map')[0]

        asset_path = os.path.dirname(path)

        # Load base attributes
        stage = Stage()

        stage.tile_width = int(stage_raw.getAttribute('tilewidth'))
        stage.tile_height = int(stage_raw.getAttribute('tileheight'))
        stage.width = int(stage_raw.getAttribute('width')) * stage.tile_width
        stage.height = int(stage_raw.getAttribute('height')) * stage.tile_height
        stage.path = path

        map_properties = xml.getElementsByTagName('properties')
        try:
            for prop in map_properties[0].getElementsByTagName('property'):
                property_name = prop.getAttribute('name')
                property_value = prop.getAttribute('value')
                stage.properties[property_name] = property_value
        except IndexError:
            pass

        # Load tilesets
        for tileset_raw in stage_raw.getElementsByTagName('tileset'):
            tileset = stage._Tileset()
            tileset.firstGID = int(tileset_raw.getAttribute('firstgid'))

            # Parse .TSX
            tsx_source = tileset_raw.getAttribute('source')
            if tsx_source:
                tsx_xml = open_xml(os.path.join(asset_path, tsx_source))
                if tsx_xml is None:
                    raise IOError("[ERROR] Could not load tileset: {0}".format(tsx_source))
                else:
                    tileset_raw = tsx_xml.getElementsByTagName('tileset')[0]
            
            tileset.name = tileset_raw.getAttribute('name')
            tileset.tilewidth = int(tileset_raw.getAttribute('tilewidth'))
            tileset.tileheight = int(tileset_raw.getAttribute('tileheight'))

            try:
                tileset.image = peachy.fs.get_image(tileset.name)
            except IOError:
                image_raw = tileset_raw.getElementsByTagName('image')[0]
                source = image_raw.getAttribute('source')
                source_path = os.path.abspath(os.path.join(asset_path, source))
                
                tileset.image = peachy.fs.load_image(tileset.name, source_path)

            stage.tileset_images += peachy.graphics.splice(tileset.image,
                                                tileset.tilewidth,
                                                tileset.tileheight)

            properties = tileset_raw.getElementsByTagName('property')
            for prop in properties:
                property_name = prop.getAttribute('name')
                property_value = prop.getAttribute('value')
                tileset.properties[property_name] = property_value

            stage.tilesets.append(tileset)

        # Load layers and tiles

        for layer_raw in stage_raw.getElementsByTagName('layer'):

            layer = stage._Layer()
            layer.name = layer_raw.getAttribute('name')
            layer.width = int(layer_raw.getAttribute('width')) * stage.tile_width
            layer.height = int(layer_raw.getAttribute('height')) * stage.tile_height

            tile_x = 0
            tile_y = 0

            for tile_raw in layer_raw.getElementsByTagName('tile'):
                tile_id = int(tile_raw.getAttribute('gid'))

                if tile_id > 0:
                    tile = stage._Tile()
                    tile.x = tile_x
                    tile.y = tile_y
                    tile.gid = tile_id
                    layer.tiles.append(tile)

                tile_x += stage.tile_width
                if tile_x == layer.width:
                    tile_x = 0
                    tile_y += stage.tile_height

            properties = layer_raw.getElementsByTagName('property')
            for prop in properties:
                property_name = prop.getAttribute('name')
                property_value = prop.getAttribute('value')
                layer.properties[property_name] = property_value

            stage.layers.append(layer)

        # Load objects

        for object_group in stage_raw.getElementsByTagName('objectgroup'):

            group = object_group.getAttribute('name')

            for object_raw in object_group.getElementsByTagName('object'):

                obj = stage._Object()
                obj.group = group
                obj.name = object_raw.getAttribute('name')
                obj.type = object_raw.getAttribute('type')
                obj.x = int(object_raw.getAttribute('x'))
                obj.y = int(object_raw.getAttribute('y'))

                try:
                    obj.w = int(object_raw.getAttribute('width'))
                except ValueError:
                    obj.w = 0

                try:
                    obj.h = int(object_raw.getAttribute('height'))
                except ValueError:
                    obj.h = 0

                polygon = object_raw.getElementsByTagName('polygon')
                polyline = object_raw.getElementsByTagName('polyline')
                if polygon:
                    obj.is_polygon = True
                    obj.polygon_points = stage.parse_tiled_polygon(polygon)
                elif polyline:
                    obj.is_polygon = True
                    obj.polygon_points = stage.parse_tiled_polygon(polyline)

                properties = object_raw.getElementsByTagName('property')
                for prop in properties:
                    property_name = prop.getAttribute('name')
                    property_value = prop.getAttribute('value')
                    obj.properties[property_name] = property_value

                stage.objects.append(obj)

        return stage

    def parse_tiled_polygon(stage, polygon):
        points = []
        points_raw = polygon[0].getAttribute('points').split()
        for raw_point in points_raw:
            raw_point = raw_point.split(',')
            p = Point(int(raw_point[0]), int(raw_point[1]))
            points.append(p)
            # points.append(map(int, raw_point.split(',')))
        return points

    def render(self):
        """
        Render all layers, front to back
        """
        for layer in self.layers:
            render_layer(layer)

    def render_layer(self, layer, name=None):
        """
        Render a single layer by providing a reference to the layer or 
        alternatively a name
        """

        if name:
            for lay in self.layers:
                if lay.name == name:
                    layer = lay
                    break

        try:
            for tile in layer.tiles:
                peachy.graphics.draw(self.tileset_images[tile.gid - 1], 
                    tile.x, tile.y)
        except AttributeError:
            DEBUG('[ERROR] Layer could not be rendered ' + layer)


    class _Layer(object):
        def __init__(self):
            self.name = ''
            self.width = 0
            self.height = 0
            self.tiles = []
            self.properties = {}

        def __repr__(self):
            return "<Tiled Layer> " + self.name

    class _Object(object):
        def __init__(self):
            self.group = ''
            self.name = ''
            self.x = 0
            self.y = 0
            self.w = 0
            self.h = 0
            self.is_polygon = False
            self.polygon_points = []
            self.properties = {}

    class _Tile(object):
        def __init__(self):
            self.x = 0
            self.y = 0
            self.gid = 0

    class _Tileset(object):
        def __init__(self):
            self.name = ''
            self.firstgid = 0
            self.tilewidth = 0
            self.tileheight = 0
            self.properties = {}

    ''' 
    * Not sure if this function is required.     *
    * Temporarily commented out pending removal. *
    
    @staticmethod
    def _load_tileset(stage, tileset_raw):
        tileset = stage._Tileset()

        tileset.name = tileset_raw.getAttribute('name')
        tileset.firstGID = int(tileset_raw.getAttribute('firstgid'))
        tileset.tilewidth = int(tileset_raw.getAttribute('tilewidth'))
        tileset.tileheight = int(tileset_raw.getAttribute('tileheight'))

        try:
            tileset.image = peachy.graphics.get_image(tileset.name)
        except IOError:
            image_raw = tileset_raw.getElementsByTagName('image')[0]
            source = image_raw.getAttribute('source')
            source_path = os.path.abspath(os.path.join(asset_path, source))

            tileset.image = peachy.graphics._load_image(tileset.name, source_path)

        stage.tileset_images += splice_image(tileset.image,
                                            tileset.tilewidth,
                                            tileset.tileheight)

        properties = tileset_raw.getElementsByTagName('property')
        for prop in properties:
            property_name = prop.getAttribute('name')
            property_value = prop.getAttribute('value')
            tileset.properties[property_name] = property_value

        stage.tilesets.append(tileset)
        return
    '''

class StagePathfindingGrid(object):

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.obstructions = []

    def in_bounds(self, location):
        x, y = location
        if 0 <= x < self.width and 0 <= y < self.width:
            return True
        return False

    def cost(self, location, destination):
        x1, y1 = location
        x2, y2 = destination

        if (x1 - x2) == 0 or (y1 - y2) == 0:
            return 1
        else:
            return 1.5

    def passable(self, location):
        return location not in self.obstructions

    def neighbours_dep(self, location):
        x, y = location
        results = [(x, y + 1), (x, y - 1), (x + 1, y), (x - 1, y)]
        results = filter(self.in_bounds, results)
        results = filter(self.passable, results)
        return results

    def neighbours(self, location):
        x, y = location
        results = []

        for translation in [(0, 1), (0, -1), (1, 0), (1, 1), (1, -1), (-1, 0), (-1, 1), (-1, -1)]:

            trans_x, trans_y = translation
            destination = (x + trans_x, y + trans_y)

            if self.passable(destination):

                if trans_x != 0 and trans_y != 0:
                    border_one = (x + trans_x, y)
                    border_two = (x, y + trans_y)
                    if self.passable(border_one) and self.passable(border_two):
                        results.append(destination)
                else:
                    results.append(destination)

        results = filter(self.in_bounds, results)
        return results
