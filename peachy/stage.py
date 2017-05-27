"""Peachy Stages
    peachy.stage

Modules for loading and handling stages. Uses pytmx for tiled stages and a
generic StageData model for custom loaders.
"""

import logging
import peachy
import pytmx


def load_tiled_tmx(path):
    """Load a tiled TMX file.

    Loads a tiled TMX map using pytmx, and returns a pytmx.TiledMap. Also:
    appends layer_type(str) to pytmx layers, to make parsing simpler.

    Args:
        path (str): Absolute path to the tiled TMX resource.

    Returns:
        pytmx.TiledMap: A reference to the loaded tiled map.

    Todo:
        Custom image loading that utilizes peachy.fs.load_image.
    """
    tiled_map = pytmx.util_pygame.load_pygame(
        peachy.fs.use_resource_directory(path))

    for layer in tiled_map.layers:
        if isinstance(layer, pytmx.TiledTileLayer):
            layer.layer_type = 'tile'
        elif isinstance(layer, pytmx.TiledObjectGroup):
            layer.layer_type = 'object group'
        elif isinstance(layer, pytmx.TiledImageLayer):
            layer.layer_type = 'image'

    return tiled_map


def render_tiled_map(stage):
    """Convenience function for rendering all layers in a tiled map.

    Args:
        stage(pytmx.TiledMap): A stage file
    """
    for layer in stage.layers:
        if isinstance(layer, pytmx.TiledTileLayer):
            render_tiled_layer(layer)


def render_tiled_layer(stage, layer):
    """Render a single layer by providing reference or layer name.

    Args:
        stage(pytmx.TiledMap, StageData): A stage object, pytmx or StageData.
        layer(pytmx.TiledTileLayer, StageLayer, str): A stage layer object,
            pytmx or StageLayer. Can also specify a string name and this
            function will find the layer with said name.

    Todo:
        Tile animations.
    """

    if type(layer) == str:
        if isinstance(stage, pytmx.TiledMap):
            layer = stage.get_layer_by_name(layer)
        elif isinstance(stage, StageData):
            layer = next((l for l in stage.layers if l.name == layer), None)
        else:
            layer = None

    try:
        for x, y, image in layer.tiles():
            if image:
                peachy.graphics.draw(image, x * stage.tilewidth,
                                     y * stage.tileheight)
    except AttributeError:
        logging.warning('Layer could not be rendered ' + layer)


class StageData(object):
    def __init__(self):
        self.name = ''

        self.width = 0
        self.height = 0
        self.tile_width = 0
        self.tile_height = 0

        # RGB or HEX
        self.background_color = ''

        self.layers = []  # Cannot be dict, layers must remain in order
        self.tilesets = []
        self.tileset_images = []

        self.path = ''

    def clear(self):
        """Clear the stage of all data."""
        del self.layers[:]
        del self.tilesets[:]
        del self.tileset_images[:]

    class StageLayer(object):
        """StageData Layer

        Attributes:
            name (str): Name of the layer
            tiles (list[StageData.StageTile]): A list containing all the tiles
                that belong to this stage.
        """
        def __init__(self):
            self.name = ''
            self.tiles = []

        def __repr__(self):
            return "<Stage Layer> " + self.name

    class StageTile(object):
        """StageData Tile

        Attributes:
            x (int): The x-coordinate of this tile (in tiles)
            y (int): The y-coordinate of this tile (in tiles)
            gid (int): The global ID of this tile (related to its place among
                all tiles spanning all loaded tilesets).
        """
        def __init__(self):
            self.x = 0
            self.y = 0
            self.gid = 0

    class StageTileset(object):
        """StageData Tileset Reference

        Tilesets are loaded to resources. This class keeps a reference to
        a specific stages representation of a Tileset.

        Attributes:
            name (str): The name of the tileset (USED AS REFERENCE TO RESOURCE)
            firstgid (int): The starting global ID for this tileset.
            tilewidth (int): The width of an individual tile.
            tileheight (int): The height of an individual tile.
        """
        def __init__(self):
            self.name = ''
            self.firstgid = 0
            self.tilewidth = 0
            self.tileheight = 0
