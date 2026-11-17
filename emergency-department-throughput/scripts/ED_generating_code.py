import pandas as pd
import numpy as np
from pathlib import Path

# ============================================================
# CEDARBRIDGE GENERAL HOSPITAL (FICTIONAL)
# EMERGENCY DEPARTMENT RAW DATA GENERATOR
#
# Reporting period: 01 January - 31 October 2026
# Original unique visits: 4,000
# Intentional duplicate records: 60
# Expected raw rows: 4,060
#
# Python: Dataset generation ONLY
# Excel: Data cleaning, profiling and analysis
# Power BI: Interactive dashboard
#
# All data is synthetic. No real patients or hospitals.
# ============================================================


# ------------------------------------------------------------
# 1. SETTINGS
# ------------------------------------------------------------

RANDOM_SEED = 20261031
TOTAL_VISITS = 4000
DUPLICATE_COUNT = 60

rng = np.random.default_rng(RANDOM_SEED)

start_date = pd.Timestamp("2026-01-01 00:00:00")
end_date = pd.Timestamp("2026-11-01 00:00:00")

MODES = ["Walk-in", "Ambulance", "Referral", "Police"]
ACUITY = ["Resuscitation", "Emergency", "Urgent", "Less Urgent"]


# ------------------------------------------------------------
# 2. GENERATE ARRIVAL DATETIMES
# Busiest: afternoons, Mondays, July-August
# ------------------------------------------------------------

hour_bins = pd.date_range(
    start=start_date,
    end=end_date,
    freq="h",
    inclusive="left"
)

weekday_weights = {
    0: 1.25,  # Monday surge
    1: 1.10,
    2: 1.10,
    3: 1.10,
    4: 1.10,
    5: 0.95,
    6: 0.90
}

month_weights = {
    1: 0.95, 2: 0.95, 3: 1.00, 4: 1.00, 5: 1.05,
    6: 1.05, 7: 1.10, 8: 1.10, 9: 1.00, 10: 1.05
}


def hour_of_day_weight(hour):
    if 12 <= hour <= 18:
        return 1.65
    if 7 <= hour <= 11 or 19 <= hour <= 22:
        return 1.35
    if hour >= 23 or hour <= 5:
        return 0.55
    return 0.85


hour_weights = np.array([
    hour_of_day_weight(ts.hour)
    * weekday_weights[ts.dayofweek]
    * month_weights[ts.month]
    for ts in hour_bins
], dtype=float)

hour_weights /= hour_weights.sum()

selected_hours = rng.choice(
    len(hour_bins),
    size=TOTAL_VISITS,
    replace=True,
    p=hour_weights
)

# Sorted so visit IDs run in time order, like a real system.
arrival_datetimes = sorted(
    hour_bins[h] + pd.Timedelta(seconds=int(rng.integers(0, 3600)))
    for h in selected_hours
)


# ------------------------------------------------------------
# 3. GENERATE PATIENT CHARACTERISTICS
# Age -> arrival mode -> acuity (each depends on the one before)
# ------------------------------------------------------------

age_bands = [(1, 17), (18, 39), (40, 64), (65, 95)]
band_probs = [0.22, 0.25, 0.28, 0.25]

band_choice = rng.choice(
    len(age_bands),
    size=TOTAL_VISITS,
    p=band_probs
)

ages = np.array([
    int(rng.integers(age_bands[b][0], age_bands[b][1] + 1))
    for b in band_choice
])

sexes = rng.choice(
    ["Male", "Female"],
    size=TOTAL_VISITS,
    p=[0.48, 0.52]
)


def arrival_mode_probs(age):
    # Order: Walk-in, Ambulance, Referral, Police
    if age >= 65:
        return [0.50, 0.38, 0.11, 0.01]
    if age >= 40:
        return [0.68, 0.19, 0.12, 0.01]
    if age >= 18:
        return [0.68, 0.18, 0.10, 0.04]
    return [0.80, 0.08, 0.12, 0.00]


def acuity_probs(age, mode):
    # Order: Resuscitation, Emergency, Urgent, Less Urgent
    if mode == "Ambulance":
        p = [0.08, 0.30, 0.45, 0.17]
    elif mode == "Police":
        p = [0.03, 0.17, 0.50, 0.30]
    elif mode == "Referral":
        p = [0.03, 0.20, 0.52, 0.25]
    else:
        p = [0.01, 0.10, 0.47, 0.42]

    p = np.array(p, dtype=float)

    if age >= 65:
        p[0] += 0.02
        p[1] += 0.06
        p[3] -= 0.08

    return p / p.sum()


