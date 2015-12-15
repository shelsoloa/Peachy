import heapq
import os
import pickle
import pygame
import core
import xml.dom.minidom
from peachy import AssetManager, graphics


def a_star_search(grid, start, goal):
    frontier = PriorityQueue()
    frontier.put(start, 0)
    came_from = {}
    cost_so_far = {}
    came_from[start] = None
    cost_so_far[start] = 0

    while not frontier.empty():
        current = frontier.get()

        if current == goal:
            break

        for neighbour in grid.neighbours(current):
            new_cost = cost_so_far[current] + grid.cost(current, neighbour)
            if neighbour not in cost_so_far or new_cost < cost_so_far[neighbour]:
                cost_so_far[neighbour] = new_cost
                priority = new_cost + a_star_heuristic(goal, neighbour)
                frontier.put(neighbour, priority)
                came_from[neighbour] = current

    # return came_from, cost_so_far
    current = goal
    path = [current]
    while current != start:
        current = came_from[current]
        path.append(current)
    path.reverse()
    return path


def a_star_heuristic(a, b):
    x1, y1 = a
    x2, y2 = b
    return abs(x1 - x2) + abs(y1 - y2)


def save(data, file_name):
    _file = None
    try:
        _file = open(file_name, 'wb')
        pickle.dump(data, _file)
        _file.close()
    except (IOError, pickle.PickleError):
        if _file is not None:
            _file.close()
        raise


def load(file_name):
    _file = None
    saved_data = None
    try:
        _file = open(file_name, 'rb')
        saved_data = pickle.load(_file)
        _file.close()
    except (IOError, pickle.PickleError):
        if _file is not None:
            _file.close()
        raise
    return saved_data


def splice_image(image, frame_width, frame_height, margin_x=0, margin_y=0):
    x = 0
    y = 0

    sub_images = []

    src_width, src_height = image.get_size()

    while x + frame_width <= src_width and y + frame_height <= src_height:
        crop = pygame.Surface((frame_width, frame_height), flags=pygame.SRCALPHA)
        crop.blit(image, (0, 0), (x, y, frame_width, frame_height))

        sub_images.append(crop)

        x += frame_width + margin_x
        if x + frame_width > src_width:
            x = 0
            y += frame_height + margin_y

    return sub_images


