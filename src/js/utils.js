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
