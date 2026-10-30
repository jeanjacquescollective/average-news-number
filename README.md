# Average News Number

Collects every number (digits *and* written-out Dutch/English numbers like "honderd" or
"twenty-one") in the headlines on the [VRT NWS](https://www.vrt.be/vrtnws/nl/) front page, and
publishes the **mean** and **median** number of each day. Only the headlines count: the site shows
nothing from the article texts.

- **Front-page headlines** (the main number): each headline counts once, on the day it first appears
  on the front page. Liveblogs that run for days get a new headline with every development; each new
  headline counts again.
- **Full articles**: the scraper still stores headline + body of every article (in `data/days`), but
  the site does not use them.

The site follows the house style of [Jean-Jacques Collective](https://www.jeanjacquescollective.org/):
black and white, Helvetica, and big outlined Georgia titles that fill in on hover. It is in Dutch with an
NL/EN switch, and black unless the reader switches to white (Zwart → Wit); both choices are remembered
per visitor. Pages (all accept `?date=YYYY-MM-DD`):

- `index.html` (**Het getal**): yesterday's headline mean (big), the median, and an ⓘ button that
  lists every headline of that day with the numbers found in it.
- `charts.html` (**Grafieken**): every headline number of the day over time with the mean and median,
  the headline numbers per order of magnitude, their first digits next to Benford's law, and the mean,
  median and count per day.
- `financial-time.html` (**Financial Time**): every amount of money in the day's front page headlines,
  marked as lost/negative (gestolen, verlies, boete, kost…) or gained/positive (winst, budget, in beslag
  genomen, gekregen…) by the nearest signal word in the headline; without one it counts as positive.
  With the totals, the balance, and charts per day.
- `history.html` (**Geschiedenis**): highest/lowest mean, highest/lowest median, the biggest and
  smallest headline number ever found, and a table of all days.

## How it works

```
scraper/scrape.py      finds new articles, extracts numbers, updates data/
scraper/numextract.py  the number extraction (see the docstring for the exact rules)
scraper/money.py       amounts of money and whether they were lost or gained (see the docstring)
data/days/YYYY/*.json  every headline and article with the numbers found in it, one file per day
data/summary.json      per-day stats; the website reads this
data/state.json        which headlines and articles were already processed
site/                  the static website (system fonts: Helvetica and Georgia)
```

Each run (every 10 minutes on GitHub Actions):

1. Reads the headlines on the front page and stores every headline it has not seen before.
   (A headline that is on the front page for less than the 10 minutes between runs can be missed.)
2. Collects article links from the Atom feed (~last 6 hours), the
   [net binnen](https://www.vrt.be/vrtnws/nl/net-binnen/) page (~last 24 hours), the homepage, and the
   weekly sitemaps (last 8 days). Overlapping sources mean an article is caught even if runs are
   skipped for hours.
3. Skips anything already processed. Each article is processed **once**, using its text at that moment.
4. Reads the full text from the article's own `.rss.xml` feed (or the page itself for liveblogs),
   extracts the numbers from the headline and body, and files the article under its publication day
   (Belgian time).
5. Recomputes `data/summary.json`. A day is shown as "complete" once it is over in Belgium. If an
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

### The first run

When `data/` is empty, the first run also collects the previous 14 days (about 30 minutes):

- **Articles** from the weekly sitemaps. The current week's sitemap only appears once the week is
  over, so the days before yesterday start incomplete; later runs fill them in automatically as
  soon as that sitemap exists.
- **Front page headlines** from archived copies of the front page on
  [archive.org](https://web.archive.org/) (at most one per hour). Days without archived copies get
  no headline number; headlines that were on the front page only briefly may be missing.

`--since YYYY-MM-DD` picks another start date (up to 30 days back). To start over, delete `data/`.
