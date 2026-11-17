# Cedarbridge General Hospital: Emergency Department Throughput

An end-to-end analysis of 4,000 synthetic emergency department visits (January to October 2026). Python generates the dataset, Excel Power Query cleans it, Excel PivotTables explore it, and a four-page Power BI dashboard presents the findings.

> **All data is synthetic.** No real patients or hospitals. The patterns were built into the generator, so the findings demonstrate the method, not real hospital performance.

![Overview](docs/screenshots/01-overview.png)

## Business questions

1. When is the ED busiest?
2. Are patients seen within target wait times?
3. Who walks out without being seen, and when?
4. Who gets admitted, and how long do they wait for a bed?

## Key findings

**Volume**
- Afternoons carry 36% of visits, and Monday is the busiest day (660 visits).
- July and August run about 20% busier than January to April.

**Waits**
- Only 32% of seen patients met their wait target (median wait 50 minutes).
- By acuity: Resuscitation 79%, Emergency 40%, Urgent 28%, Less Urgent 29%.

**Walk-outs**
- 218 patients (5.5%) left without being seen, all from Urgent and Less Urgent.
- Less Urgent patients left at 9.3%, nearly twice the Urgent rate (5.1%).
- Afternoons had the highest walk-out rate (6.5%) and night the lowest (3.3%).

**Admissions and boarding**
- 21% of seen patients were admitted, but about 37% of patients aged 65+ versus 10 to 18% for everyone else.
- Median boarding time after the admit decision was 224 minutes. Afternoon and evening arrivals waited 244 and 237 minutes, versus 193 at night and 185 in the morning.
- 7 stays ran past 24 hours (5 past 48 hours). They were kept and flagged, and medians are used so they do not distort results.

**Suggested actions (for discussion)**
- Open a fast-track lane for Less Urgent patients in the afternoon.
- Plan bed capacity for afternoons and evenings.
- Start discharge planning earlier for older patients.

## Dashboard pages

| Page | What it answers |
|---|---|
| Overview | Headline KPIs, monthly volume, acuity mix, hour-band summary |
| Patient Flow | Weekday by time-of-day heatmap, arrivals by hour, arrival mode, age groups |
| Waits | Wait target performance, waits vs walk-outs by hour band, walk-outs by acuity |
| Admissions | Admit rate by age, boarding time by hour band and age, length of stay by disposition |

![Patient Flow](docs/screenshots/02-patient-flow.png)
![Waits](docs/screenshots/03-waits.png)
![Admissions](docs/screenshots/04-admissions.png)

## How it was built

| Stage | Tool | What happened |
|---|---|---|
| Data generation | Python (pandas, numpy) | Seeded script (seed 20261031) creates 4,000 visits plus 60 duplicates and planted data-quality issues |
| Cleaning | Excel Power Query | 4,060 raw rows cleaned to 4,000 visits, with every step documented |
| Exploration | Excel PivotTables | Volume, wait targets, walk-outs, admissions and boarding, reconciled to source totals |
| Dashboard | Power BI | Date table, DAX measures, custom teal theme, four pages |

## Data cleaning summary

| Issue | Rows | Action |
|---|---|---|
| Duplicate records | 60 | Removed |
| Inconsistent arrival mode labels | 20 | Standardised to 4 values |
| Length of stay stored as text | 20 | Parsed to minutes |
| Missing triage time | 25 | Flagged, visits kept |
| Missing disposition | 12 | 1 recovered as Admitted, 11 labelled Unknown |
| Negative waiting time | 8 | Recalculated from timestamps |
| Departure before arrival | 4 | Departure and LOS blanked, visits kept |
| Extended stays (over 24 hours) | 7 | Flagged and kept |

The full log is in [`docs/ED_Cleaning_Log.xlsx`](docs/ED_Cleaning_Log.xlsx).

## Definitions and assumptions

- **Wait targets** (assumed): Resuscitation 5 minutes, Emergency 15, Urgent 30, Less Urgent 60.
- **Wait Target Met %** is calculated among patients who were seen.
- **LWBS Rate** = walk-outs divided by all visits.
- **Admit Rate** = admitted divided by seen visits (walk-outs excluded).
- **Waits, length of stay and boarding** use medians, because a few very long stays skew averages.

## Limitations

- Synthetic data: findings reflect how the dataset was generated, not a real hospital.
- Wait targets are assumptions, not an official standard.
- Walk-outs have no recorded wait, so wait figures understate the real experience.
- Night boarding cells are small (10 to 35 admits per age group), so read them with care.
- No staffing, bed capacity or diagnosis data.

## Repository structure

```
cedarbridge-ed-dashboard/
├── README.md
├── scripts/
│   └── cedarbridge_ed_generator.py
├── data/
│   ├── Cedarbridge_ED_Raw_Jan_Oct_2026.csv
│   └── Cedarbridge_ED_Issue_Key.csv
├── excel/
│   └── Cedarbridge_ED_Analysis.xlsx
├── powerbi/
│   ├── Cedarbridge_ED_Dashboard.pbix
│   └── Cedarbridge_ED_Teal_Theme.json
└── docs/
    ├── ED_Dashboard.pdf
    ├── ED_Cleaning_Log.xlsx
    └── screenshots/
```

## Reproduce it

1. Run `scripts/cedarbridge_ed_generator.py` (Python 3 with pandas and numpy). The seed makes the dataset repeatable.
2. Open the Excel workbook to see the Power Query steps and pivots.
3. Open the `.pbix` in Power BI Desktop.

## Author

Gideon Odeyemi, Clinical & Operations Data Analyst.
Portfolio: