"""An alternative method for loading tiled maps that does not use PyTMX.
Does not support all tiled functionality and is currently unmaintained.
"""

import os
import peachy
from peachy.stage import StageData, StageLayer, StageTileset, StageTile


def load_tiled_tmx(filename):
    """Load a Tiled TMX map

    Creates a StageData object from a tiled .tmx file.

    Args:
        path (str): Absolute path to a valid tiled TMX file.

    Returns:
        peachy.stage.StageData: a populated StageData object.

    Raises:
        IOError: File was not found.
    """

    root_xml = peachy.fs.open_xml(filename)
    if root_xml is None:
        raise IOError('stage "{0}" not found'.format(filename))

    stage_node = root_xml.getElementsByTagName('map')[0]
    asset_path = os.path.dirname(filename)
    stage = TiledStageData()

    # TODO validate version
    # version = stage_node.getAttribute('version')

    # Load base attributes
    stage.filename = filename
    stage.orientation = stage_node.getAttribute('orientation')
    stage.renderorder = stage_node.getAttribute('renderorder')

    stage.width = int(stage_node.getAttribute('width')) * stage.tile_width
    stage.height = int(stage_node.getAttribute('height')) * stage.tile_height
    stage.tile_width = int(stage_node.getAttribute('tilewidth'))
    stage.tile_height = int(stage_node.getAttribute('tileheight'))

    # Load stage properties
    stage.properties = parse_properties(stage_node)

    # Load tilesets
    for tileset_node in stage_node.getElementsByTagName('tileset'):
        tileset = TiledTileset()

        # We parse GID before loading TSX because it is map specific.
        tileset.first_GID = int(tileset_node.getAttribute('firstgid'))

        # Retrieve tileset info from TSX if provided
        tsx_source = tileset_node.getAttribute('source')
        if tsx_source:
            tsx_xml = peachy.fs.open_xml(os.path.join(asset_path, tsx_source))
            if tsx_xml is None:
                raise IOError("[ERROR] Could not load tileset: " + tsx_source)
            else:
                tileset_node = tsx_xml.getElementsByTagName('tileset')[0]

        # Parse basic tileset info
        tileset.name = tileset_node.getAttribute('name')
        tileset.tilewidth = int(tileset_node.getAttribute('tilewidth'))
        tileset.tileheight = int(tileset_node.getAttribute('tileheight'))

        try:
            tileset.spacing = int(tileset_node.getAttribute('spacing'))
        except ValueError:
            pass
        try:
            tileset.margin = int(tileset_node.getAttribute('margin'))
        except ValueError:
            pass
        try:
            tileset.tilecount = int(tileset_node.getAttribute('tilecount'))
        except ValueError:
            pass
        try:
            tileset.columns = int(tileset_node.getAttribute('columns'))
        except ValueError:
            pass

        # Load and save the tileset image file. First attempts to load from
        # resources using tileset.name as key. Loads from source if not in
        # resources.
        # TODO optional saving
        try:
            tileset.image = peachy.fs.get_image(tileset.name)
        except IOError:
            image_node = tileset_node.getElementsByTagName('image')[0]

            image_source = image_node.getAttribute('source')
            image_path = os.path.abspath(os.path.join(asset_path, image_source))
            # TODO check format (png, gif, jpg, bmp, etc.)
            # image_format = image_node.getAttribute('format')
            # TODO check transparent color.
            # image_transparent_color = image_node.getAttribute('trans')

            tileset.image = peachy.fs.load_image(tileset.name, image_path)

        # Cut each tile in the tileset into individual images that are saved to
        # stage.tileset_images
        # TODO save to tileset.spliced_tiles
        tileset.images = peachy.graphics.splice(
            tileset.image, tileset.tile_width, tileset.tile_height)
        stage.tileset_images += tileset.images

        # Load tileset tile offset
        tileset_offset_node = tileset_node.getElementsByTagName('tileoffset')
        if tileset_offset_node:
            tileset_offset_node = tileset_offset_node[0]
            tileset.tile_offset_x = tileset_offset_node.getAttribute('x')
            tileset.tile_offset_y = tileset_offset_node.getAttribute('y')

        # Load tileset terraintypes
        # TODO theres a good chance I did this wrong.
        terrain_types_node = tileset_node.getElementsByTagName('terrain')
        for terrain_node in terrain_types_node:
            terrain_name = terrain_node.getAttribute('name')
            terrain_tile = terrain_node.getAttribute('tile')
            tileset.terrain_types.append((terrain_name, terrain_tile))

        # Load tileset properties
        tileset.properties = parse_properties(tileset_node)

        # Load tileset tile data
        # TODO bind each tile to their image as well.
        # tst == tileset :3
        tst_tile_nodes = tileset_node.getElementsByTagName('tile')
        for tst_tile_node in tst_tile_nodes:
            tst_tile = tileset.Tile()

            # Load tileset tile animation
            tst_tile_anim_node = tst_tile_node.getElementsByTagName('animation')
            if not tst_tile_anim_node:
                tst_tile.animated = True
                frames = tst_tile_anim_node[0].getElementsByTagName('frame')
                for frame in frames:
                    frame_tileid = frame.getAttribute('tileid')
                    frame_duration = frame.getAttribute('duration')
                    tst_tile.frames.append((frame_tileid, frame_duration))

            # Load tileset tile properties
            tst_tile.properties = parse_properties(tst_tile_node)

            # Add tileset tile data to tileset
            tileset.append(tst_tile)

        # Add tileset to TiledStageData object
        stage.tilesets.append(tileset)

    # Load tile layers
    layer_count = 0
    for layer_node in stage_node.getElementsByTagName('layer'):
        layer = TiledLayer()

        layer.name = layer_node.getAttribute('name')

        try:
            layer.tile_width = int(layer_node.getAttribute('tilewidth'))
        except ValueError:
            layer.tile_width = stage.tile_width
        try:
            layer.tile_height = int(layer_node.getAttribute('tileheight'))
        except ValueError:
            layer.tile_height = stage.tile_height

        layer.width = int(layer_node.getAttribute('width'))
        layer.height = int(layer_node.getAttribute('height'))

        layer.order = layer_count
        layer_count += 1

        layer.opacity = layer_node.getAttribute('opacity')
        if not layer.opacity:
            layer.opacity = 1
        else:
            layer.opacity = int(layer.opacity)

        layer.visible = layer_node.getAttribute('visible') == '1'

        layer.offset_x = layer_node.getAttribute('offsetx')
        if not layer.offset_x:
            layer.offset_x = 0
        else:
            layer.offset_x = int(layer.offset_x)
        layer.offset_y = layer_node.getAttribute('offsety')
        if not layer.offset_y:
            layer.offset_y = 0
        else:
            layer.offset_y = int(layer.offset_y)

        # Load tiles
        data_node = layer_node.getElementsByTagName('data')
        next_gid = None
        tile_data = None

        # Decode tile data
        encoding = data_node.getAttribute('encoding')
        if encoding == 'base64':
            from base64 import b64decode
            tile_data = b64decode(data_node.text())
        elif encoding == 'csv':
            pass
            next_gid = \
                map(int,
                    "".join(line.strip() for line in data_node.text().strip()
                            ).split(",")
                    )
        elif encoding:
            peachy.DEBUG('[ERROR] TMX encoding type {0} not supported'
                         .format(encoding))

        # Decompress tile data
        compression = data_node.getAttribute('compression')
        # if compression == 'gzip':
        #     import gzip
        #     with gzip.GzipFile(fileobj=six.BytesIO(tile_data)) as fh:
        #         tile_data = fh.read()
        if compression == 'zlib':
            import zlib
            tile_data = zlib.decompress(tile_data)
        elif compression:
            peachy.DEBUG('[ERROR] TMX compression type {} not supported'
                         .format(compression))

        if encoding == next_gid is None:
            def get_children(parent):
                for tile_node in parent.getElementsByTagName('tile'):
                    yield int(tile_node.getAttribute('gid'))
            next_gid = get_children(data_node)
        elif tile_data:
            pass
            # if type(data) == bytes:
            #     fmt = struct.Struct('<L')
            #     iterator = (data[i:i + 4] for i in range(0, len(data), 4))
            #     next_gid = (fmt.unpack(i)[0] for i in iterator)
            # else:
            #     msg = 'layer data not in expected format ({})'
            #     logger.error(msg.format(type(data)))
            #     raise Exception

        print('test')

        # TODO base64
        tile_x = 0
        tile_y = 0

        for tile_id in next_gid:
            if tile_id > 0:
                tile = TiledTile()
                tile.x = tile_x
                tile.y = tile_y
                tile.id = tile_id
                layer.tiles.append(tile)

            print('in')

            tile_x += stage.tile_width
            if tile_x == layer.width:
                tile_x = 0
                tile_y += stage.tile_height

        print('test2')

        properties = layer_node.getElementsByTagName('property')
        for prop in properties:
            property_name = prop.getAttribute('name')
            property_value = prop.getAttribute('value')
            layer.properties[property_name] = property_value

        stage.layers.append(layer)

    # TODO Load image layer

    # Load objects
    for object_group in stage_node.getElementsByTagName('objectgroup'):

        group = object_group.getAttribute('name')
        # object_group = TiledObjectGroup()

        for object_node in object_group.getElementsByTagName('object'):

            obj = stage.Object()
            obj.group = group
            obj.name = object_node.getAttribute('name')
            obj.type = object_node.getAttribute('type')
            obj.x = int(object_node.getAttribute('x'))
            obj.y = int(object_node.getAttribute('y'))

            try:
                obj.w = int(object_node.getAttribute('width'))
            except ValueError:
                obj.w = 0

            try:
                obj.h = int(object_node.getAttribute('height'))
            except ValueError:
                obj.h = 0

            # parse polygon
            polygon = object_node.getElementsByTagName('polygon') or \
                object_node.getElementsByTagName('polyline')
            if polygon:
                points_node = polygon[0].getAttribute('points').split()
                for raw_point in points_node:
                    raw_point = raw_point.split(',')
                    p = peachy.geo.Point(int(raw_point[0]), int(raw_point[1]))
                    obj.polygon_points.append(p)
                obj.is_polygon = True

            # parse properties
            properties = object_node.getElementsByTagName('property')
            for prop in properties:
                property_name = prop.getAttribute('name')
                property_value = prop.getAttribute('value')
                obj.properties[property_name] = property_value

            stage.objects.append(obj)

    return stage


