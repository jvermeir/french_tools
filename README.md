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