import numpy as np
if __package__ is None:
    import sys
    from os import path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

import conversation
import parsers

import collections
from bokeh.plotting import figure, output_file, show, ColumnDataSource
from bokeh.palettes import brewer
from bokeh.models import HoverTool, BoxZoomTool, ResetTool, PanTool, ResizeTool, WheelZoomTool

hover = HoverTool(tooltips=[
    ("index", "$index"),
    ("(x,y)", "(@dates, $y)"),
    # ("Person", "@label"),
])

import itertools
messages = collections.defaultdict(list)
for contact, text in parsers.Whatsapp("../Whatsapp"):
    messages[contact].append(text)
for contact in messages:
    messages[contact] = list(itertools.chain.from_iterable(messages[contact]))
    messages[contact].sort(key=lambda x: x['timestamp'])

TOOLS = [
    hover,
    BoxZoomTool(),
    ResetTool(),
    PanTool(),
    ResizeTool(),
    WheelZoomTool()
]

# output to static HTML file
output_file("lengths.html", title="Chat lengths")

p = figure(width=800, height=500, x_axis_type="datetime", tools=TOOLS)

colors = brewer["Spectral"][len(messages)]

for i, k in enumerate(messages):
    days = conversation.Conversation(messages[k]).days()
    dates = sorted(days.keys())
    lengths = np.array([len(days[key]) for key in dates])
    x_dates = np.array(sorted(days.keys()), dtype=np.datetime64)
    source = ColumnDataSource(
        data=dict(
            x=x_dates,
            y=lengths,
            dates=dates,
            # label=[k]*len(dates),
        ))
    p.line('x', 'y', source=source, color=colors[i], line_width=2)
    p.circle('x', 'y', source=source, color=colors[i], legend=k, size=8)

# NEW: customize by setting attributes
p.title = "Per day chat lengths"
p.legend.orientation = "top_left"
p.grid.grid_line_alpha = 0
p.xaxis.axis_label = 'Date'
p.yaxis.axis_label = 'Amount talked'
p.ygrid.band_fill_color = "olive"
p.ygrid.band_fill_alpha = 0.1

# show the results
show(p)
