import math
import cairo
import os
import typing as t
import pyRavenMatrices.matrix as mat
import pyRavenMatrices.element as elt


#################
### UTILITIES ###
#################


def _get_dims(cell_structure: mat.CellStructure) -> t.Tuple[int, int]:

    width = cell_structure.width - (2 * cell_structure.horizontal_margin)
    height = cell_structure.height - (2 * cell_structure.vertical_margin)

    return width, height


##############
### SHAPES ###
##############


def ellipse(
    ctx: cairo.Context, cell_structure: mat.CellStructure, r: float = 2
) -> None:
    """
    Draw an ellipse in the given context.

    Drawing is centered relative to cell structure, and semi-major is aligned 
    with vertical coordinate axis.

    :param ctx: Current context.
    :param cell_structure: Assumptions about structure of the cell being drawn.
    :param r: Semi-major over semi-minor, must be > 2.
    """
    
    if not 2 <= r:        
        raise ValueError()

    width, height = _get_dims(cell_structure)
    
    ctx.save()
    ctx.translate(cell_structure.width / 2., cell_structure.height / 2.)
    ctx.scale(width / (2 * r), height / 2)
    ctx.new_sub_path()
    ctx.arc(0., 0., 1., 0., 2 * math.pi)
    ctx.restore()


def triangle(ctx, cell_structure, r=1):
    """
    Draw a triangle in the given context.

    Drawing is centered relative to cell structure.

    :param ctx: Current context.
    :param cell_structure: Assumptions about structure of the cell being drawn.
    :param r: height over base, must be > 0.
    """
    
    if not 0 < r:        
        raise ValueError()
        
    width, height = _get_dims(cell_structure)

    div = max(1, r)
    
    ctx.save()
    ctx.translate(cell_structure.width / 2., cell_structure.height / 2.)
    ctx.scale(1 / div, r / div)
    ctx.new_sub_path()
    ctx.move_to(- width / 2., height / 2.)
    ctx.line_to(width / 2., height / 2.)
    ctx.line_to(0, - height / 2.)
    ctx.line_to(- width / 2., height / 2.)
    ctx.restore()


def rectangle(ctx, cell_structure, r = 2):
    
    if not r >= 2:
        raise ValueError()
    
    width, height = _get_dims(cell_structure)

    ctx.save()
    ctx.translate(cell_structure.width / 2., cell_structure.height / 2.)
    ctx.scale(1 / r, 1)
    ctx.new_sub_path()
    ctx.move_to(- width / 2., height / 2.)
    ctx.line_to(width / 2., height / 2.)
    ctx.line_to(width / 2., - height / 2.)
    ctx.line_to(- width / 2., - height / 2.)
    ctx.line_to(- width / 2., height / 2.)
    ctx.restore()


def trapezoid(ctx, cell_structure, r=1):
    
    if not r > 0:        
        raise ValueError()

    width, height = _get_dims(cell_structure)
    
    div = max(1, r)
    
    ctx.save()
    ctx.translate(cell_structure.width / 2., cell_structure.height / 2.)
    ctx.scale(1 / div, r / div)
    ctx.new_sub_path()
    ctx.move_to(- width / 2., height / 2.)
    ctx.line_to(width / 2., height / 2.)
    ctx.line_to(width / 4., - height / 2.)
    ctx.line_to(- width / 4., - height / 2.)
    ctx.line_to(- width / 2., height / 2.)
    ctx.restore()


def diamond(ctx, cell_structure, r=1):
    
    if not 1 <= r:        
        raise ValueError()
 
    width, height = _get_dims(cell_structure)
    
    ctx.save()
    ctx.translate(cell_structure.width / 2., cell_structure.height / 2.)
    ctx.scale(1 / r, 1)
    ctx.new_sub_path()
    ctx.move_to(0, height / 2.)
    ctx.line_to(width / 2., - height / 4.)
    ctx.line_to(0, - height / 2.)
    ctx.line_to(- width / 2., - height / 4.)
    ctx.line_to(0, height / 2.)
    ctx.restore()


def tee(ctx, cell_structure, r=1):
    
    if not 0 < r:        
        raise ValueError()

    width, height = _get_dims(cell_structure)
    
    div = max(1, r)
    
    ctx.save()
    ctx.translate(cell_structure.width / 2., cell_structure.height / 2.)
    ctx.scale(1 / div, r / div)
    ctx.new_sub_path()
    ctx.move_to(- width / 6., height / 2.)
    ctx.line_to(width / 6., height / 2.)
    ctx.line_to(width / 6., - height / 4.)
    ctx.line_to(width / 2., - height / 4.)
    ctx.line_to(width / 2., - height / 2.)
    ctx.line_to(- width / 2., - height / 2.)
    ctx.line_to(- width / 2., - height / 4.)
    ctx.line_to(- width / 6., - height / 4.)
    ctx.line_to(- width / 6., height / 2.)
    ctx.restore()


#################
### MODIFIERS ###
#################


def scale(element, factor=.5):

    def wrapped(ctx, cell_structure, *args, **kwargs):

        ctx.save()
        ctx.translate(cell_structure.width / 2., cell_structure.height / 2.)
        ctx.scale(factor, factor)
        ctx.translate(- cell_structure.width / 2., - cell_structure.height / 2.)    
        element(ctx, cell_structure, *args, **kwargs)
        ctx.restore()

    return wrapped


def rotation(element, angle=math.pi/2.):

    def wrapped(ctx, cell_structure, *args, **kwargs):

        ctx.save()
        ctx.translate(cell_structure.width / 2., cell_structure.height / 2.)
        ctx.rotate(angle)
        ctx.translate(-cell_structure.width / 2., -cell_structure.height / 2.)
        element(ctx, cell_structure)
        ctx.restore()
        
    return wrapped


def shading(element, lightness=.5):
    
    def wrapped(ctx, cell_structure, *args, **kwargs):

        element(ctx, cell_structure, *args, **kwargs)
        ctx.save()
        ctx.set_source_rgb(lightness, lightness, lightness)
        ctx.fill_preserve()
        ctx.restore()
    
    return wrapped


def numerosity(element, number=5):
    
    def wrapped(ctx, cell_structure, *args, **kwargs):
        if i > 4:
            for i in range(number):
                
                x = (i % 3) * (cell_structure.width / 3.)
                y = (i // 3) * (cell_structure.height / 3.)
                
                ctx.save()
                ctx.translate(x, y)
                ctx.scale(1 / 3, 1 / 3)
                element(ctx, cell_structure, *args, **kwargs)
                ctx.restore()
        else:
            for i in range(number):
                
                x = (i % 2) * (cell_structure.width / 2.)
                y = (i // 2) * (cell_structure.height / 2.)
                
                ctx.save()
                ctx.translate(x, y)
                ctx.scale(1 / 2, 1 / 2)
                element(ctx, cell_structure, *args, **kwargs)
                ctx.restore()

    
    return wrapped
