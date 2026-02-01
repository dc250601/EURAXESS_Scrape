# EURAXESS Job Scraper

A small Python scraper for [EURAXESS](https://euraxess.ec.europa.eu/jobs/search) job search. It uses Selenium to apply filters, paginate through results, and export job listings (title, country, link, date posted) to a CSV file.

---

## Features

- **Filtered search** — Apply Research Field, Academic Level, and other site filters before scraping.
- **Pagination** — Automatically follows “Next” and collects jobs from all result pages.
- **CSV export** — Saves Title, Country, Link, date_posted, and a derived JOB ID column.
- **Configurable delays** — Tune wait times to avoid rate limits and flaky page loads.

---

## Requirements

- Python 3.7+
- Chrome browser (for Selenium/ChromeDriver)

Install dependencies:

```bash
pip install selenium pandas tqdm webdriver-manager
```

Or use a `requirements.txt`:

```text
selenium
pandas
tqdm
webdriver-manager
```

Then: `pip install -r requirements.txt`

---

## Quick Start

1. Install dependencies (see above).
2. Run the scraper with defaults (filters and output file are set in `main.py`):

```bash
python main.py
```

3. Optional: set output file and delays:

```bash
python main.py --output my_jobs.csv --MicroDelay 1 --ShortDelay 2 --LongDelay 10
```

Output is written to `job_listings.csv` by default (or the name you pass to `--output`).

---

## How the Filters Work

The scraper uses the EURAXESS search page filters. In code, each filter is identified by its **label** (the text shown next to the filter on the page) and a **list of option names** (the exact text of the checkboxes you want to select).

### Existing filters in `main.py`

- **Research Field** — Options like `"Computer science"`, `"Physics"`, `"Astrophysics"`, etc.
- **Academic Level** — Options like `"Research Support Positions"`, `"PhD Positions"`, `"Other Positions"`.

Filter logic lives in `util.add_filters()`: it finds the filter by label, opens it, clicks each option in your list, closes the dropdown, then clicks “Apply filters”.

### Using different filter options

To **narrow or broaden** results, edit the lists in `main.py` and keep the **exact option text** as shown on the EURAXESS website.

**Example — only Computer science and PhDs:**

```python
research_fields = ["Computer science", "Computer science other", "Computer technology"]
Academic_levels = ["PhD Positions"]

util.add_filters(config, driver, wait, "Research Field", research_fields)
util.add_filters(config, driver, wait, "Academic Level", Academic_levels)
```

**Example — many research fields, all academic levels:**

```python
research_fields = [
    "Computer science", "Computer science other", "Computer technology",
    "Physics", "Physics other", "Applied physics", "Astrophysics", "Computational physics",
    "Mathematics", "Statistics"
]
Academic_levels = ["Research Support Positions", "PhD Positions", "Other Positions"]

util.add_filters(config, driver, wait, "Research Field", research_fields)
util.add_filters(config, driver, wait, "Academic Level", Academic_levels)
```

**Important:** Option names must match the site exactly (including spaces and capitalization). If a checkbox isn’t found, check the browser on [EURAXESS jobs search](https://euraxess.ec.europa.eu/jobs/search): open the filter and copy the label text.

---

## Tutorial: Changing the Code for Desired Results

### 1. Change the output file

- **From the command line:**  
  `python main.py --output path/to/my_listings.csv`

- **In code:**  
  In `main.py`, the default is set by:  
  `parser.add_argument('--output', type=str, default='job_listings.csv', ...)`  
  Change the `default` value to your preferred filename.

### 2. Change which filter options are selected

Edit the lists in `main.py` in the “Tune the filter as per requirement” block:

- **Fewer options** → fewer, more focused results.
- **More options** → more results; scraping will take longer (more pages).

Use the exact strings you see on the EURAXESS filter checkboxes.

### 3. Change delays (if pages load slowly or you hit rate limits)

- **Command line:**  
  `python main.py --MicroDelay 2 --ShortDelay 3 --LongDelay 15`

- **In code:**  
  In `config.py`, change `MICRO_DELAY`, `SHORT_DELAY`, and `LONG_DELAY` in `Config.__init__`.  
  Or in `main.py`, after `config = Config()`, set e.g. `config.LONG_DELAY = 15`.

- **When to increase:**  
  - `LONG_DELAY`: after “Apply filters” (results reload).  
  - `SHORT_DELAY`: after “Next” page.  
  - `MICRO_DELAY`: between small UI actions (opening filters, clicking options).

### 4. Change which columns are saved

Job data is built in `util.get_job_data()` and returned as a list of dicts. Currently each dict has: `Title`, `Country`, `Link`, `date_posted`.

- To **add a field:** In `util.get_job_data()`, find where the card is parsed, extract the new value (e.g. organisation, deadline), and add it to the `data.append({...})` dict. The CSV will then include the new column automatically.
- To **drop a field:** Remove the key from that dict, or in `main.py` after building the DataFrame, do `df = df.drop(columns=["Country"])` (or similar) before `df.to_csv(...)`.

### 5. Add a JOB ID or other derived columns

The script already adds a JOB ID from the link:

```python
df["JOB ID"] = list(map(lambda x: int(x.split("/")[-1]), list(df["Link"])))
```

You can add more columns to `df` before `df.to_csv(...)` (e.g. extract country from another field, or add a “source” column).

---

## Tutorial: Adding New Filters

EURAXESS may show more filters (e.g. Country, Deadline, Organisation). You can add any of them using the same helper.

### Step 1: Find the filter label and option names

1. Open [EURAXESS jobs search](https://euraxess.ec.europa.eu/jobs/search).
2. Find the filter you want (e.g. “Country”, “Career Stage”).
3. Note the **exact label** of the filter (the text next to the dropdown).
4. Open the filter and note the **exact text** of each checkbox you want to select.

### Step 2: Add a list and call `add_filters` in `main.py`

In the “Tune the filter as per requirement” block, define a new list and one more `add_filters` call:

```python
# Tune the filter as per requirement
#----------------------------------------------------------------------------------------------------------
research_fields = ["Computer science", "Computer science other", "Computer technology",
                "Physics", "Physics other", "Applied physics", "Astrophysics", "Computational physics"]
Academic_levels = ["Research Support Positions", "PhD Positions", "Other Positions"]

# New filter example (use exact labels and option names from the website)
countries = ["Germany", "France", "Netherlands"]

util.add_filters(config, driver, wait, "Research Field", research_fields)
util.add_filters(config, driver, wait, "Academic Level", Academic_levels)
util.add_filters(config, driver, wait, "Country", countries)   # new filter
#----------------------------------------------------------------------------------------------------------
```

**Important:** The second argument to `add_filters` is the **filter label** as shown on the page (e.g. `"Country"`, `"Career Stage"`). The fourth argument is the **list of option strings** that must match the checkbox labels exactly.

### Step 3: If the site structure changes

Filter discovery in `util.add_filters()` uses:

- A filter **input** located by: label text + following input with class containing `ecl-select`.
- **Options** by: span with class containing `ecl-checkbox__label-text` and containing the option text.

If EURAXESS changes their HTML or class names, you may need to update the XPath/CSS in `util.py`:

- Filter trigger:  
  `filter_xpath = f"//label[contains(., '{filter_name}')]/following::input[contains(@class, 'ecl-select')][1]"`
- Option:  
  `xpath_selector = f"//span[contains(@class, 'ecl-checkbox__label-text') and contains(., '{option_name}')]"`

Adjust `filter_name` and the selectors to match the new structure if the site is redesigned.

---

## Configuration Summary

| Item            | Where to change                         |
|-----------------|-----------------------------------------|
| Output file     | `--output` or default in `main.py`      |
| Delays          | `config.py` or `--MicroDelay` etc.      |
| Filter options  | Lists in `main.py` (Research Field, etc.) |
| New filters     | New list + `util.add_filters(..., "Filter Label", list)` in `main.py` |
| Columns in CSV  | `util.get_job_data()` dict + optional `df` edits in `main.py` |

---

## Output Format

The CSV contains:

- **Title** — Job title  
- **Country** — Country (or `N/A` if not found)  
- **Link** — URL to the job page  
- **date_posted** — Posted date text  
- **JOB ID** — Numeric ID parsed from the job URL  

---

## Disclaimer

This scraper is for personal or research use. Respect EURAXESS’s terms of use and robots policy; use reasonable delays to avoid overloading the server.
