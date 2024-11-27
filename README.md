# Tools to support learning french

Don't know where this is going yet. I'm learning French and thought I 
might need some thingies to support me. Like grabbing all words from 
the transcript of a podcast on [inner french](https://innerfrench.com/). 

So I can do who knows?

## Install

```
git clone git@github.com:jvermeir/french_tools.git
cd french_tools/
python3 -m venv venv
source venv/bin/activate
```

Create a folder named `secrets` and a file named `userdata.txt`. Open the inner French site and log in. Find a cookie with a name like `wordpress_logged_in_`
and copy its value in the userdata.txt file. This is necessary to access the site as a logged-in user.

## Usage

First create a file named `urls.txt` in the data folder. This file should contain one 
url per line. Each url should point to a podcast page on the inner French site.

Now run `synchronize` to download the transcripts of the podcasts listed in `urls.txt`. Files
won't be reloaded, so if you want to reload a file, delete it first. The result of this step
is a file in the data folder. The name is the episode number of the podcast, with a `.json` extension.
Each json file contains the url, the contents of the page for the podcast and a list of words found in the 
transcript.

Then run `analyze` to create a list of all words found in the transcripts. This list is stored in a file named `first_occurrences.json` in the data folder.
This file lists the words that occur for the first time in a particular episode. 

`reload` will parse the data downloaded using the json file for each episode, and re-create the list of words found
in the text. This might be useful if you make changes to the algorithm to extract words from the text and don't want
to download the data again.