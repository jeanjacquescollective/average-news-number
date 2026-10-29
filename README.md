# Average News Number

Reads every new article on [VRT NWS](https://www.vrt.be/vrtnws/nl/), collects every number in it
(digits *and* written-out Dutch/English numbers like "honderd" or "twenty-one"), and publishes the
**mean** and **median** number of each day.

- `index.html`: yesterday's mean (big), the median, and an ⓘ button that lists every article of that day
  with the numbers found in it. `?date=YYYY-MM-DD` shows any other day.
- `history.html`: highest/lowest mean, highest/lowest median, the biggest and smallest number ever
  found, and a table of all days.

## How it works

```
scraper/scrape.py      finds new articles, extracts numbers, updates data/
scraper/numextract.py  the number extraction (see the docstring for the exact rules)
data/days/YYYY/*.json  every article with the numbers found in it, one file per day
data/summary.json      per-day stats; the website reads this
data/state.json        which articles were already processed
site/                  the static website
```

Each run (every 10 minutes on GitHub Actions):

1. Collects article links from the Atom feed (~last 6 hours), the
   [net binnen](https://www.vrt.be/vrtnws/nl/net-binnen/) page (~last 24 hours), the homepage, and the
   weekly sitemaps (last 8 days). Overlapping sources mean an article is caught even if runs are
   skipped for hours.
2. Skips anything already processed. Each article is processed **once**, using its text at that moment.
3. Reads the full text from the article's own `.rss.xml` feed (or the page itself for liveblogs),
   extracts the numbers from the headline and body, and files the article under its publication day
   (Belgian time).
4. Recomputes `data/summary.json`. A day is shown as "complete" once it is over in Belgium. If an
   article from an earlier day turns up late (e.g. via the sitemaps), that day's stats update.

Only standard-library Python 3.11+ is needed; there are no dependencies.

## Setup on GitHub

1. Create a **public** GitHub repository and push this folder to its `main` branch.
   (Public, because Pages is free there and Actions minutes are unlimited. A run every 10 minutes
   adds up to roughly 4,000+ minutes a month, which is more than the free private quota.)
2. **Settings → Pages → Build and deployment → Source: GitHub Actions.**
3. **Settings → Actions → General → Workflow permissions: Read and write permissions.**
4. **Actions → Scrape and publish → Run workflow** once to start. After that it runs every 10 minutes
   and redeploys the site whenever there is a new article.

The site will be at `https://<your-user>.github.io/<repo-name>/`.

## Running locally

```sh
python -m unittest discover -s tests   # tests for the number extraction
python scraper/scrape.py               # one scrape run; updates data/
```

To preview the site, assemble it the way the workflow does and serve it:

```sh
mkdir -p _site/data && cp -r site/. _site/ && cp -r data/days data/summary.json _site/data/
python -m http.server -d _site 8000
```

On the very first run, `--since YYYY-MM-DD` starts the history earlier (up to 30 days back), using
the weekly sitemaps to find older articles.