def hex_to_rgb(val):
    # (#ffffff) -> (255, 255, 255)
    val = val.lstrip('#')
    lv = len(val)
    # Hell if I know how this works...
    return tuple(int(val[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))


def open_xml(path):
    try:
        xml_file = open(os.path.join(AssetManager.assets_path, path), 'r')
        data = xml_file.read()
        xml_file.close()
        return xml.dom.minidom.parseString(data)
    except IOError:
        print '[ERROR] could not load xml file: ' + path


class Camera(object):
    
    def __init__(self, view_width, view_height, smoothing_enabled=False, speed=1):
        self.x = 0
        self.y = 0

        self.view_width = view_width
        self.view_height = view_height
        self.max_width = -1
        self.max_height = -1
        self.bounds_width = view_width

        self.destination_x = 0
        self.destination_y = 0

        self.smoothing_enabled = smoothing_enabled
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
        graphics.translate(self.x, self.y)


class Music(object):

    def __init__(self, source):
        self.source = source
        self.loaded = False
        self.paused = False
        self.playing = False

    def load(self):
        pygame.mixer.music.load(self.source)
        self.loaded = True
        self.paused = False
        self.playing = False

    def pause(self):
        if not self.loaded:
            return
        pygame.mixer.music.pause()
        self.paused = True
        self.playing = False

    def play(self):
        if not self.loaded:
            return
        pygame.mixer.music.play()
        self.paused = False
        self.playing = True

    def resume(self):
        if not self.loaded:
            return
        pygame.mixer.music.unpause()
        self.paused = False
        self.playing = True

    def stop(self):
        if not self.loaded:
            return
        pygame.mixer.music.stop()
        self.paused = False
        self.playing = False


class PriorityQueue(object):
    # TODO ... This has something to do with A* but I don't know what. I want to remove it.
    
    def __init__(self):
        self.elements = []

    def empty(self):
        return len(self.elements) == 0

    def put(self, item, priority):
        heapq.heappush(self.elements, (priority, item))

    def get(self):
        return heapq.heappop(self.elements)[1]


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

    def clear(self):
        del self.layers[:]
        del self.tilesets[:]
        del self.tileset_images[:]
        del self.objects[:]
        self.properties.clear()

    def load_tiled(self, path):
        xml = open_xml(path)
        stage_raw = xml.getElementsByTagName('map')[0]

        # Load base attributes

        self.tile_width = int(stage_raw.getAttribute('tilewidth'))
        self.tile_height = int(stage_raw.getAttribute('tileheight'))
        self.width = int(stage_raw.getAttribute('width')) * self.tile_width
        self.height = int(stage_raw.getAttribute('height')) * self.tile_height
        self.path = path

        map_properties = xml.getElementsByTagName('properties')
        if map_properties:
            for prop in map_properties[0].getElementsByTagName('property'):
                property_name = prop.getAttribute('name')
                property_value = prop.getAttribute('value')
                self.properties[property_name] = property_value

        # Load tilesets

        for tileset_raw in stage_raw.getElementsByTagName('tileset'):

            tileset = self._Tileset()
            tileset.name = tileset_raw.getAttribute('name')
            tileset.firstGID = int(tileset_raw.getAttribute('firstgid'))
            tileset.tilewidth = int(tileset_raw.getAttribute('tilewidth'))
            tileset.tileheight = int(tileset_raw.getAttribute('tileheight'))

            tileset.image = AssetManager.get_image(tileset.name)
            if tileset.image is None:
                image_raw = tileset_raw.getElementsByTagName('image')[0]
                source = image_raw.getAttribute('source')
                tileset.image = AssetManager.load_image(tileset.name, source)

            self.tileset_images += splice_image(tileset.image,
                                                tileset.tilewidth,
                                                tileset.tileheight)

            properties = tileset_raw.getElementsByTagName('property')
            for prop in properties:
                property_name = prop.getAttribute('name')
                property_value = prop.getAttribute('value')
                tileset.properties[property_name] = property_value

            self.tilesets.append(tileset)

        # Load layers and tiles

        for layer_raw in stage_raw.getElementsByTagName('layer'):

            layer = self._Layer()
            layer.name = layer_raw.getAttribute('name')
            layer.width = int(layer_raw.getAttribute('width')) * self.tile_width
            layer.height = int(layer_raw.getAttribute('height')) * self.tile_height

            tile_x = 0
            tile_y = 0

            for tile_raw in layer_raw.getElementsByTagName('tile'):
                tile_id = int(tile_raw.getAttribute('gid'))

                if tile_id > 0:
                    tile = self._Tile()
                    tile.x = tile_x
                    tile.y = tile_y
                    tile.gid = tile_id
                    layer.tiles.append(tile)

                tile_x += self.tile_width
                if tile_x == layer.width:
                    tile_x = 0
                    tile_y += self.tile_height

            properties = layer_raw.getElementsByTagName('property')
            for prop in properties:
                property_name = prop.getAttribute('name')
                property_value = prop.getAttribute('value')
                layer.properties[property_name] = property_value

            self.layers.append(layer)

        # Load objects

        for object_group in stage_raw.getElementsByTagName('objectgroup'):

            group = object_group.getAttribute('name')

            for object_raw in object_group.getElementsByTagName('object'):

                obj = self._Object()
                obj.group = group
                obj.name = object_raw.getAttribute('name')
                obj.x = int(object_raw.getAttribute('x'))
                obj.y = int(object_raw.getAttribute('y'))

                polygon = object_raw.getElementsByTagName('polygon')
                polyline = object_raw.getElementsByTagName('polyline')
                if polygon:
                    obj.is_polygon = True
                    obj.polygon_points = self.parse_tiled_polygon(polygon)
                elif polyline:
                    obj.is_polygon = True
                    obj.polygon_points = self.parse_tiled_polygon(polyline)
                else:
                    try:
                        obj.w = int(object_raw.getAttribute('width'))
                        obj.h = int(object_raw.getAttribute('height'))
                    except ValueError:
                        obj.w = 0
                        obj.h = 0


                properties = object_raw.getElementsByTagName('property')
                for prop in properties:
                    property_name = prop.getAttribute('name')
                    property_value = prop.getAttribute('value')
                    obj.properties[property_name] = property_value

                self.objects.append(obj)

    def parse_tiled_polygon(self, polygon):
        points = []
        points_raw = polygon[0].getAttribute('points').split()
        for raw_point in points_raw:
            points.append(map(int, raw_point.split(',')))
        return points

    # TODO improve map render performance
    #
    # Modify tiles to directly reference their image instead of holding a gid.
    # Don't try to draw every image

    def render(self):
        for layer in self.layers:
            for tile in layer.tiles:
                tile_image = self.tileset_images[tile.gid]
                graphics.draw_image(tile_image, tile.x, tile.y)

    def render_layer(self, layer):
        for tile in layer.tiles:
            tile_image = self.tileset_images[tile.gid - 1]
            graphics.draw_image(tile_image, tile.x, tile.y)

    def render_layer_name(self, layer_name):
        for layer in self.layers:
            if layer.name == layer_name:
                self.render_layer(layer)
                break

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
