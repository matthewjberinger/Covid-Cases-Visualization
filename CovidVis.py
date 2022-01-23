


#import modules
import pandas as pd
import numpy as np


from bokeh.models import *
from bokeh.plotting import *
from bokeh.io import *
from bokeh.tile_providers import *
from bokeh.palettes import *
from bokeh.transform import *
from bokeh.layouts import *
from bokeh.palettes import *



# Convert from lat/lan to web mercator


def wgs84_to_web_mercator(df, lon, lat):
    """Converts decimal longitude/latitude to Web Mercator format"""
    k = 6378137
    df["x"] = df[lon] * (k * np.pi/180.0)
    df["y"] = np.log(np.tan((90 + df[lat]) * np.pi/360.0)) * k
    return df



def main():


    month = 0
    day = 0
    year = 0

    print("Welcome to the covid case visualizer")

    while year != 2020 and year != 2021 and year != 2022:
        year = int(input("Enter the year: "))

    if year == 2022:
        month = 1

    else:
        while month < 1 or month > 12:
            month = int(input("Enter the month (as a number): "))

    if month == 1 and year == 2022:
        while day < 1 or day > 21:
            day = int(input("Enter the day: "))

    elif year == 2020 and month == 1:
        while day < 21 or day > 31:
            day = int(input("Enter the day: "))

    elif month == 1 or month == 3 or month == 5 or month == 7 or month == 8 or month == 10 or month == 12 :
        while day < 1 or day > 31:
            day = int(input("Enter the day: "))

    elif month == 4 or month == 6 or month == 9 or month == 11:
        while day < 1 or day > 30:
            day = int(input("Enter the day: "))

    else:
        while day < 1 or day > 28:
            day = int(input("Enter the day: "))

    date = str(month) + "/" + str(day) + "/" + str(year)

    print(date)

    cases_df = pd.read_csv(
        'https://raw.githubusercontent.com/matthewjberinger/Covid-Cases-Visualization/main/United_States_COVID-19_Cases_and_Deaths_by_State_over_Time.csv')
    cases_df = cases_df.loc[cases_df['submission_date'] == date]  # filter out only the one date



    # Convert to different data types
    cases_df['Latitude'] = cases_df['Latitude'].astype('float')
    cases_df['Longitude'] = cases_df['Longitude'].astype('float')
    cases_df['tot_cases'] = cases_df['tot_cases'].astype('int64')
    cases_df['cases_per_capita'] = cases_df['cases_per_capita'].astype('float')
    cases_df2 = cases_df.loc[1:52]

    df = wgs84_to_web_mercator(cases_df, 'Longitude', 'Latitude')


    #Make zoom scale for the map
    scale = 10000
    x = df['x']
    y = df['y']

    # The range for the map extents is derived from the lat/lon fields. This way the map is automatically centered on the plot elements.

    x_min = int(x.mean() - (scale * 350))
    x_max = int(x.mean() + (scale * 350))
    y_min = int(y.mean() - (scale * 350))
    y_max = int(y.mean() + (scale * 350))

    # Defining the map tiles to use. I use OSM, but you can also use ESRI images or google street maps.

    tile_provider = get_provider(OSM)

    # Set output
    output_file(filename="covid_cases.html", title="US Covid Cases")

    #Set up the figure

    plot = figure(
        title='United States Covid Cases ' + date,
        match_aspect=True,
        tools='wheel_zoom,pan,reset,save',
        x_range=(x_min, x_max),
        y_range=(y_min, y_max),
        x_axis_type='mercator',
        y_axis_type='mercator',

    )

    #Set up the colors
    palette = RdBu[11]
    color_mapper = linear_cmap(field_name='cases_per_capita', palette=palette, low=cases_df['cases_per_capita'].min(),
                               high=cases_df['cases_per_capita'].max())

    plot.grid.visible = True

    map = plot.add_tile(tile_provider)
    map.level = 'underlay'

    plot.xaxis.visible = False
    plot.yaxis.visible = False

    # Bubble Map

    def bubble_map(plot, df, radius_col, state, cases, scale, leg_label='Bubble Map'):
        radius = []
        for i in df[radius_col]:
            radius.append(i * scale * 200)

        df['radius'] = radius

        source = ColumnDataSource(df)
        c = plot.circle(x='x', y='y', color=color_mapper, source=source, size=1, fill_alpha=0.4, radius='radius',
                        legend_label=leg_label, hover_color='red')

        state_label = '@' + state
        cases_label = '@' + cases

        circle_hover = HoverTool(tooltips=[('State:', state_label), ('Cases:', cases_label)],
                                 mode='mouse', point_policy='follow_mouse', renderers=[c])
        circle_hover.renderers.append(c)
        plot.tools.append(circle_hover)


        plot.legend.location = "top_right"
        plot.legend.click_policy = "hide"


    # Create the bubble map
    bubble_map(plot=plot,
               df=cases_df,
               radius_col='cases_per_capita',
               leg_label='Cases Per Capita',
               state='state',
               cases='tot_cases',
               scale=scale)

    color_bar = ColorBar(color_mapper=color_mapper['transform'],
                         formatter=NumeralTickFormatter(format='0.0[0000]'),
                         label_standoff=13, width=8, location=(0, 0))
    # Set color_bar location
    plot.add_layout(color_bar, 'right')


    save(plot)


main()