arrival_modes = []
acuity_levels = []

for age in ages:
    mode = str(rng.choice(MODES, p=arrival_mode_probs(age)))
    arrival_modes.append(mode)
    acuity_levels.append(
        str(rng.choice(ACUITY, p=acuity_probs(age, mode)))
    )


# ------------------------------------------------------------
# 4. GENERATE TRIAGE AND PROVIDER ASSESSMENT TIMES
# Waits are longer in the afternoon, on Mondays, in summer
# ------------------------------------------------------------

wait_scale = {
    "Resuscitation": 2,
    "Emergency": 12,
    "Urgent": 30,
    "Less Urgent": 55
}

triage_range = {  # minutes from arrival to triage (low, high-exclusive)
    "Resuscitation": (1, 4),
    "Emergency": (2, 9),
    "Urgent": (3, 16),
    "Less Urgent": (5, 26)
}

triage_datetimes = []
provider_datetimes = []
waiting_times = []

for i in range(TOTAL_VISITS):

    arrival = arrival_datetimes[i]
    acuity = acuity_levels[i]

    low, high = triage_range[acuity]
    triage_delay = int(rng.integers(low, high))

    crowding = 1.0

    if 12 <= arrival.hour <= 18:
        crowding = 1.25
    elif 19 <= arrival.hour <= 22:
        crowding = 1.10

    if arrival.dayofweek == 0:
        crowding *= 1.10

    if arrival.month in (7, 8):
        crowding *= 1.10

    ambulance_factor = 0.65 if arrival_modes[i] == "Ambulance" else 1.0

    wait = int(
        rng.gamma(
            shape=2.0,
            scale=wait_scale[acuity] * crowding * ambulance_factor
        )
    )

    wait = max(wait, triage_delay + 1)

    triage_datetimes.append(arrival + pd.Timedelta(minutes=triage_delay))
    provider_datetimes.append(arrival + pd.Timedelta(minutes=wait))
    waiting_times.append(wait)


# ------------------------------------------------------------
# 5. GENERATE DISPOSITIONS AND DEPARTURE TIMES
# Long waits -> more walk-outs. Older patients -> more admissions
# and longer boarding for a bed.
# ------------------------------------------------------------

admission_base = {
    "Resuscitation": 0.70,
    "Emergency": 0.45,
    "Urgent": 0.18,
    "Less Urgent": 0.04
}

dispositions = []
disposition_datetimes = []
departure_datetimes = []

for i in range(TOTAL_VISITS):

    acuity = acuity_levels[i]
    age = ages[i]
    arrival = arrival_datetimes[i]
    provider_time = provider_datetimes[i]
    wait = waiting_times[i]

    lwbs_probability = min(0.01 + max(wait - 45, 0) * 0.0012, 0.20)

    if acuity == "Resuscitation":
        lwbs_probability = 0.0
    elif acuity == "Emergency":
        lwbs_probability *= 0.4

    if rng.random() < lwbs_probability:

        disposition = "Left Without Being Seen"

        departure_delay = int(
            rng.integers(max(wait, 10), max(wait, 10) + 91)
        )

        disposition_time = pd.NaT
        departure_time = arrival + pd.Timedelta(minutes=departure_delay)

    else:

        admission_probability = admission_base[acuity]

        if age >= 65:
            admission_probability += 0.12
        elif age < 18:
            admission_probability *= 0.5

        admission_probability = min(admission_probability, 0.90)

        transfer_probability = (
            0.06 if acuity in ("Resuscitation", "Emergency") else 0.025
        )

        random_value = rng.random()

        if random_value < admission_probability:
            disposition = "Admitted"
        elif random_value < admission_probability + transfer_probability:
            disposition = "Transferred"
        else:
            disposition = "Discharged"

        decision_delay = int(rng.gamma(shape=2.0, scale=35))

        disposition_time = provider_time + pd.Timedelta(
            minutes=decision_delay
        )

        if disposition == "Admitted":

            boarding_factor = 1.0

            if 12 <= arrival.hour <= 22:
                boarding_factor *= 1.25
            if arrival.month in (7, 8):
                boarding_factor *= 1.10
            if age >= 65:
                boarding_factor *= 1.15

            boarding_minutes = int(
                rng.gamma(shape=2.0, scale=100 * boarding_factor)
            ) + 15

            departure_time = disposition_time + pd.Timedelta(
                minutes=boarding_minutes
            )

        elif disposition == "Transferred":

            transfer_delay = int(
                rng.gamma(shape=2.0, scale=55)
            ) + 20

            departure_time = disposition_time + pd.Timedelta(
                minutes=transfer_delay
            )

        else:

            discharge_delay = int(
                rng.gamma(shape=2.0, scale=30)
            ) + 10

            departure_time = disposition_time + pd.Timedelta(
                minutes=discharge_delay
            )

    dispositions.append(disposition)
    disposition_datetimes.append(disposition_time)
    departure_datetimes.append(departure_time)


