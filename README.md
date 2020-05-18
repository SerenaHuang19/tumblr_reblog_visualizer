# Tumblr Reblog Visualizer

##### _A tool to visualize the reblogs of tumblr posts!_

Ever wonder how a post spreads across the microblogging site tumblr? As someone who's used tumblr for the last 5+ years, this question has certainly crossed my mind, so I decided to build this tool to interactively visualize the reblogs of a tumblr post. Input the URL of any<sup>[1]</sup> tumblr post to create an interactive 3D network graph, where the nodes are tumblr users and the vertices between nodes show the reblogs of a post. 

### Examples 

Check out some examples of reblog structures [here](languageramblings.tumblr.com/reblog_viz), using three posts that I've picked from my tumblr, [languageramblings](languageramblings.tumblr.com), where I post about fun language-y and linguisticky things. 

More complex examples with the most popular posts on my tumblr are available [here](https://github.com/SerenaHuang19/tumblr_reblog_visualizer/blob/master/tumblr_highlights_manual.html), although be warned that it's a much larger file as the largest network graphs have 1000+ nodes! 

### Technical Details and Tools

* **the tumblr API:** to grab post metadata, including post date, total number of notes, and tags
* **BeautifulSoup:** to scrape the post's notes (likes + reblogs)
* **Networkx:** to build a network graph 
* **plotly:** to create an interactive 3D visualization
* **HTML / CSS:** to create the frontend 
* **Python:** for all backend operations

<sup>[1]</sup> Almost any:

* the post URL must be a valid link

* it should have at least one reblog to visualize

* the total number of notes should not exceed 7500 for speed / efficiency reasons
