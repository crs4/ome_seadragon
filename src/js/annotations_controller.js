function AnnotationsController(canvas_id, fill_color) {
    this.canvas_id = canvas_id;
    this.x_offset = undefined;
    this.y_offset = undefined;
    this.canvas = undefined;
    // geometries appearance default configuration
    this.default_fill_color = (typeof fill_color === 'undefined') ? 'black' : fill_color;

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

    this.configurePathObject = function(path_obj, conf) {
        var fill_color = (typeof conf.fill_color === 'undefined') ? this.default_fill_color : conf.fill_color;
        path_obj.setFillColor(fill_color);
    };

    this.drawRectangle = function(top_left_x, top_left_y, width, height, shape_conf, refresh_view) {
        refresh_view = (typeof refresh_view === 'undefined') ? true : refresh_view;
        var rect = new paper.Rectangle(
            top_left_x - this.x_offset,
            top_left_y - this.y_offset,
            width, height);
        var rpath = new paper.Path.Rectangle(rect);
        if (refresh_view === true) {
            this.refreshView();
        }
        this.configurePathObject(rpath, shape_conf);
        return rpath;
    };
}