# ------------------------------------------------------------
# 6. BUILD THE BASE DATASET
# ------------------------------------------------------------

df = pd.DataFrame({
    "visit_id": [f"ED{n:05d}" for n in range(1, TOTAL_VISITS + 1)],
    "arrival_datetime": arrival_datetimes,
    "age": ages,
    "sex": sexes,
    "arrival_mode": arrival_modes,
    "acuity": acuity_levels,
    "triage_datetime": triage_datetimes,
    "provider_start_datetime": provider_datetimes,
    "disposition": dispositions,
    "disposition_datetime": disposition_datetimes,
    "departure_datetime": departure_datetimes
})

# LWBS patients never see a provider.
lwbs_mask = df["disposition"] == "Left Without Being Seen"
df.loc[lwbs_mask, "provider_start_datetime"] = pd.NaT


# ------------------------------------------------------------
# 7. VALID LONG STAYS, THEN DURATION FIELDS
# Five admitted patients stay 36-72 hours longer. These are
# REAL outliers, not errors. They must not be deleted.
# ------------------------------------------------------------

available = set(df.index)


def pick(eligible, n):
    """Pick n unused rows so no row gets two planted issues."""
    eligible = sorted(i for i in eligible if i in available)
    chosen = [int(i) for i in rng.choice(eligible, size=n, replace=False)]
    available.difference_update(chosen)
    return chosen


admitted_idx = df.index[df["disposition"] == "Admitted"].tolist()
valid_long_stay = pick(admitted_idx, 5)

for i in valid_long_stay:
    extra_hours = int(rng.integers(36, 73))
    df.at[i, "departure_datetime"] = (
        df.at[i, "departure_datetime"] + pd.Timedelta(hours=extra_hours)
    )

df["waiting_time_minutes"] = (
    df["provider_start_datetime"] - df["arrival_datetime"]
).dt.total_seconds() / 60

df["length_of_stay_minutes"] = (
    df["departure_datetime"] - df["arrival_datetime"]
).dt.total_seconds() / 60

df["boarding_time_minutes"] = np.where(
    df["disposition"] == "Admitted",
    (df["departure_datetime"] - df["disposition_datetime"]).dt.total_seconds() / 60,
    np.nan
)


# ------------------------------------------------------------
# 8. INTRODUCE CONTROLLED DATA-QUALITY ISSUES
# Exact counts, no overlap between issue types.
# ------------------------------------------------------------

all_rows = df.index.tolist()

issue_rows = {
    "valid_long_stay": valid_long_stay,  # keep, not an error
    "missing_triage": pick(all_rows, 25),
    "missing_disposition": pick(all_rows, 12),
    "negative_wait": pick(
        df.index[df["waiting_time_minutes"].notna()].tolist(), 8
    ),
    "invalid_departure": pick(
        df.index[df["disposition"] != "Admitted"].tolist(), 4
    ),
    "los_as_text": pick(all_rows, 20),
    "category_variations": pick(all_rows, 20),
}

# 8A. Missing triage timestamps.
for i in issue_rows["missing_triage"]:
    df.at[i, "triage_datetime"] = pd.NaT

# 8B. Missing disposition labels (timestamps and boarding time stay).
for i in issue_rows["missing_disposition"]:
    df.at[i, "disposition"] = np.nan

# 8C. Negative waiting times.
for i in issue_rows["negative_wait"]:
    df.at[i, "waiting_time_minutes"] = -abs(
        df.at[i, "waiting_time_minutes"]
    )

# 8D. Departure before arrival.
for i in issue_rows["invalid_departure"]:
    df.at[i, "departure_datetime"] = (
        df.at[i, "arrival_datetime"] - pd.Timedelta(minutes=15)
    )
    df.at[i, "length_of_stay_minutes"] = -15.0

