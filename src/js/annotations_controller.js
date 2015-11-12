function AnnotationsController(canvas_id, default_config) {
    this.canvas_id = canvas_id;
    this.x_offset = undefined;
    this.y_offset = undefined;
    this.canvas = undefined;
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

    this.configureShape = function(shape, conf) {
        if (typeof conf === 'undefined') {
            conf = {};
        }
        var fill_color = (typeof conf.fill_color === 'undefined') ? this.default_fill_color : conf.fill_color;
        var fill_alpha = (typeof  conf.fill_alpha === 'undefined') ? this.default_fill_alpha : conf.fill_alpha;
        shape.setFillColor(ColorsAdapter.hexToPaperColor(fill_color, fill_alpha));
        var stroke_color = (typeof conf.stroke_color === 'undefined') ? this.default_stroke_color : conf.stroke_color;
        var stroke_alpha = (typeof conf.stroke_alpha === 'undefined') ? this.default_stroke_alpha : conf.stroke_alpha;
        shape.setStrokeColor(ColorsAdapter.hexToPaperColor(stroke_color, stroke_alpha));
        var stroke_width = (typeof conf.stroke_width === 'undefined') ? this.default_stroke_width : conf.stroke_width;
        shape.setStrokeWidth(stroke_width);
    };

    this.drawShape = function(shape, shape_conf, refresh_view) {
        refresh_view = (typeof refresh_view === 'undefined') ? true : refresh_view;
        this.configureShape(shape, shape_conf);
        if (refresh_view === true) {
            this.refreshView();
        }
    };

    this.drawRectangle = function(top_left_x, top_left_y, width, height, shape_conf, refresh_view) {
        var rect = new paper.Shape.Rectangle({
            point: [
                top_left_x - this.x_offset,
                top_left_y - this.y_offset
            ],
            size: [width, height]
        });
        this.drawShape(rect, shape_conf, refresh_view);
        return rect;
    };

    this.drawEllipse = function(center_x, center_y, size_x, size_y, shape_conf, refresh_view) {
        var ellipse = new paper.Shape.Ellipse({
            point: [
                center_x - this.x_offset,
                center_y - this.y_offset
            ],
            size: [size_x, size_y]
        });
        this.drawShape(ellipse, shape_conf, refresh_view);
        return ellipse;
    };

    this.drawLine = function(from_x, from_y, to_x, to_y, shape_conf, refresh_view) {
        var line = new paper.Path.Line({
            from: [
                from_x - this.x_offset,
                from_y - this.y_offset
            ],
            to: [
                to_x - this.x_offset,
                to_y - this.y_offset
            ]
        });
        this.drawShape(line, shape_conf, refresh_view);
        return line;
    };
}