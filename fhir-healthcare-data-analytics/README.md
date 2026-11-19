# FHIR Healthcare Data Integration & Encounter Analytics

**Portfolio:** Gideon Odeyemi  
**Focus:** Clinical & Operations Data Analytics  
**Skills:** Python · REST APIs · FHIR R4 · SQL · Exploratory Analysis  
**Stage:** Project definition and API discovery

## Business question

**What patterns in healthcare encounters and service utilisation can we identify from standardised FHIR records, and what data-quality limitations affect our conclusions?**

This is an analytics project with a practical API/data-pipeline component, not just a software integration demonstration.

## Objectives

- Retrieve a reproducible set of **synthetic** FHIR R4 `Patient` and `Encounter` resources from an appropriate test dataset.
- Understand how patient and encounter records relate.
- Assess missing fields, duplicated IDs, invalid dates and incomplete patient references.
- Build analysis-ready relational tables in SQL.
- Explore visit frequency, encounter class, encounter status, and time-based utilisation patterns where the data supports them.
- Explain limitations and present findings with clear visualisations.

## Planned workflow

| Stage | Output | Tools |
|---|---|---|
| Define problem and source | Scope, questions, provenance and limitations | Documentation |
| Explore the FHIR API | Capability statement, resource definitions and test connection | Python |
| Extract and validate synthetic records | Reproducible extracts and a cleaning log | Python |
| Model analytics tables | Patient and encounter tables with keys and relationships | SQL |
| Analyse utilisation | Queries, measures, charts and interpretation | SQL + Python |
| Publish case study | Results, quality checks, limitations and portfolio links | GitHub + website |

## Initial measures (subject to data quality)

1. Encounter counts and patient counts.
2. Encounters per patient.
3. Encounter class and status distribution.
4. Encounter duration, **only** when reliable start/end fields exist.
5. Counts by month/weekday, **only** when enough trustworthy dates exist.

**Important:** Do not interpret a public test server's changing records as representative of a hospital, a region or real-world clinical utilisation. Rates and results must describe only the extracted test dataset.

## API starting point

For *learning the protocol*, we will inspect the public [HAPI FHIR R4 test server](https://hapi.fhir.org/) and its capability statement at `https://hapi.fhir.org/baseR4/metadata`. This is a shared demonstration service, **not** a verified, fixed cohort of synthetic encounters. We will choose and document a suitable synthetic dataset before producing analytical conclusions. Do not upload actual patient information to any public server.

## Current files

- `scripts/01_check_fhir_api.py`: checks FHIR R4 server metadata without retrieving patient records.
- `requirements.txt`: Python dependency for the initial API check.
- `docs/analysis-plan.md`: problem, initial schema and acceptance criteria.

## Data integrity and ethics

Use only verified synthetic/public demonstration data; never use confidential patient information. Keep raw downloads out of Git until their provenance and permissible publication are confirmed. Record extraction date, source URL, query parameters and row counts. Treat missingness, coding differences and time ranges explicitly.

## Project status

**Started:** November 2026. No dataset, validated findings or dashboard have been produced yet.
