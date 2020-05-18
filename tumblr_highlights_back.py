#################################### IMPORT STATEMENTS
# for processing queries
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib import parse
# for web scraping 
import requests
from bs4 import BeautifulSoup
from bs4.element import Tag, NavigableString
from urllib.request import urlopen
import time
# for processing and retreiving data 
from collections import defaultdict
import pytumblr
import json
import re
# for creating the visualizations
import pandas as pd
import networkx as nx
import plotly.graph_objects as go

client = pytumblr.TumblrRestClient('9TRGPe4N17LiyRiZvwlhSRoaEaov0w9sn2ntYqJt3DsP3SDWeZ')

#################################### MAIN FUNCTION
class CorpusWebServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        query = parse.urlsplit(self.path).query
        query_dict = parse.parse_qs(query)
        print('QUERY DICT:', query_dict)
        if self.path == "/":
            self.send_header('Content-type','text/html; charset=utf-8')
            self.end_headers()
            f = open("tumblr_highlights_public.html", encoding="utf-8")
            html = f.read()
            f.close()
            self.wfile.write(html.encode("utf-8"))
        elif 'search' in query_dict: 
            self.send_header('Content-type','text/html; charset=utf-8')
            self.end_headers()
            post_url = query_dict['search'][0]
            viz, date, note_count, tags, len_nodes = reblog_viz(post_url)
            if type(viz) == int:
                if viz == 1:
                    html2 = catch_error("invalid link")
                if viz == 2:
                    html2 = catch_error("too many notes")
                if viz == 3:
                    html2 = catch_error("no reblogs")
                f = open("debug.html", "w")
                f.write(html2)
                f.close()
                self.wfile.write(html2.encode("utf-8"))
                print("finished processing error")
            else:
                viz.write_html("reblog_struc.html", include_plotlyjs = 'cdn')
                viz_html = open('reblog_struc.html').read()
                html2 = insert(viz_html, date, note_count, tags, len_nodes)
                f = open("debug.html", "w")
                f.write(html2)
                f.close()
                self.wfile.write(html2.encode("utf-8"))
                print('finished viz')

#################################### MY FUNCTIONS
def catch_error(type_of_error):
    """in one of three scenarios return error message"""
    f = open("tumblr_highlights_public.html", encoding = "utf-8")
    html = f.read()
    f.close()
    if type_of_error == "invalid link":
        html = html.replace("</form>", "</form><br><br><p> Oops, this link does not seem to exist. Try again? </p>")
    elif type_of_error == "too many notes": 
        html = html.replace("</form>", "</form><br><br><p> This post is too popular to visualize! Try again with a post that has less than 7500 notes. </p>")
    elif type_of_error == "no reblogs":
        html = html.replace("</form>", "</form><br><br><p> Oops, this post seems to have no reblogs. Try again? </p>")
    return html

def insert(viz, date, note_count, tags, len_nodes):
    """given all appropriate information, insert into webpage and return completed html"""
    f = open("tumblr_highlights_public.html", encoding = "utf-8")
    html = f.read()
    f.close()
    html = html.replace("</form>", "</form><br><br><p>Date posted: <b>" + str(date) + "</b> &emsp;	&emsp; Total notes: <b>" + str(note_count) + "</b> 	&emsp; 	&emsp; Total reblogs: <b>" + str(len_nodes) + "</b><br> Tags: <i>" + str(tags) +"</i><br><br>" + str(viz) + "</p>")
    return html

def reblog_viz(post_url):
    """given a post url scrape all the notes and create a visualization of the reblog structure"""
    
    # check url and get post metadata, return errors if necessary
    try:
        user_url = post_url.split("/post/")[0].split("://")[1]
        user_url_full = post_url.split("/post/")[0]
        post_id = post_url.split("/")[4]
        post = client.posts(user_url, id = post_id, reblog_info=True, notes_info=True)
        slug = post['posts'][0]['slug']
        date = post['posts'][0]['date'].split(" ")[0]
        tags = ", ".join(["#" + tag for tag in post['posts'][0]['tags']]) 
        note_count = post['posts'][0]['note_count']
        print("Date posted:", date, "\tTotal notes count:", note_count, "\nTags:", tags)
    except:
        return 1, 2, 3, 4, 5
    if note_count > 7500:
        return 2, 3, 4, 5, 6
    
    # make visualization, return errors if necessary
    try:
        notes_url = get_notes_url(post_url)
        reblog_dict = process_post(notes_url)
    except:
        reblog_dict = process_single_post(post_url)
    if reblog_dict == 3:
        return 3, 4, 5, 6, 7
    viz, len_nodes = make_reblog_plot(reblog_dict)
    return viz, date, note_count, tags, len_nodes

def process_single_post(posturl):
    """takes a post URL, processes all its notes and gathers them into a dict, 
    returns the dict and prints the number of notes"""
    
    # setting things up
    reblog_dict = defaultdict(list)
    r = requests.get(posturl, 'html')
    soup = BeautifulSoup(r.text)
    text = soup.get_text()
    words = text.split()

    # update the reblog dict
    for i in range(1, len(words)):
        if words[i] == 'reblogged': 
            reblog_dict[words[i+3]].append(words[i-1])
    print("The current length of the reblog dict is", len(reblog_dict))
    if len(reblog_dict) == 0:
        return 3
        
    # reverse items to keep list in chronological order
    for key, value in reblog_dict.items():
        reblog_dict[key] = list(reversed(value))
        
    return reblog_dict

