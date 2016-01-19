function ViewerController(div_id, prefix_url, tile_sources, viewer_config) {
    this.viewer = undefined;
    this.div_id = div_id;
    this.prefix_url = prefix_url;
    this.tile_sources = tile_sources;
    this.config = viewer_config;

    this.buildViewer = function() {
        if (this.viewer === undefined) {
            var base_config = {
                id: this.div_id,
                prefixUrl: this.prefix_url,
                tileSources: this.tile_sources
            };
            $.extend(base_config, this.config);
            this.viewer = OpenSeadragon(base_config);
        } else {
            console.warn("Viewer already created");
        }
    };

    this.setMinDZILevel = function(level) {
        if (typeof this.viewer !== 'undefined') {
            this.viewer.source.minLevel = level;
        }
    };

    this.enableScalebar = function(image_mpp, scalebar_config) {
        if (typeof this.viewer !== "undefined" && image_mpp > 0) {
            var pixels_per_meter = (1e6 / image_mpp);
            var sc_conf = {'pixelsPerMeter': pixels_per_meter};
            if (typeof scalebar_config !== "undefined") {
                $.extend(sc_conf, scalebar_config);
            }
            this.viewer.scalebar(sc_conf);
        }
    };

    this.getViewportDetails = function(viewport_coordinates) {
        if (this.viewer !== undefined) {
            var vp_coord = (typeof viewport_coordinates === 'undefined') ? false : viewport_coordinates;
            var zoom_level = this.viewer.viewport.getZoom();
            var center_point = this.viewer.viewport.getCenter();
            if (vp_coord === false) {
                center_point = this.getImageCoordinates(center_point.x, center_point.y);
            }
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
            'x': vc_point.x,
            'y': vc_point.y
        }
    };

    this.getImageCoordinates = function(point_x, point_y) {
        var img_point = this.viewer.viewport.viewportToImageCoordinates(point_x, point_y);
        return {
            'x': img_point.x,
            'y': img_point.y
        }
    };

    this.getCanvasSize = function() {
        if (this.viewer !== undefined) {
            return {
                'width': $("#" + this.div_id).width(),
                'height': $("#" + this.div_id).height()
            }
        } else {
            console.warn("Viewer not initialized!");
            return undefined;
        }
    };

    this.getImageDimensions = function() {
        if (this.viewer !== undefined) {
            return {
                'width': this.viewer.viewport.contentSize.x,
                'height': this.viewer.viewport.contentSize.y
            }
        } else {
            console.warn('Viewer not initialized');
            return undefined;
        }
    };

    this.getCenter = function() {
        var img_center = this.viewer.viewport.viewportToImageCoordinates(this.viewer.viewport.getCenter());
        return {'x': img_center.x, 'y': img_center.y};
    };

    this.getImageZoom = function() {
        return this.viewer.viewport.viewportToImageZoom(this.viewer.viewport.getZoom());
    };

    this.addAnnotationsController = function(annotations_controller, stop_annotations_controller_events) {
        var stop_events = (typeof stop_annotations_controller_events === 'undefined') ?
            true : stop_annotations_controller_events;
        // attach annotations_controller to viewer object, this will be useful when handling events
        this.viewer.annotations_controller = annotations_controller;
        this.viewer.viewport_controller = this;

        // set zoom level for the annotations_controller
        var img_zoom = this.getImageZoom();
        annotations_controller.setZoom(img_zoom);
        var center = this.getCenter();
        annotations_controller.setCenter(center.x, center.y);

        // paper.js canvas won't listen to mouse events, they will be propagated to OpenSeadragon viewer
        if (stop_events === true) {
            annotations_controller.disableMouseEvents();
        }

        this.viewer.addHandler('animation', function(event) {
            var v_center = event.eventSource.viewport_controller.getCenter();
            event.eventSource.annotations_controller.setCenter(v_center.x, v_center.y);
            var img_zoom = event.eventSource.viewport_controller.getImageZoom();
            event.eventSource.annotations_controller.setZoom(img_zoom);
        });
    };
}
