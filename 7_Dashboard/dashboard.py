# DEPENDENCIES
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px

# DATASET
path = r"D:\IBM Professional Certification\10_Data Science Capstone Project\6_Dashboard\data & files\spacex_launch_dash.csv"
df = pd.read_csv(path, index_col=0) ## Automobile Sales dataset

"""
DATASET DETAILS

A. Columns ->
['Flight Number', 'Launch Site', 'class', 'Payload Mass (kg)',
       'Booster Version', 'Booster Version Category']

B. Original dtypes ->
Flight Number                 int64
Launch Site                  object
class                         int64
Payload Mass (kg)           float64
Booster Version              object
Booster Version Category     object
"""

# APP INSTANCE
app = dash.Dash(__name__)





# MAIN LAYOUT

## App Title
app_title = html.H1(
    children="SpaceX Launch Records Dashboard",
    style=dict(
        fontFamily="times new roman",
        fontWeight="bold",
        fontSize="50px",
        textAlign="center",
        color="#222831"
    )
)

## App Dropdown 1 (Launch Site selection)
    ### options full forms
sites_full_names = {
    "CCAFS LC-40":"Cape Canaveral Launch Complex 40",
    "VAFB SLC-4E":"Vandenberg Space Force Base Space Launch Complex 4 East",
    "KSC LC-39A":"Kennedy Space Center Launch Complex 39A",
    "CCAFS SLC-40":"Cape Canaveral Space Launch Complex 40"
}
    ### options for dropdown 1
drop1_options = [
    dict(label=sites_full_names[str(site)], value=str(site))
    for site in df["Launch Site"].unique()
]
drop1_options.insert(0, dict(label="All Sites", value="All"))
    ### dropdown 1 menu
drop1 = dcc.Dropdown(
    id="launch-site",
    options=drop1_options,
    placeholder="Select Launch site",
    value=None,
    searchable=True,
    style=dict(
        width="100%",
        padding="3px",
        textAlignLast="center",
        fontSize="20px",
        fontFamily="times new roman",
        color="#191919"
    )
)

## App Range slider 1 (Payload Range selector)
    ## slider marks
slider1_marks = {
    k:f"{str(k)} kg"
    for k in range(0, 10001, 1000)
}
slider1 = dcc.RangeSlider(
    id="payload-slider",
    min=0, max=10000, step=1000,
    marks=slider1_marks,
    value=["min_payload", "max_payload"]
)



## Adjust main layout
app.layout = html.Div(
    children=[
        app_title,
        html.Div(
            children=[
                html.H2("Launch Site", style=dict(fontFamily="times new roman", fontSize="18px", textAlign="left")),
                drop1
            ]
        ),
        html.Div(
            html.Div(
                id="plot-render",
                className="plots",
                style=dict(display=None)
            )
        ),
        html.Div(
            children=[
                html.H2("Payload Range (kg)", style=dict(fontFamily="times new roman", fontSize="18px", textAlign="left")),
                slider1
            ]
            
        ),
        html.Div(
            id="scatter-render",
            className="scatter",
            style=dict(display=None)
        )
    ]
)


# APP CALLBACKS

## Callback for rendering Success Pie chart based on selected Launch site

