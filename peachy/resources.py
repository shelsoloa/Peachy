"""Peachy Resource Management
"""
import enum
import json
import logging
import os
import peachy.fs


class ResourceType(enum.Enum):
    IMAGE = 0
    SOUND = 1
    FONT = 2


class ResourceManager(object):
    def __init__(self):
        self.outline = None
        self.resources = dict()
        self.bundles = []

    def __contains__(self, resource):
        if isinstance(resource, Resource):
            for _, res in self.resources.items():
                if res == resource:
                    return True
        else:
            for _, res in self.resources.items():
                if res.name == resource or res.path == resource:
                    return True
        return False

    def __len__(self):
        return len(self.resources)

    def activate_bundle(self, bundle_name):
        bundle = self.outline.bundles.get(bundle_name)
        for resource_name in bundle.resources:
            res = self.outline.resources.get(resource_name)
            self.load_resource(res.name, res.path, res.resource_type)
        self.bundles.append(bundle)

    def deactivate_bundle(self, bundle_name):
        bundle = self.outline.bundles.get(bundle_name)
        for resource_name in bundle.resources:
            self.remove_resource_by_name(resource_name)
        self.bundles.remove(bundle)

    def add_resource(self, resource):
        if resource.name in self.resources:
            logging.log('[WARN] Overwriting resource %s' % resource.name)
        self.resources[resource.name] = resource
        return self.resources[resource.name]

    def bind_outline(self, outline_path):
        self.outline = ResourceOutline.process(outline_path)

    def clear(self):
        self.outline = None
        self.resources.clear()
        self.bundles.clear()

    def get_group(self, group_name):
        results = []
        for _, resource in self.resources.items():
            if resource.member_of(group_name):
                results.append(resource)
        return results

    def get_resource(self, res_tag):
        """Get a resource by tag (name or path)."""
        resource = self.get_resource_by_name(res_tag)
        if resource is None:
            resource = self.get_resource_by_path(res_tag)
        return resource

    def get_resource_by_name(self, res_name):
        return self.resources.get(res_name)

    def get_resource_by_path(self, res_path):
        for _, resource in self.resources.items():
            if resource.path == res_path:
                return resource
        return None

    def load_resource(self, res_name, res_path, res_type):
        """Load a resource from the filesystem and save into manager"""
        resource_data = None
        if res_type == ResourceType.IMAGE:
            resource_data = peachy.fs.load_image(res_path)
        elif res_type == ResourceType.FONT:
            resource_data = peachy.fs.load_font(res_path)
        elif res_type == ResourceType.SOUND:
            resource_data = peachy.fs.load_sound(res_path)

        if resource_data is not None:
            resource = Resource(res_name, resource_data, res_path)
            return self.add_resource(resource)
        else:
            logging.warning(
                'Invalid resource provided to ResourceManager.load_resource\n' +
                '\t{0}\n\t{1}\n\t{2}'.format(res_name, res_path, res_type))

    def remove_group(self, group_name):
        # TODO better algorithm for this
        remove_keys = []
        for k, resource in self.resources.items():
            if resource.member_of(group_name):
                remove_keys.append(k)
        for k in remove_keys:
            del self.resources[k]

    def remove_resource(self, res_tag):
        """Remove a resource by tag (name or path)."""
        removed = self.resources.pop(res_tag, None)
        if removed is None:
            removed = self.remove_resource_by_path(res_tag)
        return removed

    def remove_resource_by_name(self, res_name):
        return self.resources.pop(res_name, None)

    def remove_resource_by_path(self, res_path):
        for res_key, resource in self.resources.items():
            if resource.path == res_path:
                return self.resources.pop(res_path)
        return None


class ResourceBundle(object):
    def __init__(self, bundle_name, resource_names):
        self.name = bundle_name
        self.resources = resource_names


class Resource(object):
    def __init__(self, name, data, path=''):
        self.name = name
        self.data = data
        self.path = path
        self.group = ''

    @property
    def group(self):
        return self.__group

    @group.setter
    def group(self, group_string):
        self.__group = group_string.split()

    def member_of(self, group):
        return group in self.__group


class ResourceOutline(object):
    def __init__(self, resources=None, bundles=None):
        if resources is not None:
            self.resources = resources
        else:
            self.resources = {}

        if bundles is not None:
            self. bundles = bundles
        else:
            self.bundles = {}

    @staticmethod
    def process(outline_path):
        outline_raw = ''
        with open(outline_path, 'r') as resource_outline:
            outline_raw = json.load(resource_outline)

        resource_directory = outline_raw.get('directory')
        if resource_directory is None:
            resource_directory = os.path.dirname(outline_path)

        # convert resources
        resources = {}
        resource_nodes = outline_raw.get('resources')
        for resource_node in resource_nodes:
            res_type = resource_node['type']
            if res_type == 'image':
                res_type = ResourceType.IMAGE
            elif res_type == 'font':
                res_type = ResourceType.FONT
            elif res_type == 'sound':
                res_type = ResourceType.SOUND

            res_path = os.path.join(resource_directory, resource_node['path'])

            resource = ResourceOutline_Resource(
                res_type, resource_node['name'], res_path)
            resources[resource.name] = resource

        # convert bundles
        bundles = {}
        bundle_nodes = outline_raw.get('bundles', [])
        for bundle_node in bundle_nodes:
            bundle_name = bundle_node['name']

            bundle_resources = []
            bundle_resource_nodes = bundle_node.get('resources', [])
            for bundle_resource in bundle_resource_nodes:
                print(bundle_resource)
                if bundle_resource in resources:
                    bundle_resources.append(bundle_resource)
                else:
                    logging.warning(
                        'Attempt to add unregistered resource to bundle.')

            bundles[bundle_name] = ResourceBundle(bundle_name, bundle_resources)

        # finalize
        return ResourceOutline(resources, bundles)


class ResourceOutline_Resource(object):
    def __init__(self, restype, name, path, **additional_args):
        self.resource_type = restype
        self.name = name
        self.path = path
        self.additional = additional_args
