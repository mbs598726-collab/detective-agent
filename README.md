# Data Detective Agent 🔎

A desktop app that you point at any CSV spreadsheet. It loads the data, lets you
ask plain-English questions about it, and draws charts — all through a graphical
interface (no typing commands into a menu).

Built as part of the Applied Agentic AI Foundation Programme, Month 3.

## Features

- **Preview tab** — open any CSV and see it as a proper spreadsheet table, with
  row/column counts and column names.
- **Ask a Question tab** — pick what you want to know from a dropdown:
  - Row count
  - Average of a column
  - Highest & lowest of a column
  - Find the row with the top value (who actually has that highest score?)
  - Filter rows by a condition (e.g. `Population_Millions > 200`)
  - Average grouped by a category (e.g. average GDP per continent)
- **Charts tab** — generate a bar chart, line chart, or histogram from any
  columns, shown right inside the window, with a button to save it as a PNG.
- Ships with `world_data.csv` — a small **real-world** dataset (20 countries:
  population, continent, GDP, area, life expectancy) instead of made-up sample
  data. Open your own CSV any time with the **Open CSV...** button.

## Requirements

- Python 3.9 or newer
- The following libraries:
  - `customtkinter`
  - `pandas`
  - `matplotlib`
  - `numpy`

## Setup

1. Put `detective_gui.py` and `world_data.csv` in the same folder.
2. Open a terminal in that folder.
3. Install the dependencies:

   ```bash
   pip install customtkinter pandas matplotlib numpy
   ```

   If `pip` isn't recognised, try:

   ```bash
   python -m pip install customtkinter pandas matplotlib numpy
   ```

## Running the app

```bash
python detective_gui.py
```

On Windows, if you use the `py` launcher instead:

```bash
py detective_gui.py
```

The app will automatically load `world_data.csv` on startup if it's sitting
next to the script. Use the **Open CSV...** button at any time to load a
different spreadsheet.

## How to use it

1. **Preview tab** — check the shape and column names of your data first, so
   you know what you're working with.
2. **Ask a Question tab** — choose an operation from the dropdown. The input
   fields below it change depending on what you pick (e.g. filtering asks for
   a column, a comparison, and a value). Click **Run** to see the answer.
3. **Charts tab** — pick a chart type and the column(s) to plot, click
   **Generate**, then **Save PNG...** if you want to keep a copy of the image.

## Using your own data

Any CSV works, as long as the first row is the column headers. Numeric columns
(numbers) are used for averages, filters, and chart values; text columns
(like country or category names) are used for grouping and as chart labels.

## Notes on the sample data

The figures in `world_data.csv` (population, GDP, etc.) are approximate,
commonly cited public figures included for demonstration purposes — not a
live data feed. Swap in your own dataset for anything you need to be exact
about.

## Troubleshooting

| Problem | Likely fix |
|---|---|
| `ModuleNotFoundError: No module named 'customtkinter'` | Run the `pip install` command above. |
| Blank/empty screen on a tab | Update customtkinter: `pip install --upgrade customtkinter`, then re-run from a terminal (not by double-clicking) so any error message is visible. |
| `File not found` when opening a CSV | Make sure the file path is correct and the file isn't open in Excel (which can lock it). |
| A column doesn't show up in a dropdown | Numeric operations (average, filter, chart Y-axis) only list number columns; text columns only appear for grouping and as chart X-axis/category options. |

## Project structure

```
detective agent/
├── detective_gui.py   # the app
├── world_data.csv     # sample real-world dataset
└── README.md          # this file
```