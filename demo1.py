import secrets
from unicodedata import name
import pandas as pd
import dash
from dash import dcc, html, Input, Output, dash_table
import yfinance as yf
from dash import dash_table
import dash_bootstrap_components as dbc
import plotly.express as px
import requests
from bs4 import BeautifulSoup


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])


def gettickers():
    # Fetch the webpage
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    res = requests.get(url)

    # Parse the webpage with BeautifulSoup
    soup = BeautifulSoup(res.text, 'html.parser')

    # Find the table with the list of tickers and extract the tickers
    table = soup.find('table', {'class': 'wikitable sortable'})
    tickers = [row.find_all('td')[0].text.strip()
               for row in table.find_all('tr')[1:]]
    return tickers


available_Stocks = gettickers()

app.layout = dbc.Container([
    dbc.Row(
        dbc.Col(
            html.H1("S&P 500 Stocks View"),
            width={"size": 6, "offset": 3},
            style={"text-align": "center", "margin-top": "50px"}
        )
    ),
    html.Div([
        html.Div([
            dcc.Dropdown(
                id='demo-dropdown',
                options=[{'label': k, 'value': k}
                         for k in available_Stocks]
            ),
            html.Hr(),
            dash_table.DataTable(id='display-selected-values', page_current=0,
                                 page_size=10, style_table={'overflowX': 'auto'})
        ], className="col-6 mt-5 ml-auto"),
        html.Div([
            dcc.Graph(id='stock-graph')
        ], className="col-6 mt-5"),
        html.Div(className="w-100"),
        html.Div([
            dcc.Graph(id='graph-div3')
        ], className="col-6 mt-5"),
        html.Div([
            dcc.Graph(id='graph-div4')
        ], className="col-6 mt-5")
    ], className="row")
])


@app.callback(
    Output('display-selected-values', 'data'),
    Input('demo-dropdown', 'value')
)
def update_output(value):
    # print(value)
    df_chart = yf.download(value, '2006-01-01', '2023-04-25')
    df_chart = df_chart.reset_index()
    df_chart['Date'] = pd.to_datetime(
        df_chart['Date']).dt.strftime('%Y-%m-%d')
    # print(df_chart[:10])
    # print(type(df_chart))
    return df_chart.to_dict('records')


@app.callback(
    Output('stock-graph', 'figure'),
    Input('display-selected-values', 'data')
)
def update_graph(data):
    if data:
        df = pd.DataFrame(data)
        fig = px.line(df, x="Date", y="Close")
        return fig
    else:
        return {}


@app.callback(
    Output('graph-div3', 'figure'),
    Input('display-selected-values', 'data')
)
def update_graph_div3(data):
    if data:
        df = pd.DataFrame(data)
        fig = px.area(df, x='Date', y='Close')
        return fig
    else:
        return {}


@app.callback(
    Output('graph-div4', 'figure'),
    Input('display-selected-values', 'data')
)
def update_graph_div4(data):
    if data:
        df = pd.DataFrame(data)
        fig = px.density_heatmap(df, x='Date', y='Volume')
        return fig
    else:
        return {}


if __name__ == '__main__':
    app.run_server(debug=True)
