def identity(value):
    return value


CUSTOM_SETTINGS_MAPPINGS = {
    'omero.web.ome_seadragon.search.default_group': ['DEFAULT_SEARCH_GROUP', None, identity, None]
    # configure this value using OMERO.cli
    # <ome_home>/bin/config set omero.web.ome_seadragon.repository $(./bin/omero config get omero.data.dir)
    'omero.web.ome_seadragon.repository': ['IMGS_REPOSITORY', None, identity, None],
    'omero.web.ome_seadragon.images_folder': ['IMGS_FOLDER', 'ManagedRepository', identity, None],
}
