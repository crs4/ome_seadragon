#!/bin/bash

#  Copyright (c) 2021, CRS4
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy of
#  this software and associated documentation files (the "Software"), to deal in
#  the Software without restriction, including without limitation the rights to
#  use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
#  the Software, and to permit persons to whom the Software is furnished to do so,
#  subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
#  FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
#  COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
#  IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
#  CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

OMERO_HOST="localhost"
OMERO_PORT=4064
OME_ROOT_PASS="omero"
OME_PUBLIC_GROUP="ome_public_data"
OME_PUBLIC_USER="ome_public"
OME_PUBLIC_USER_PASS="omero"
REDISHOST="localhost"
REDISPORT=6379
REDISDB=0
CACHE_EXPIRE_TIME='{"minutes": 30}'
IMAGES_FOLDER="/tmp/images"
MIRAX_FOLDER="/tmp/mirax"
DATASETS_REPOSITORY="/tmp/datasets"

omero config set omero.web.server_list '[["'$OMERO_HOST'", '$OMERO_PORT', "omero-dev"]]'
omero config set omero.web.application_server development
omero config set omero.web.debug True

export PYTHONPATH="$(dirname $PWD):$PYTHONPATH"

omero config append omero.web.apps '"ome_seadragon"'

omero config append omero.web.apps '"corsheaders"'
omero config append omero.web.middleware '{"index": 0.5, "class": "corsheaders.middleware.CorsMiddleware"}'
omero config append omero.web.middleware '{"index": 10, "class": "corsheaders.middleware.CorsPostCsrfMiddleware"}'
omero config set omero.web.cors_origin_allow_all True

omero group add --ignore-existing --server $OMERO_HOST --port $OMERO_PORT --user root \
                --password $OME_ROOT_PASS --type read-only $OME_PUBLIC_GROUP
omero user add --ignore-existing --server $OMERO_HOST --port $OMERO_PORT --user root \
               --password $OME_ROOT_PASS $OME_PUBLIC_USER OME PUBLIC --group-name $OME_PUBLIC_GROUP \
               --userpassword $OME_PUBLIC_USER_PASS
omero config set omero.web.public.enabled True
omero config set omero.web.public.user $OME_PUBLIC_USER
omero config set omero.web.public.password $OME_PUBLIC_USER_PASS
omero config set omero.web.public.url_filter "^/ome_seadragon"
omero config set omero.web.public.server_id 1

omero config set omero.web.ome_seadragon.ome_public_user $OME_PUBLIC_USER

omero config set omero.web.ome_seadragon.images_cache.cache_enabled True
omero config set omero.web.ome_seadragon.images_cache.driver 'redis'
omero config set omero.web.ome_seadragon.images_cache.host $REDISHOST
omero config set omero.web.ome_seadragon.images_cache.port $REDISPORT
omero config set omero.web.ome_seadragon.images_cache.database $REDISDB
omero config set omero.web.ome_seadragon.images_cache.expire_time "$CACHE_EXPIRE_TIME"

omero config set omero.web.ome_seadragon.images_folder "$IMAGES_FOLDER"
omero config set omero.web.ome_seadragon.mirax_folder "$MIRAX_FOLDER"

omero config set omero.web.ome_seadragon.tiles.primary_rendering_engine "openslide"
omero config set omero.web.ome_seadragon.tiles.secondary_rendering_engine "omero"
omero config set omero.web.ome_seadragon.thumbnails.primary_rendering_engine "omero"
omero config set omero.web.ome_seadragon.thumbnails.secondary_rendering_engine "openslide"

omero config set omero.web.ome_seadragon.deepzoom.overlap 1
omero config set omero.web.ome_seadragon.deepzoom.format "jpeg"
omero config set omero.web.ome_seadragon.deepzoom.jpeg_tile_quality 90
omero config set omero.web.ome_seadragon.deepzoom.limit_bounds True
omero config set omero.web.ome_seadragon.deepzoom.tile_size 256

omero config set omero.web.ome_seadragon.dzi_adapter.datasets.repository "$DATASETS_REPOSITORY"
