# Analysis plan: FHIR Encounter Analytics

## Context

FHIR (Fast Healthcare Interoperability Resources) is a standard for exchanging health information via structured resources and APIs. Our first relevant resources are:

| Resource | Role in the analysis | Key fields to inspect |
|---|---|---|
| Patient | Unique subject of care | id, gender, birthDate |
| Encounter | A recorded healthcare interaction | id, subject.reference, status, class.code, period.start, period.end |

We will not assume every resource has every field. Some encounters can lack patients, end dates or meaningful classifications.

## Analytical questions

1. What is the size and coverage of the extracted cohort?
2. How many encounters are associated with each patient?
3. What are the encounter status and class distributions?
4. What time trends and encounter durations can be measured without unsupported assumptions?
5. What missingness or coding issues could distort findings?

## Initial relational design

- `patients(patient_id PRIMARY KEY, gender, birth_date)`
- `encounters(encounter_id PRIMARY KEY, patient_id, status, class_code, start_time, end_time)`

A patient's birth date is optional, and the encounter-to-patient relationship must be tested for missing or unmatched references. We will design SQL tables after inspecting real example *synthetic* resources.

## Quality checks

- Check resource types, unique identifiers, duplicates and referential integrity.
- Profile missing dates, non-parseable values and invalid time intervals.
- Record population and sample selection criteria.
- Avoid patient-identifying fields not needed for the stated questions.
- Keep all result figures marked provisional until checks are passed.

## First milestone

1. Run the metadata script to verify that the endpoint responds.
2. Confirm the API is FHIR R4 and identify supported `Patient` and `Encounter` resources.
3. Review suitable synthetic data sources for a stable reproducible cohort.
4. Decide extract size and analysis period based on inspected source coverage.

**No figures, outcomes or claims have been calculated at this stage.**
