import json
import os

import networkx as nx
import yfinance as yf
from tqdm import tqdm


def get_ticker_list(tickers):
    """Gets ticker list from dict key.

    Args:
        tickers (list/None): List of tickers or None if no tickers found.

    Returns:
        list: tickers 
    """
    temp_tics = tickers if isinstance(tickers, list) else []
    return [tic_dict['ticker'] for tic_dict in temp_tics]


def get_adj_list(folder='./article-parsed/short-ideas/'):
    """Creates adjacency list from folder of article jsons. Data not in repo

    Args:
        folder (str, optional): Folder for article data. Defaults to './article-parsed/short-ideas/'.
    """
    files = os.listdir(folder)
    adj_list = ""
    for file in files:
        with open(folder+file, 'r') as f:
            data = json.load(f)
        p_tics = get_ticker_list(data['primary_tickers'])
        s_tics = get_ticker_list(data['all_tickers'])
        tickers = p_tics + s_tics
        if len(tickers) > 1:
            adj_list += ' '.join(tickers)
            adj_list += '\n'

    with open('SA_adj_list.txt', 'w') as f:
        f.write(adj_list)


def write_node_data(G):
    """Function that fetches data for nodes from yfinance API. Creates json from data.

    Args:
        G (nx.graph): SA graph
    """
    node_data = {}
    # this process takes several hours
    tickers = list(G.nodes)
    for ticker in tqdm(tickers):
        if ticker in node_data:
            continue
        node_data[ticker] = yf.Ticker(ticker).info

    with open('SA_node_data.json', 'w') as outfile:
        json.dump(node_data, outfile)


def set_node_attrs(G, node_data):
    """Sets node attributes in graph.

    Args:
        G (nx.graph): Mutable SA graph
        node_data (dict): Node data from yfinance
    
    Returns:
        nx.graph: SA graph with node attributes 
    """
    node_to_sector = {key: val.get('sector') for key, val in node_data.items()}
    nx.set_node_attributes(G, node_to_sector, 'sector')

    node_to_mcap = {key: val.get('marketCap') for key, val in node_data.items()}
    nx.set_node_attributes(G, node_to_mcap, 'market_cap')

    node_to_ebitda = {key: val.get('ebitda') for key, val in node_data.items()}
    nx.set_node_attributes(G, node_to_ebitda, 'ebitda')

    return G


def remove_no_data_nodes(G):
    """Removes all nodes with any None attributes

    Args:
        G (nx.graph): SA graph with node attributes

    Returns:
        nx.graph: SA graph with no missing data
    """
    nodes_with_no_data = [
        node for node, node_attrs in G.nodes(data=True)
        if None in list(node_attrs.values())
    ]

    for node_to_remove in nodes_with_no_data:
        G.remove_node(node_to_remove)
    
    return G


def remove_separated_nodes(G):
    giant_component = max(nx.connected_components(G), key=len)
    return G.subgraph(giant_component)


if __name__ == '__main__':
    # skip fetching data, as some data is not included in repo
    G = nx.read_adjlist('SA_adj_list.txt')
    with open('SA_node_data.json', 'r') as f:
        node_data = json.load(f)
    G = set_node_attrs(G, node_data)
    G = remove_no_data_nodes(G)
    G = remove_separated_nodes(G)
    nx.write_gexf(G, "SA.gexf")
