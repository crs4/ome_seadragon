function ColorsAdapter() {}

ColorsAdapter.isHexColor = function(color_string) {
    return /(^#[0-9A-F]{6}$)|(^#[0-9A-F]{3}$)/i.test(color_string);
};

ColorsAdapter.hexToRGB = function(hex_color) {
    if (hex_color.length === 7) {
        return {
            'red': parseInt(hex_color.substring(1, 3), 16),
            'green': parseInt(hex_color.substring(3, 5), 16),
            'blue': parseInt(hex_color.substring(5, 7), 16)
        }
    } else if (hex_color.length === 4) {
        return {
            'red': parseInt(hex_color[1], 16),
            'green': parseInt(hex_color[2], 16),
            'blue': parseInt(hex_color[3], 16)
        }
    } else {
        console.error('Unable to convert to RGB value ' + hex_color);
    }
};

ColorsAdapter.RGBIntToFloat = function(rgb_int) {
    var constant = 1/255;
    return {
        'red':rgb_int.red * constant,
        'green': rgb_int.green * constant,
        'blue': rgb_int.blue * constant
    }
};

ColorsAdapter.hexToPaperColor = function(hex_color, alpha_value) {
    if (!ColorsAdapter.isHexColor(hex_color)) {
        console.error(hex_color + ' is not a valid HEX color string');
        return undefined;
    }
    var rgb_color = ColorsAdapter.RGBIntToFloat(ColorsAdapter.hexToRGB(hex_color));
    var alpha = (typeof alpha_value === 'undefined') ? 1 : alpha_value;
    return new paper.Color(rgb_color.red, rgb_color.green, rgb_color.blue, alpha);
};

ColorsAdapter.paperColorToHex = function(paper_color) {
    return {
        'hex_color': paper_color.toCSS(true),
        'alpha': paper_color.getAlpha()
    }
};


function TransformMatrixHelper() {}

TransformMatrixHelper.getPaperMatrix = function(a, c, b, d, tx, ty) {
    return new paper.Matrix(a, c, b, d, tx, ty);
};

TransformMatrixHelper.getTranslationMatrix = function(tx, ty) {
    return TransformMatrixHelper.getPaperMatrix(1, 0, 0, 1, tx, ty);
};

TransformMatrixHelper.fromOMEMatrix = function(ome_matrix_elements) {
    return TransformMatrixHelper.getPaperMatrix(
        Number(ome_matrix_elements[0]), Number(ome_matrix_elements[1]),
        Number(ome_matrix_elements[2]), Number(ome_matrix_elements[3]),
        Number(ome_matrix_elements[4]), Number(ome_matrix_elements[5])
    )
};

TransformMatrixHelper.fromOMETranslate = function(ome_translate_elements) {
    return TransformMatrixHelper.getTranslationMatrix(
        Number(ome_translate_elements[0]), Number(ome_translate_elements[1])
    )
};

TransformMatrixHelper.fromOMETransform = function(ome_transform) {
    if (ome_transform === 'none' || typeof(ome_transform) === 'undefined')
        return undefined;
    var transform_type = ome_transform.substr(0, ome_transform.search('\\('));
    var transform_data = ome_transform.substr(
        ome_transform.search('\\(') + 1,
        ome_transform.search('\\)') - ome_transform.search('\\(') - 1
    ).split(' ');
    switch (transform_type){
        case 'matrix':
            return TransformMatrixHelper.fromOMEMatrix(transform_data);
        case 'translate':
            return TransformMatrixHelper.fromOMETranslate(transform_data);
        default:
            console.warn('Unknown transform type: ' + transform_type);
            return undefined;
    }
};

TransformMatrixHelper.fromMatrixJSON = function(matrix_json) {
    if (matrix_json && matrix_json[0] === 'Matrix') {
        return this.getPaperMatrix(
            matrix_json[1], matrix_json[2], matrix_json[3],
            matrix_json[4], matrix_json[5], matrix_json[6]
        );
    } else {
        console.warn('Not a valid Matrix JSON');
        return undefined;
    }
};

function ShapeConverter() {}

ShapeConverter.extractPathSegments = function(paper_shape, x_offset, y_offset) {
    var x_off = (typeof x_offset === 'undefined') ? 0 : x_offset;
    var y_off = (typeof y_offset === 'undefined') ? 0: y_offset;
    var segments = [];
    try {
        var paper_segments = paper_shape.getSegments();
    } catch(err) {
        var paper_segments = new paper.CompoundPath(paper_shape.getPathData()).getSegments();
    }
    for (var i=0 ; i<paper_segments.length; i++) {
        var segment = {
            point: {
                x: paper_segments[i].getPoint().x + x_off,
                y: paper_segments[i].getPoint().y + y_off
            }
        };
        if (paper_segments[i].getHandleIn().length > 0) {
            segment['handle_in'] = {
                x: paper_segments[i].getHandleIn().x,
                y: paper_segments[i].getHandleIn().y
            }
        }
        if (paper_segments[i].getHandleOut().length > 0) {
            segment['handle_out'] = {
                x: paper_segments[i].getHandleOut().x,
                y: paper_segments[i].getHandleOut().y
            }
        }
        segments.push(segment);
    }
    return segments;
};

ShapeConverter.keepBiggerShape = function(path_items) {
    console.log(path_items);
    try {
        // single path, no need to filter
        path_items.getSegments();
        return path_items;
    } catch(err) {
        var bigger_area = undefined;
        var selected_children_index = undefined;
        for (var ch in path_items.getChildren()) {
            var children_path = path_items.children[ch];
            if (typeof selected_children_index !== 'undefined') {
                if (children_path.getArea() > bigger_area) {
                    selected_children_index = ch;
                    bigger_area = children_path.getArea();
                }
            } else {
                selected_children_index = ch;
                bigger_area = children_path.getArea();
            }
        }
        return path_items.children[selected_children_index];
    }
};