class TiledElement(object):
    def __init__(self):
        self.properties = {}


class TiledStageData(TiledElement, StageData):
    """ Holds raw information about the current stage """

    def __init__(self):
        TiledElement.__init__(self)
        StageData.__init__(self)

        self.orientation = ''
        self.renderorder = ''

        self.hexsidelength = 0
        self.staggeraxis = 0
        self.staggerindex = 0

    def get_layers_by_type(self, t):
        return [layer for layer in self.layers if layer.type_ == t]

    @property
    def image_layers(self):
        return self.get_layers_by_type('image')

    @property
    def object_groups(self):
        return self.get_layers_by_type('object')

    @property
    def tile_layers(self):
        return self.get_layers_by_type('tile')

    @property
    def objects(self):
        # Test if this works.
        # results = [group.objects for group in self.object_groups]

        results = []
        for group in self.object_groups:
            results += group.objects
        return results

    def clear(self):
        super().clear()
        del self.objects[:]
        self.properties.clear()


class TiledLayer(TiledElement, StageLayer):
    def __init__(self):
        TiledElement.__init__()
        StageLayer.__init__()


class TiledImageLayer(TiledLayer):
    def __init__(self):
        super().__init__()


class TiledObjectGroup(TiledElement):
    def __init__(self):
        super().__init__()
        self.objects = []