def get_notes_url(post_url):
    """given a post url as a string return the full notes url"""
    
    # grab the user's URL from the post URL
    user_url = post_url.split("/post/")[0]
    print("The user URL is", user_url)
    
    # find and append the notes URL to the user URL
    notes_reg = "(open\('GET',')(/notes/[0-9]*/[A-Za-z0-9]*)(\?from_c=)"
    r = requests.get(post_url, 'html')
    soup = BeautifulSoup(r.text)
    mat2 = re.search(notes_reg, str(soup))
    return user_url + mat2.group(2)

def make_reblog_plot(reblog_d, reblog_id = None, save = False):
    """given a reblog_dict make and optionally save the entire graph (used for testing)"""

    # create dataframe with reblog structure
    all_source, all_dest = [], []
    for key, value in reblog_d.items():
        for v in value:
            all_source.append(key)
            all_dest.append(v)

    reblog_df = pd.DataFrame({'source': all_source, 'dest': all_dest})
    print("Shape of reblog dataframe:", reblog_df.shape)

    # create graph and add nodes
    sources = list(reblog_df["source"].unique())
    dests = list(reblog_df["dest"].unique())
    node_list = list(set(sources + dests))
    print("Number of nodes:", len(node_list))
    G = nx.Graph()
    for i in node_list:
        G.add_node(i)
        
    for i, j in reblog_df.iterrows():
        G.add_edges_from([(j["source"], j["dest"])])
    
    # add positions using spring layout 
    pos = nx.spring_layout(G, dim = 3, k = .5, iterations = 50)
    for n, p in pos.items():
        G.node[n]['pos'] = p
        
    # create 3D scatter plot 
    edge_trace = go.Scatter3d(
    x=[],
    y=[],
    z=[],
    line=dict(width=0.5,color='#888'),
    hoverinfo='none',
    mode='lines')
    
    for edge in G.edges():
        x0, y0, z0 = G.node[edge[0]]['pos']
        x1, y1, z1 = G.node[edge[1]]['pos']
        edge_trace['x'] += tuple([x0, x1, None])
        edge_trace['y'] += tuple([y0, y1, None])
        edge_trace['z'] += tuple([z0, z1, None])
        
    node_trace = go.Scatter3d(
        x=[],
        y=[],
        z=[],
        text=[],
        mode='markers',
        hoverinfo='text',
        marker=dict(
            showscale=True,
            colorscale='Plasma',
            reversescale=False,
            color=[],
            size=5,
            colorbar=dict(
                thickness=10,
                title='Number of Reblogs',
                xanchor='left',
                titleside='right'
            ),
            line=dict(width=0)))
    
    for node in G.nodes():
        x, y, z = G.node[node]['pos']
        node_trace['x'] += tuple([x])
        node_trace['y'] += tuple([y])
        node_trace['z'] += tuple([z])
        
    for node, adjacencies in enumerate(G.adjacency()):
        node_trace['marker']['color']+=tuple([len(adjacencies[1])])
        node_info = "reblogged " + str(len(adjacencies[1])) + " times from " + adjacencies[0] 
        node_trace['text']+=tuple([node_info])
    
    # create figure 
    print("Creating figure...")
    fig = go.Figure(data=[edge_trace, node_trace],
             layout=go.Layout(
                title='',
                titlefont=dict(size=16),
                showlegend=False,
                hovermode='closest',
                paper_bgcolor = "#E5ECF6", 
                hoverdistance = 100,
                scene = dict(xaxis_showspikes=False,
                             yaxis_showspikes=False,
                            zaxis_showspikes=False,
                            xaxis_showgrid = False,
                            yaxis_showgrid = False,
                            zaxis_showgrid = False,
                            xaxis_showticklabels = False,
                            yaxis_showticklabels = False,
                            zaxis_showticklabels = False,
                            xaxis_zeroline = False,
                            yaxis_zeroline = False,
                            zaxis_zeroline = False,
                            xaxis_title = "",
                            yaxis_title = "",
                            zaxis_title = ""),
                margin=dict(b=10,l=10,r=10,t=10))) 
    
    # write to file
    if save:
        fig.write_html("reblog_graph_" + str(reblog_id) + ".html", include_plotlyjs = 'cdn')
        print("File saved to HTML!")
    
    return fig, len(node_list)

def process_post(posturl):
    """takes a post URL, processes all its notes and gathers them into a dict, 
    returns the dict and prints the number of notes"""
    
    # setting things up
    reblog_dict = defaultdict(list)
    notes_count = 0
    new_url_reg = "([A-Za-z0-9]*)(\?from_c=[0-9]*)(',true)"
    
    # initial url 
    url = posturl 
    show_more = True
    
    # while there are more notes to show...
    while show_more:
    
        # grab text from current url 
        time.sleep(10)
        print("Sleeping now...")
        r = requests.get(url, 'html')
        soup = BeautifulSoup(r.text)
        
        # look at the text, update the notes count, and check if we're at the end yet
        text = soup.get_text()
        words = text.split()
        notes_count += words.count("this")
        print('The current notes count is', notes_count, ", new notes:", words.count("this"))

        # update the reblog dict
        for i in range(1, len(words)):
            if words[i] == 'reblogged': 
                reblog_dict[words[i+3]].append(words[i-1])
        print("The current length of the reblog dict is", len(reblog_dict))
        
        # grab the next url 
        mat = re.search(new_url_reg, str(soup))
        if mat is None:
            show_more = False
            print("Almost done!")
            break
        url = posturl + mat.group(2)
        print("The next URL is", url)

    if len(reblog_dict) == 0:
        return 3
        
    # reverse items to keep list in chronological order
    for key, value in reblog_dict.items():
        reblog_dict[key] = list(reversed(value))
        
    print("The final notes count is", notes_count)
    return reblog_dict

#####################################################

if __name__ == "__main__":
    http_port = 9985
    server = HTTPServer(('localhost', http_port),  CorpusWebServer)
    server.serve_forever()