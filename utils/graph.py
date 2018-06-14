# Bokeh
from bokeh.plotting import figure, output_file, show
from bokeh.embed import components
from bokeh.models import FactorRange
from numpy import pi
from utils.tweet_test import group_by_date, filtrar_df_fecha, buscar_palabra_df, n_palabras_comun, hashtags_pie, count_locations
import datetime
import numpy as np
from math import log, sqrt


# Test Pie Chart with Bokeh
def test_pie_chart(df_bueno, pie_chart_resul, plot_width=400, plot_height=400, most_common=5):


    p = figure(plot_width=plot_width, plot_height=plot_height, title="",
               x_axis_type=None, y_axis_type=None,
               x_range=(-420, 420), y_range=(-420, 420),
               min_border=0, #outline_line_color="black",
               background_fill_color="#f2f7f6")
    p.xgrid.grid_line_color = None
    p.ygrid.grid_line_color = None
    p.toolbar.logo = None
    p.toolbar_location = None


    h_counter = hashtags_pie(df_bueno, most_common=most_common)
    h_counter = sorted(h_counter, key=lambda tup: tup[1])
    total_h = sum([x[1] for x in h_counter])
    percents = [ float(x[1])/float(total_h) for x in h_counter ]
    starts = []
    count = 0
    for per in percents:
        count = (per * np.pi * 2) + count
        starts.append(count)
    ends = starts[1:]+[starts[0]]

    colors = ["#CD5C5C", "#F08080", "#FA8072", "#E9967A", "#FFA07A"]
    if most_common>len(colors):
        i = int(most_common/len(colors))
        colors += colors*(i-1)
        colors += colors[:most_common%len(colors)]
    else:
        colors = colors[:most_common]

    #a color for each pie piece
    #colors = ["red", "green", "blue", "orange", "yellow"]
    #p = figure(x_range=(-1, 1), y_range=(-1, 1), plot_width=plot_width, plot_height=plot_height)
    #p.wedge(x=0, y=0, radius=1, start_angle=starts, end_angle=ends, color=colors)
    p.annular_wedge(
        0, 0, 0, 400, starts, ends, color=colors,
    )

    # Poner Texto
    inner_radius = 0
    outer_radius = 400
    minr = sqrt(log(.001 * 1E4))
    maxr = sqrt(log(1000 * 1E4))
    a = (outer_radius - inner_radius) / (minr - maxr)
    b = inner_radius - a * maxr
    labels = np.power(10.0, np.arange(-3, 4))
    radii = a * np.sqrt(np.log(labels * 1E4)) + b
    # Posicion media de cada angulo
    halfs= [starts[-1]]+ starts[:-1]
    for i in range(len(halfs)):
        halfs[i] += percents[i] * np.pi

    # Ángulos del texto
    xr = (radii[0]-150) * np.cos(np.array(halfs))
    yr = (radii[0]-150) * np.sin(np.array(halfs))
    label_angle = np.array(halfs)
    for i,angle in enumerate(label_angle):
        if (np.pi / 2) < angle < np.pi+(np.pi/2):
            label_angle[i] += np.pi

    p.text(xr, yr, ['#'+x[0] + ': '+str(x[1]) for x in h_counter], angle=label_angle,
           text_font_size="9pt", text_align="center", text_baseline="middle")

    # Store Components
    pie_chart_resul[0], pie_chart_resul[1] = components(p)


def pie_chart(percents):
    # define starts/ends for wedges from percentages of a circle
    percents = [0, 0.3, 0.4, 0.6, 0.9, 1]
    starts = [p * 2 * pi for p in percents[:-1]]
    ends = [p * 2 * pi for p in percents[1:]]

    # a color for each pie piece
    colors = ["red", "green", "blue", "orange", "yellow"]

    p = figure(x_range=(-2, 2), y_range=(-2, 2))

    p.wedge(x=0, y=0, radius=1, start_angle=starts, end_angle=ends, color=colors)

    return p

def test_graph(df, title='Test Title', x_axis_label='X-Asis-Test', y_axis_label='Y-Asis-Test', plot_width=400, plot_height=400):
    series = group_by_date(df).mean().fillna(0) # fillna para pasar nan values a 0
    nuevo_df = filtrar_df_fecha(df, '2016-02-16', '2016-02-16')
    bseries = buscar_palabra_df(df,'la')
    df2 = df[bseries]
    counter = n_palabras_comun(df, 100)
    #uniq_usuarios_df(df)
    categorias = list(series.keys())
    plot = figure(x_axis_type='datetime', plot_width=400, plot_height=400, x_axis_label='Fecha', y_axis_label='Retweets')#, x_range=categorias
    bar_width = 150000000/len(categorias)
    plot.vbar(categorias, top=list(series.values), width=bar_width, line_color='green', bottom=0)
    plot.toolbar.logo = None
    plot.toolbar_location = None
    #Store Components
    script, div = components(plot)
    return script, div


def n_words_graph(df, n, column, n_words_resul):
    counter = n_palabras_comun(df, n, column=column)
    categorias = [ x[0] for x in counter ]
    top = [ x[1] for x in counter ]
    plot = figure(x_range=categorias, plot_width=400, plot_height=400, x_axis_label='Palabra', y_axis_label='Frecuencia')#, x_range=categorias
    bar_width = 1
    plot.vbar(x=categorias, top=top, width=bar_width, line_color='green', bottom=0)
    plot.toolbar.logo = None
    plot.toolbar_location = None
    #Store Components
    n_words_resul[0], n_words_resul[1] = components(plot)


def locations_graph(list, n, location_resul):
    counter = count_locations(list, n)
    categorias = [ x[0] for x in counter ]
    top = [ x[1] for x in counter ]
    plot = figure( plot_width=400, plot_height=400, y_range=FactorRange(factors=categorias),x_axis_label='Frecuencia')
    plot.hbar(y=categorias, right=top, left=0, height=0.5, line_color='red', fill_color='orange')
    plot.toolbar.logo = None
    plot.toolbar_location = None
    #Store Components
    location_resul[0],location_resul[1] = components(plot)

def linear_plot(df, linear_resul):
    plot_data = group_by_date(df, freq='H', column='')
    plot_data = plot_data.count()

    x_axis_values = plot_data.index.values
    y_axis_values = [x[0] for x in plot_data.values]
    p = figure(x_axis_type='datetime', plot_width=400, plot_height=400, x_axis_label='Fecha', y_axis_label='Tweets')#, x_range=categorias

    # add a line renderer
    p.line(x_axis_values, y_axis_values, line_width=2)
    p.toolbar.logo = None
    p.toolbar_location = None

    linear_resul[0], linear_resul[1] = components(p)



def mean_linear_plot(df, mean_linear_resul):
    plot_data = group_by_date(df, freq='H').mean().fillna(0)

    x_axis_values = list(plot_data.keys())
    y_axis_values = list(plot_data.values)
    p = figure(x_axis_type='datetime', plot_width=400, plot_height=400, x_axis_label='Fecha', y_axis_label='Tweets')#, x_range=categorias

    # add a line renderer
    p.line(x_axis_values, y_axis_values, line_width=2)
    p.toolbar.logo = None
    p.toolbar_location = None

    mean_linear_resul[0], mean_linear_resul[1] = components(p)


def main():
    return

if __name__ == '__main__':
    main()