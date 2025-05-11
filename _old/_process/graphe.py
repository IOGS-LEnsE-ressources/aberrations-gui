#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Outils Numériques pour l'Ingénieur.e en Physique
Bibliothèque de graphiques

Created on Tue Sep 26 2023

@author: Dorian Mendes
"""
# %% Libraries
import matplotlib.pyplot as plt


# %% New plot
def new_plot(fig_output=False, *args, **kwargs):
    """
    Generate a new plot area.

    Parameters
    ----------
    fig_output : bool, optional
        Define if the function has to return the variable of the Figure instance.
        The default is False.

    Returns
    -------
    matplotlib.Axis or (matplotlib.Figure, matplotlib.Axis)
        The new plot area.

    """
    fig, ax = plt.subplots(1, 1, *args, **kwargs)
    if fig_output:
        return fig, ax
    else:
        return ax


# %% New mosaique
def new_mosaique(nb_rows, nb_columns, style=None, fig_output=False, *args, **kwargs):
    """
    Generate a new grid of plots.

    Parameters
    ----------
    nb_rows : int
        The number of rows of the grid.
    nb_columns : int
        The number of columns of the grid.
    style : dict, optional
        The dictionnary matching the style of each cell of the grid (XY plot, X-Ylog plot, polar plot, etc.).
        The keys of this dictionary are the couple of the coordinates (i, j)  of the cell.
        The values are a function of this module.
        The default is None.
    fig_output : bool, optional
        Define if the function has to return the variable of the Figure instance.
        The default is False.

    Returns
    -------
    matplotlib.Axis or (matplotlib.Figure, matplotlib.Axis)
        The new plot grid.

    """
    # Style sous la forme {(0,0): ..., (1,0):..., etc}
    fig, ax = plt.subplots(nb_rows, nb_columns, tight_layout=True, *args, **kwargs)
    if style is not None:
        for k in style.keys():
            if k is not None:
                ax[k] = style[k](ax[k])
    if fig_output:
        return fig, ax
    else:
        return ax


# %% Axes modifiers
def lin_XY(ax, title='', x_label='', x_unit='', y_label='', y_unit='', axis_intersect=(0, 0)):
    """
    Set the style of a plot to a plot with linear axis.

    Parameters
    ----------
    ax : matplotlib.Axis
        The axis we want to modify.
    title : str, optional
        The title of the plot.
        LaTeX writing is available.
        The default is ''.
    x_label : str, optional
        The label of the X axis.
        LaTeX writing is available.
        The default is ''.
    x_unit : str, optional
        The unit of the X axis.
        LaTeX writing is available.
        The default is ''.
    y_label : str, optional
        The label of the Y axis.
        LaTeX writing is available.
        The default is ''.
    y_unit : str, optional
        The unit of the Y axis.
        LaTeX writing is available.
        The default is ''.
    axis_intersect : tuple, optional
        The coordinates of the intersection point between X and Y.
        The default is (0, 0).

    Returns
    -------
    ax : matplotlib.Axis
        The axis modified.

    """
    ax.spines['left'].set_position('zero')
    ax.spines['bottom'].set_position('zero')
    ax.spines[['right', 'top']].set_color('none')

    ax.xaxis.set_ticks_position('bottom')
    ax.yaxis.set_ticks_position('left')

    if x_unit == '':
        ax.set_xlabel(r"{}".format(x_label), loc='right')
    else:
        ax.set_xlabel(r"{} ({})".format(x_label, x_unit), loc='right')
    if y_unit == '':
        ax.set_ylabel(r"{}".format(y_label), loc='top')
    else:
        ax.set_ylabel(r"{} ({})".format(y_label, y_unit), loc='top')

    x0, y0 = axis_intersect
    ax.spines['left'].set_position(['data', x0])
    ax.spines['bottom'].set_position(['data', y0])

    ax.set_title(title)
    return ax


def empty(ax):
    """
    Set the style of a plot to an empty plot.

    Parameters
    ----------
    ax : matplotlib.Axis
        The axis modified.

    Returns
    -------
    ax : TYPE
        DESCRIPTION.

    """
    ax.axis('off')
    return ax


def log_X(ax, title='', x_label='', x_unit='', y_label='', y_unit='', x_intersect=None, y_intersect=0):
    ax.set_xscale('log')
    ax.spines['bottom'].set_position('zero')
    ax.spines[['right', 'top']].set_color('none')

    ax.xaxis.set_ticks_position('bottom')
    ax.yaxis.set_ticks_position('left')

    if x_unit == '':
        ax.set_xlabel(r"{} [log]".format(x_label), loc='right')
    else:
        ax.set_xlabel(r"{} ({}) [log]".format(x_label, x_unit), loc='right')
    if y_unit == '':
        ax.set_ylabel(r"{}".format(y_label), loc='top')
    else:
        ax.set_ylabel(r"{} ({})".format(y_label, y_unit), loc='top')

    if x_intersect is not None:
        ax.spines['left'].set_position(['data', x_intersect])
    ax.spines['bottom'].set_position(['data', y_intersect])

    ax.set_title(title)
    return ax


def log_Y(ax, title='', x_label='', x_unit='', y_label='', y_unit='', x_intersect=0, y_intersect=None):
    ax.set_yscale('log')
    ax.spines['left'].set_position('zero')
    ax.spines[['right', 'top']].set_color('none')

    ax.xaxis.set_ticks_position('bottom')
    ax.yaxis.set_ticks_position('left')

    if x_unit == '':
        ax.set_xlabel(r"{}".format(x_label), loc='right')
    else:
        ax.set_xlabel(r"{} ({})".format(x_label, x_unit), loc='right')
    if y_unit == '':
        ax.set_ylabel(r"{} [log]".format(y_label), loc='top')
    else:
        ax.set_ylabel(r"{} ({}) [log]".format(y_label, y_unit), loc='top')

    if y_intersect is not None:
        ax.spines['bottom'].set_position(['data', y_intersect])
    ax.spines['left'].set_position(['data', x_intersect])

    ax.set_title(title)
    return ax


def log_XY(ax, title='', x_label='', x_unit='', y_label='', y_unit='', x_intersect=None, y_intersect=None):
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.spines[['right', 'top']].set_color('none')

    ax.xaxis.set_ticks_position('bottom')
    ax.yaxis.set_ticks_position('left')

    if x_unit == '':
        ax.set_xlabel(r"{} [log]".format(x_label), loc='right')
    else:
        ax.set_xlabel(r"{} ({}) [log]".format(x_label, x_unit), loc='right')
    if y_unit == '':
        ax.set_ylabel(r"{} [log]".format(y_label), loc='top')
    else:
        ax.set_ylabel(r"{} ({}) [log]".format(y_label, y_unit), loc='top')

    if x_intersect is not None:
        ax.spines['left'].set_position(['data', x_intersect])
    if y_intersect is not None:
        ax.spines['bottom'].set_position(['data', y_intersect])

    ax.set_title(title)
    return ax