function ViewerController(div_id, prefix_url, tile_sources) {
    this.viewer = undefined;
    this.div_id = div_id;
    this.prefix_url = prefix_url;
    this.tile_sources = tile_sources;

    this.buildViewer = function() {
        if (this.viewer === undefined) {
            this.viewer = OpenSeadragon({
                id: this.div_id,
                prefixUrl: this.prefix_url,
                tileSources: this.tile_sources
            });
        } else {
            console.warn("Viewer already created");
        }
    };

    this.getViewportDetails = function() {
        if (this.viewer !== undefined) {
            var zoom_level = this.viewer.viewport.getZoom();
            var center_point = this.viewer.viewport.getCenter();
            return {
                'zoom_level': zoom_level,
                'center_x': center_point.x,
                'center_y': center_point.y
            };
        } else {
            console.warn("Viewer not initialized!");
            return undefined;
        }
    };

    this.jumpToPoint = function(center_x, center_y) {
        if (this.viewer !== undefined) {
            var center_point = new OpenSeadragon.Point(center_x, center_y);
            this.viewer.viewport.panTo(center_point);
        } else {
            console.warn("Viewer not initialized!");
        }
    };

    this.jumpTo = function(zoom_level, center_x, center_y) {
        if (this.viewer !== undefined) {
            this.jumpToPoint(center_x, center_y);
            this.viewer.viewport.zoomTo(zoom_level);
        } else {
            console.warn("Viewer not initialized!");
        }
    };

    this.getViewportCoordinates = function(point_x, point_y) {
        var vc_point = this.viewer.viewport.imageToViewportCoordinates(point_x, point_y);
        return {
            'point_x': vc_point.x,
            'point_y': vc_point.y
        }
    };
}