@app.callback(
    Output(component_id="plot-render", component_property="children"),
    [
        Input(component_id="launch-site", component_property="value")
    ]
)
def render_pie_success(site):
    """
    """
    if site is None:
        pass
    elif site == "All":
        # data generation
        df_all = df.copy()
        subset1 = df_all[["Launch Site", "class"]]
        subset1_group = subset1.groupby(["Launch Site"], as_index=False).sum()

        # plotly pie chart
        colors_pie_all = [
            "#FFEC9E", "#9AC8CD",
            "#FA7070", "#B0D9B1"
        ]
        labels_pie_all = {
            "Launch Site":"Launch Site",
            "class":"Total Successful launches",
            
        }
        pie_all_success = px.pie(
            data_frame=subset1_group,
            values="class",
            names=list(sites_full_names.keys()),
            color_discrete_sequence=colors_pie_all,
            labels=labels_pie_all,
            opacity=0.8
        )

        # update traces of pie to add details
        pie_all_success.update_traces(
            marker=dict(
                line=dict(width=1.25, color="#001524")
            ),
            title=dict(
                position="bottom center",
                text=f"Successful Launches from Different Launch Sites",
                font=dict(family="times new roman", size=17)
            ),
            hoverlabel=dict(bgcolor="#EEEEEE", bordercolor="#222831")
        )

        # dcc graph containing the pie
        graph_pie_all_success = dcc.Graph(
            figure=pie_all_success
        )

        return graph_pie_all_success
    else:
        # data generation
        df_site = df[df["Launch Site"] == site]
        subset2 = df_site[["Launch Site", "class"]]
        subset2_group = subset2.groupby(["Launch Site"], as_index=False).value_counts()
        subset2_group["class"] = subset2_group["class"].map(arg={0:"Failure", 1:"Success"})
        subset2_group.rename(columns={"class":"Launch Outcome"}, inplace=True)

        # plotly pie
        colors_class = {"Failure":"#BF3131", "Success":"#90D26D"}
        pie_site_success = px.pie(
            data_frame=subset2_group,
            values="count",
            names="Launch Outcome",
            labels="Legend_title",
            color="Launch Outcome",
            color_discrete_map=colors_class,
            opacity=0.8
        )

        # update traces of pie to add details
        pie_site_success.update_traces(
            marker=dict(
                line=dict(width=1.25, color="#001524")
            ),
            title=dict(
                position="bottom center",
                text=f"Launch Success of {site}",
                font=dict(family="times new roman", size=17)
            ),
            hoverlabel=dict(bgcolor="#EEEEEE", bordercolor="#222831")
            
        )

        # dcc graph containing the pie
        graph_pie_site_success = dcc.Graph(
            figure=pie_site_success
        )

        return graph_pie_site_success



## Callback for rendering Payload-Launch outcome Scatter chart based on selected Launch site

@app.callback(
    Output(component_id="scatter-render", component_property="children"),
    [
        Input(component_id="launch-site", component_property="value"),
        Input(component_id="payload-slider", component_property="value")
    ]
)
def render_scatter_chart(site, payload):
    """

    """
    if site == "All":
        # data generation
        min_payload, max_payload = payload
        data_all = df[
            (df["Payload Mass (kg)"] >= min_payload)
            &
            (df["Payload Mass (kg)"] <= max_payload)
        ].copy()
            ## rename `class` column & it's categories
        data_all["class"] = data_all["class"].map(arg={0:"Failure", 1:"Success"})
        data_all.rename(columns={"class":"Launch Outcome"}, inplace=True)

        # plotly scatter chart
            ## customizations
        colors_scatter_all = {
            "v1.1":"#124076",
            "FT":"#A34343",
            "B4":"#BB8493",
            "B5":"#87A922"
        }
        symbols_scatter_all = {
            "Failure":"x",
            "Success":"circle"
        }
        scatter_all = px.scatter(
            data_frame=data_all,
            x="Payload Mass (kg)",
            y="Launch Outcome",
            color="Booster Version Category",
            color_discrete_map=colors_scatter_all,
            title="Correlation between Payload and Success for All Sites",
            symbol="Launch Outcome",
            symbol_map=symbols_scatter_all
        )

        # update trace for details
        scatter_all.update_traces(
            
        )


        # dcc figure object
        graph_scatter_all = dcc.Graph(
            figure=scatter_all
        )

        return graph_scatter_all
        
    elif site is not None:
        # data generation
        min_payload, max_payload = payload
        data_site = df[
            (df["Payload Mass (kg)"] >= min_payload)
            &
            (df["Payload Mass (kg)"] <= max_payload)
            &
            (df["Launch Site"] == site)
        ].copy()
            ## rename `class` column & it's categories
        data_site["class"] = data_site["class"].map(arg={0:"Failure", 1:"Success"})
        data_site.rename(columns={"class":"Launch Outcome"}, inplace=True)

        # plotly scatter chart
            ## customizations
        colors_scatter_site = {
            "v1.1":"#124076",
            "FT":"#A34343",
            "B4":"#BB8493",
            "B5":"#87A922"
        }
        symbols_scatter_site = {
            "Failure":"x",
            "Success":"circle"
        }
        scatter_site = px.scatter(
            data_frame=data_site,
            x="Payload Mass (kg)",
            y="Launch Outcome",
            color="Booster Version Category",
            color_discrete_map=colors_scatter_site,
            title=f"Correlation between Payload and Success for {str(site)}",
            symbol="Launch Outcome",
            symbol_map=symbols_scatter_site
        )

        # update trace for details
        scatter_site.update_traces(
            
        )


        # dcc figure object
        graph_scatter_site = dcc.Graph(
            figure=scatter_site
        )

        return graph_scatter_site

    else:
        pass
        







# RUN APP
if __name__ == "__main__":
    app.run_server()