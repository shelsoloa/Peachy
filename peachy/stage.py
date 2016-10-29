import os

import peachy
from peachy.fs import open_xml


def load_tiled_tmx(path):
    """ Creates a new StageData object from a tiled .tmx file """

    xml = open_xml(path)
    if xml is None:
        raise IOError('stage "{0}" not found'.format(path))

    stage_raw = xml.getElementsByTagName('map')[0]

    asset_path = os.path.dirname(path)

    stage = StageData()

    # Load base attributes
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

        # parse .TSX
        tsx_source = tileset_raw.getAttribute('source')
        if tsx_source:
            tsx_xml = open_xml(os.path.join(asset_path, tsx_source))
            if tsx_xml is None:
                raise IOError("[ERROR] Could not load tileset: " + tsx_source)
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
    layer_count = 0
    for layer_raw in stage_raw.getElementsByTagName('layer'):

        layer = stage._Layer()
        layer.name = layer_raw.getAttribute('name')
        layer.width = int(layer_raw.getAttribute('width')) * stage.tile_width
        layer.height = int(layer_raw.getAttribute('height')) * stage.tile_height
        layer.order = layer_count
        layer_count += 1

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

            # parse polygon
            polygon = object_raw.getElementsByTagName('polygon') or \
                object_raw.getElementsByTagName('polyline')
            if polygon:
                points_raw = polygon[0].getAttribute('points').split()
                for raw_point in points_raw:
                    raw_point = raw_point.split(',')
                    p = peachy.utils.Point(int(raw_point[0]), int(raw_point[1]))
                    obj.polygon_points.append(p)
                obj.is_polygon = True

            # parse properties
            properties = object_raw.getElementsByTagName('property')
            for prop in properties:
                property_name = prop.getAttribute('name')
                property_value = prop.getAttribute('value')
                obj.properties[property_name] = property_value

            stage.objects.append(obj)

    return stage


def render_map(stage):
    """ Convenience function that render all layers """
    for layer in stage.layers:
        render_layer(layer)


def render_layer(stage, layer):
    """ Render a single layer by providing reference or layer name """

    if isinstance(layer, str):
        for x in stage.layers:
            if x.name == layer:
                layer = x
                break
        else:
            layer = None

    try:
        for tile in layer.tiles:
            peachy.graphics.draw(stage.tileset_images[tile.gid - 1],
                                 tile.x, tile.y)
    except AttributeError:
        peachy.DEBUG('[ERROR] Layer could not be rendered ' + layer)


class StageData(object):
    """ Holds raw information about the current stage """

    def __init__(self):
        self.width = 0
        self.height = 0
        self.tile_width = 0
        self.tile_height = 0

        self.layers = []  # Cannot be dict because layers must remain in order
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
            self.type = ''
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


class AStarGrid(object):
    """ Has not been updated to conform with current StageData object """

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

        for translation in [(0, 1), (0, -1), (1, 0), (1, 1),
                            (1, -1), (-1, 0), (-1, 1), (-1, -1)]:

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
