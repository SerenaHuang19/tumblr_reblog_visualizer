# Tumblr Reblog Visualizer

_A tool to visualize the reblogs of tumblr posts!_

Ever wonder how a post spreads across the microblogging site tumblr? As someone who's used tumblr for the last 5+ years, this question has certainly crossed my mind, so I decided to build this tool to interactively visualize the reblogs of a tumblr post. Input the URL of any[1] tumblr post to create an interactive 3D network graph, where the nodes are tumblr users and the vertices between nodes show the reblogs of a post. 

[1] Almost any:

* the post URL must be a valid link

* it should have at least one reblog to visualize

* the total number of notes should not exceed 7500 for speed / efficiency reasons

### Examples 

Check out some examples of reblog structures [here](languageramblings.tumblr.com/reblog_viz), using three posts that I've picked from my tumblr, [languageramblings](languageramblings.tumblr.com), where I post about fun language-y and linguisticky things. 

More complex examples with the most popular posts on my tumblr are available [here](), although be warned that it's a much larger file as the largest network graphs have 1000+ nodes! 

### Technical Details 

* the tumblr API: to grab post metadata, including post date, total number of notes, and tags
* BeautifulSoup: to scrape the post's notes (likes + reblogs)
* Networkx: to build a network graph 
* plotly: to create an interactive 3D visualization
* HTML / CSS: creating the frontend 
* Python: all backend operations
