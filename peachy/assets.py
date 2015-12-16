import pygame

class Assets(object):
    """
    An asset management helper class
    """

    assets_path = ''
    stored_fonts = dict()
    stored_images = dict()
    stored_sounds = dict()

    def get_font(asset_name):
        return stored_fonts.get(asset_name)

    def get_image(asset_name):
        return stored_images.get(asset_name)

    def get_sound(asset_name):
        return stored_sounds.get(asset_name)

    def store_font(asset_name, path, point_size):
        """Retrieves a font from the HDD"""

        path = path.lstrip('../')  # cannot rise outside of asset_path

        try:
            font = pygame.font.Font(os.path.join(AssetManager.assets_path, path), point_size)
            AssetManager.stored_fonts[asset_name] = font
            return font
        except IOError:
            # TODO incorporate default font
            print '[ERROR] could not find Font: ' + path
            pc.quit()

    def store_image(asset_name, path):
        """Retrieves an image from the HDD"""

        path = path.lstrip('../')  # cannot rise outside of asset_path

        try:
            image = pygame.image.load(os.path.join(AssetManager.assets_path, path))
            image.convert_alpha()
            AssetManager.stored_images[asset_name] = image
            return image
        except IOError:
            print '[ERROR] could not find Image: ' + path
            pc.quit()

    def store_sound(asset_name, path):
        """Retrieves a sound file from the HDD"""
        # TODO add linux support

        path = path.lstrip('../')  # cannot rise outside of asset_path

        try:
            sound = pygame.mixer.Sound(os.path.join(AssetManager.assets_path, path))
            AssetManager.stored_sounds[asset_name] = sound
            return sound
        except IOError:
            print '[ERROR] could not find Sound: ' + path
            sound = pygame.mixer.Sound()
            AssetManager.stored_sounds[asset_name] = sound
            return sound


