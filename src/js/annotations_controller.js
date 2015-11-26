function AnnotationsController(canvas_id, default_config) {
    this.canvas_id = canvas_id;
    this.x_offset = undefined;
    this.y_offset = undefined;
    this.canvas = undefined;
    this.shapes_cache = {};
    // geometries appearance default configuration
    if (typeof default_config === 'undefined') {
        // to prevent errors in the following lines
        console.log('No configuration provided, using default values for shapes config');
        default_config = {};
    }
    this.default_fill_color = (typeof default_config.fill_color === 'undefined') ? '#ffffff' : default_config.fill_color;
    this.default_fill_alpha = (typeof default_config.opacity === 'undefined') ? 1 : default_config.fill_alpha;
    this.default_stroke_color = (typeof default_config.stroke_color === 'undefined') ? '#000000' : default_config.stroke_color;
    this.default_stroke_alpha = (typeof default_config.stroke_alpha === 'undefined') ? 1 : default_config.stroke_alpha;
    this.default_stroke_width = (typeof default_config.stroke_width === 'undefined') ? 20: default_config.stroke_width;

    this.buildAnnotationsCanvas = function (viewport_controller) {
        if (this.canvas === undefined) {
            this.x_offset = viewport_controller.getImageDimensions().width / 2;
            this.y_offset = viewport_controller.getImageDimensions().height / 2;

            var canvas = $("#" + this.canvas_id);
            if (canvas.length === 0) {
                console.log('Creating a new canvas');
                // create a canvas that will be used by paper.js
                var canvas_size = viewport_controller.getCanvasSize();
                $("body").append("<canvas id='" + this.canvas_id + "'></canvas>");
                $("#" + this.canvas_id).attr("width", canvas_size.width)
                    .attr("height", canvas_size.height);
                this.canvas = $("#" + this.canvas_id)[0];
            } else {
                console.log('Using an existing canvas');
                this.canvas = canvas[0];
            }

            paper.setup(this.canvas);
        } else {
            console.warn("Canvas already initialized");
        }
    };

    this.enableMouseEvents = function() {
        $("#" + this.canvas_id).css('pointer-events', 'auto');
    };

    this.disableMouseEvents = function() {
        $("#" + this.canvas_id).css('pointer-events', 'none');
    };

    var refresh = function(global_obj, auto_refresh) {
        var r = (typeof auto_refresh === 'undefined') ? true : auto_refresh;
        if (r) {
            global_obj.refreshView();
        }
    };

    this.refreshView = function() {
        console.log('Refreshing canvas');
        paper.view.draw();
    };

    this.setZoom = function(zoom_level) {
        paper.view.setZoom(zoom_level);
    };

    this.setCenter = function(center_x, center_y) {
        var center = new paper.Point(
            center_x - this.x_offset,
            center_y - this.y_offset
        );
        paper.view.setCenter(center);
    };

    this.addShapeToCache = function(shape) {
        if (! (shape.id in this.shapes_cache)) {
            this.shapes_cache[shape.id] = shape;
            return true;
        } else {
            console.error('ID ' + shape.id + ' already in use');
            return false;
        }
    };

    this.getShape = function(shape_id) {
        if (shape_id in this.shapes_cache) {
            return this.shapes_cache[shape_id];
        } else {
            return undefined;
        }
    };

    this.getShapeCenter = function(shape_id, apply_offset) {
        var add_offset = (typeof apply_offset === 'undefined') ? true : apply_offset;
        var shape = this.getShape(shape_id);
        if (shape !== 'undefined') {
            var x_offset = (add_offset === true) ? this.x_offset : 0;
            var y_offset = (add_offset === true) ? this.y_offset : 0;
            var shape_center = shape.getCenter();
            return {
                'x': shape_center.x + x_offset,
                'y': shape_center.y + y_offset
            }
        } else {
            return undefined;
        }
    };

    this.selectShape = function(shape_id, clear_selected, refresh_view) {
        var clear = (typeof clear_selected === 'undefined') ? false : clear_selected;
        if (clear === true) {
            for (var sh_id in this.shapes_cache) {
                this.deselectShape(sh_id);
            }
        }
        if (shape_id in this.shapes_cache) {
            this.shapes_cache[shape_id].select();
        }
        refresh(this, refresh_view);
    };

    this.selectShapes = function(shapes_id, clear_selected, refresh_view) {
        var clear = (typeof clear_selected === 'undefined') ? false : clear_selected;
        if (clear === true) {
            for (var index in this.shapes_cache) {
                this.deselectShape(shapes_id[index]);
            }
        }
        if (typeof shapes_id !== 'undefined') {
            for (var sh in shapes_id) {
                this.selectShape(sh, false, false);
            }
        } else {
            for (var sh in this.shapes_cache) {
                this.selectShape(sh, false, false);
            }
        }
        refresh(this, refresh_view);
    };

    this.deselectShape = function(shape_id, refresh_view) {
        if (shape_id in this.shapes_cache) {
            this.shapes_cache[shape_id].deselect();
        }
        refresh(this, refresh_view);
    };

    this.deselectShapes = function (shapes_id, refresh_view) {
        if (typeof shapes_id !== 'undefined') {
            for (var index in shapes_id) {
                this.deselectShape(shapes_id[index], false);
            }
        } else {
            for (var sh in this.shapes_cache) {
                this.deselectShape(sh, false);
            }
        }
        refresh(this, refresh_view);
    };

    this.showShape = function(shape_id, refresh_view) {
        if (shape_id in this.shapes_cache) {
            this.shapes_cache[shape_id].show();
        }
        refresh(this, refresh_view);
    };

    this.showShapes = function(shapes_id, refresh_view) {
        if (typeof shapes_id !== 'undefined') {
            for (var index in shapes_id) {
                this.showShape(shapes_id[index], false);
            }
        } else {
            for (var sh in this.shapes_cache) {
                this.showShape(sh, false);
            }
        }
        refresh(this, refresh_view);
    };

    this.hideShape = function(shape_id, refresh_view) {
        if (shape_id in this.shapes_cache) {
            this.shapes_cache[shape_id].hide();
        }
        refresh(this, refresh_view);
    };

    this.hideShapes = function (shapes_id, refresh_view) {
        if (typeof shapes_id !== 'undefined') {
            for (var index in shapes_id) {
                this.hideShape(shapes_id[index], false);
            }
        } else {
            for (var sh in this.shapes_cache) {
                this.hideShape(sh, false);
            }
        }
        refresh(this, refresh_view);
    };

    this.deleteShape = function(shape_id, refresh_view) {
        if (shape_id in this.shapes_cache) {
            this.shapes_cache[shape_id].delete();
            delete this.shapes_cache[shape_id];
        }
        refresh(this, refresh_view);
    };

    this.deleteShapes = function(shapes_id, refresh_view) {
        if (typeof shapes_id !== 'undefined') {
            for (var index in shapes_id) {
                this.deleteShape(shapes_id[index], false);
            }
            refresh(this, refresh_view);
        } else {
            this.clear(refresh_view);
        }
    };

    this.clear = function(refresh_view) {
        for (var shape_id in this.shapes_cache) {
            this.deleteShape(shape_id, false);
        }
        refresh(this, refresh_view);
    };

    this.normalizeShapeConfig = function(conf) {
        if (typeof conf === 'undefined') {
            conf = {};
        }
        return {
            'fill_color': (typeof conf.fill_color === 'undefined') ? this.default_fill_color : conf.fill_color,
            'fill_alpha': (typeof  conf.fill_alpha === 'undefined') ? this.default_fill_alpha : conf.fill_alpha,
            'stroke_color': (typeof conf.stroke_color === 'undefined') ? this.default_stroke_color : conf.stroke_color,
            'stroke_alpha': (typeof conf.stroke_alpha === 'undefined') ? this.default_stroke_alpha : conf.stroke_alpha,
            'stroke_width': (typeof conf.stroke_width === 'undefined') ? this.default_stroke_width : conf.stroke_width
        };
    };

    this.drawShape = function(shape, shape_conf, refresh_view) {
        var conf = this.normalizeShapeConfig(shape_conf);
        shape.toPaperShape();
        shape.configure(conf);
        refresh(this, refresh_view);
    };

    this.drawRectangle = function(shape_id, top_left_x, top_left_y, width, height, shape_conf, refresh_view) {
        var rect = new Rectangle(shape_id, top_left_x - this.x_offset, top_left_y - this.y_offset,
            width, height);
        if (this.addShapeToCache(rect)) {
            this.drawShape(rect, shape_conf, refresh_view);
        }
    };

    this.drawEllipse = function(shape_id, center_x, center_y, radius_x, radius_y, shape_conf, refresh_view) {
        var ellipse = new Ellipse(shape_id, center_x - this.x_offset, center_y - this.y_offset,
            radius_x, radius_y);
        if (this.addShapeToCache(ellipse)) {
            this.drawShape(ellipse, shape_conf, refresh_view);
        }
    };

    this.drawLine = function(shape_id, from_x, from_y, to_x, to_y, shape_conf, refresh_view) {
        var line = new Line(shape_id, from_x - this.x_offset, from_y - this.y_offset,
            to_x - this.x_offset, to_y - this.y_offset);
        if (this.addShapeToCache(line)) {
            this.drawShape(line, shape_conf, refresh_view);
        }
    };
}