class TiledTileLayer(TiledLayer):
    def __init__(self):
        super().__init__()
        self.tiles = []
        self.tile_width = 0
        self.tile_height = 0

    @property
    def width_in_pixels(self):
        return self.width * self.tile_width

    @property
    def height_in_pixels(self):
        return self.height * self.tile_height

    def render(self):
        for tile in self.tiles:
            peachy.graphics.draw(tile.image, tile.x, tile.y)
#            peachy.graphics.draw(stage.tileset_images[tile.gid - 1],
#                                 tile.x, tile.y)


class TiledObject(TiledElement):
    def __init__(self):
        super().__init__()
        self.group = ''
        self.name = ''
        self.type = ''
        self.x = 0
        self.y = 0
        self.w = 0
        self.h = 0
        self.is_polygon = False
        self.polygon_points = []


class TiledTile(TiledElement, StageTile):
    def __init__(self):
        TiledElement.__init__(self)
        StageTile.__init__(self)


class TiledTileset(TiledElement, StageTileset):
    def __init__(self):
        TiledElement.__init__(self)
        StageTileset.__init__(self)
        self.image = None
        self.first_GID = 0
        self.terrain_types = []
        self.tile_offset_x = 0
        self.tile_offset_y = 0
        self.tile_data = {}  # Key is tiledata id


class TiledTileData(TiledElement):
    """Tileset tile data.

    Tiles can have animations and properties. TileData is held within
    it's governing tileset.
    """
    def __init__(self):
        super().__init__()
        self.local_id = 0
        self.animated = False
        self.frames = []  # list of tuples (tileid, duration)


def parse_properties(properties_root, convert_type=True):
    # Get first 'properties' root. Subsequent 'properties' roots are ignored.
    properties_node = properties_root.getElementsByTagName('properties')
    if len(properties_node) > 0:
        properties_node = properties_node[0]
    else:
        return {}   # Return empty dict if no properties exist.

    # Iterate through every 'property' node and store name and value.
    property_nodes = properties_node.getElementsByTagName('property')
    properties = {}
    for prop in property_nodes:
        property_name = prop.getAttribute('name')
        property_value = prop.getAttribute('value')

        if convert_type:
            property_type = prop.getAttribute('type')
            try:
                if property_type == 'int':
                    property_value = int(property_value)
                elif property_type == 'float':
                    property_value = float(property_value)
                elif property_type == 'bool':
                    property_value = not property_value == 'false'
                # color = '#AARRGGBB'
                # file = relative path
                # 'color' and 'file' are ignored because they are still strings.
            except ValueError:
                pass

        properties[property_name] = property_value
    return properties
