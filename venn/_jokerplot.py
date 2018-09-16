from matplotlib.path import Path
from matplotlib.patches import PathPatch
from matplotlib.pyplot import subplots
from ._venn import is_valid_dataset_dict, init_axes, generate_petal_labels
from ._venn import generate_colors, less_transparent_color, draw_ellipse
from ._constants import CENTER_TEXT, TOP_TEXT, TRUNK_XFIT, TRUNK_YFIT

def draw_spline(coords, color, ax):
    """Convert list of lists of tuples of coordinates to path, add to `ax` as patch"""
    vertices, codes = [coords[0][0]], [Path.MOVETO]
    for curve_coords in coords[1:]:
        vertices.extend(curve_coords)
        if len(curve_coords) == 1:
            codes.extend([Path.LINETO])
        elif len(curve_coords) == 2:
            codes.extend([Path.CURVE3]*2)
        elif len(curve_coords) == 3:
            codes.extend([Path.CURVE4]*3)
        else:
            raise ValueError
    vertices.append(coords[0][0])
    codes.append(Path.CLOSEPOLY)
    path = Path(vertices, codes)
    patch = PathPatch(
        path, facecolor=color, edgecolor=less_transparent_color(color)
    )
    ax.add_patch(patch)

def draw_leaf(k, n_sets, color, label, fontsize, ax):
    """Draw one segment of joker's hat, including cicle, and label"""
    coords = [
        [(-4, -2)], [(-4-4*k/n_sets, k*1.5+2), (10, k)],
        [(9.5, k-.3)], [(-6/(n_sets-k), k*.9-1), (0, -2)]
    ]
    draw_spline(coords, color=color, ax=ax)
    draw_ellipse(10.6, k-.2, .9, .9, 0, color, ax)
    ax.text(11.2, k-.05, label, fontsize=fontsize, **TOP_TEXT)

def draw_jokerplot_trunk_labels(petal_labels, fontsize, ax):
    """Add labels to intersections in trunk of jokerplot"""
    n_sets = len(list(petal_labels.keys())[0])
    trunk_x, trunk_y = (
        TRUNK_XFIT(range(n_sets)), TRUNK_YFIT(range(n_sets))
    )
    for n in range(n_sets):
        logic = bin(2**(n_sets-n)-1)[2:].zfill(n_sets)
        if logic in petal_labels:
            ax.text(
                trunk_x[n], trunk_y[n], petal_labels[logic],
                fontsize=fontsize, **CENTER_TEXT
            )

def draw_jokerplot_bell_labels(bell_labels, fontsize, ax):
    """Add labels to bells in jokerplot (full sizes of datasets)"""
    for k, label in enumerate(bell_labels):
        ax.text(10.6, k-.2, label, fontsize=fontsize, **CENTER_TEXT)

def draw_jokerplot(*, petal_labels, bell_labels, dataset_labels, zorder, colors, figsize, fontsize, ax):
    """Draw intersection of 6 leaves (does not include some combinations), annotate petals and dataset labels"""
    n_sets = len(dataset_labels)
    if n_sets > 6:
        raise NotImplementedError("Jokerplots for 7+ sets under development")
    if figsize is None:
        figsize = (20, 2*n_sets+6)
    ax = init_axes(ax, figsize)
    ax.set(xlim=(-5, 15), ylim=(-2.5, .5+n_sets))
    param_iterator = zip(range(n_sets), dataset_labels, colors)
    if zorder == "reversed":
        param_iterator = reversed(list(param_iterator))
    elif zorder != "default":
        raise ValueError("`zorder` can only be 'default' or 'reversed'")
    for k, label, color in param_iterator:
        draw_leaf(k, n_sets, color, label, fontsize, ax)
    draw_jokerplot_trunk_labels(petal_labels, fontsize, ax)
    draw_jokerplot_bell_labels(bell_labels, fontsize, ax)
    return ax

def jokerplot(
        data, petal_labels=None, fmt="{size}",
        cmap="viridis", alpha=.3, zorder="default",
        figsize=None, fontsize=13, ax=None
    ):
    """Check input, generate petal labels, draw jokerplot"""
    if not is_valid_dataset_dict(data):
        raise TypeError("Only dictionaries of sets are understood")
    n_sets = len(data)
    if petal_labels is None:
        if fmt is None:
            fmt = "{size}"
        petal_labels=generate_petal_labels(data.values(), fmt)
    elif fmt is not None:
        warn("Passing `fmt` with `petal_labels` will have no effect")
    return draw_jokerplot(
        petal_labels=petal_labels,
        bell_labels=[len(dataset) for dataset in data.values()],
        dataset_labels=data.keys(),
        colors=generate_colors(n_colors=n_sets, cmap=cmap, alpha=alpha),
        zorder=zorder, figsize=figsize, fontsize=fontsize, ax=ax
    )