# 8E. Length of stay stored as text ("125 mins" or "2h 05m").
df["length_of_stay_minutes"] = df["length_of_stay_minutes"].astype(object)

for position, i in enumerate(issue_rows["los_as_text"]):
    minutes = int(df.at[i, "length_of_stay_minutes"])

    if position % 2 == 0:
        df.at[i, "length_of_stay_minutes"] = f"{minutes} mins"
    else:
        df.at[i, "length_of_stay_minutes"] = (
            f"{minutes // 60}h {minutes % 60:02d}m"
        )

# 8F. Inconsistent arrival-mode labels. Only spelling, case and
# spacing change. The meaning of each row stays the same.
messy_labels = {
    "Walk-in": ["Walk In", "walk-in", "WALK-IN", "Walk-in "],
    "Ambulance": ["AMBULANCE", "ambulance", "Ambulance "],
    "Referral": ["referral", "Referral "],
    "Police": ["Police ", "police"],
}

for i in issue_rows["category_variations"]:
    options = messy_labels[df.at[i, "arrival_mode"]]
    df.at[i, "arrival_mode"] = options[int(rng.integers(0, len(options)))]


# ------------------------------------------------------------
# 9. STANDARDISE DATETIME EXPORT FORMAT
# ------------------------------------------------------------

datetime_columns = [
    "arrival_datetime",
    "triage_datetime",
    "provider_start_datetime",
    "disposition_datetime",
    "departure_datetime"
]

arrival_check = pd.to_datetime(df["arrival_datetime"], errors="coerce")

assert arrival_check.notna().all()
assert arrival_check.min() >= start_date
assert arrival_check.max() < end_date

print("\nARRIVAL DATE VALIDATION PASSED")
print("Earliest arrival:", arrival_check.min())
print("Latest arrival:", arrival_check.max())

for column in datetime_columns:
    df[column] = pd.to_datetime(
        df[column], errors="coerce"
    ).dt.strftime("%Y-%m-%d %H:%M:%S")
    df[column] = df[column].fillna("")


# ------------------------------------------------------------
# 10. ADD 60 EXACT DUPLICATE RECORDS
# ------------------------------------------------------------

duplicate_rows = df.sample(n=DUPLICATE_COUNT, random_state=RANDOM_SEED)

df_raw = pd.concat([df, duplicate_rows], ignore_index=True)

df_raw = df_raw.sample(
    frac=1,
    random_state=RANDOM_SEED
).reset_index(drop=True)


# ------------------------------------------------------------
# 11. FINAL VALIDATION
# ------------------------------------------------------------

assert len(df_raw) == TOTAL_VISITS + DUPLICATE_COUNT
assert df_raw["visit_id"].nunique() == TOTAL_VISITS

print("\n======================================")
print("CEDARBRIDGE ED DATASET GENERATION")
print("======================================")

print("Original unique visits:", TOTAL_VISITS)
print("Duplicate records added:", DUPLICATE_COUNT)
print("Final raw dataset rows:", len(df_raw))
print("Column count:", len(df_raw.columns))

print("\nBlank values by column:")
for column in df_raw.columns:
    if column in datetime_columns:
        blanks = int((df_raw[column] == "").sum())
    else:
        blanks = int(df_raw[column].isna().sum())
    print(f"  {column}: {blanks}")

print("\nDisposition counts:")
print(df_raw["disposition"].value_counts(dropna=False))

print("\nArrival mode counts:")
print(df_raw["arrival_mode"].value_counts(dropna=False))

print("\nPlanted issues (unique visits):")
for name, rows in issue_rows.items():
    print(f"  {name}: {len(rows)}")
print(f"  duplicate_records: {DUPLICATE_COUNT}")

print("\nALL VALIDATION CHECKS PASSED")


# ------------------------------------------------------------
# 12. SAVE RAW DATASET + PRIVATE ISSUE KEY
# The key lists every planted issue so you can check your
# cleaning against it. Don't use it in the dashboard.
# ------------------------------------------------------------

desktop = Path.home() / "Desktop"

if not desktop.exists():
    desktop = Path.cwd()

output_file = desktop / "Cedarbridge_ED_Raw_Jan_Oct_2026.csv"

df_raw.to_csv(output_file, index=False, encoding="utf-8-sig")


print("\n======================================")
print("DATASET SUCCESSFULLY GENERATED")
print("======================================")
print("Saved to:")
print(output_file)