from pathlib import Path
import re
import pandas as pd

RAW_DIR = Path("data/raw")
OUT_DIR = Path("data/processed")
OUT_DIR.mkdir(parents=True, exist_ok=True)


def find_file(*names):
    """Return the first matching file path from data/raw using possible names."""
    for name in names:
        path = RAW_DIR / name
        if path.exists():
            return path

    lowered = {p.name.lower(): p for p in RAW_DIR.glob("*")}
    for name in names:
        key = name.lower()
        if key in lowered:
            return lowered[key]

    raise FileNotFoundError(
        "Could not find any of these files inside data/raw: " + ", ".join(names)
    )


def clean_col(name):
    name = str(name).strip().lower()
    name = re.sub(r"[^a-z0-9]+", "_", name)
    name = re.sub(r"_+", "_", name).strip("_")
    return name


def clean_text(series):
    return series.astype(str).str.strip().replace({"nan": pd.NA, "None": pd.NA})


def yes_no_to_int(value):
    if pd.isna(value):
        return 0
    if isinstance(value, (int, float)):
        return int(value > 0)
    value = str(value).strip().lower()
    return 1 if value in ["yes", "y", "true", "1"] else 0


def pct(part, whole):
    if whole == 0:
        return 0
    return round((part / whole) * 100, 1)


def write_csv(df, filename):
    path = OUT_DIR / filename
    df.to_csv(path, index=False)
    print(f"Saved {path} ({len(df)} rows)")


# -------------------------------------------------------------------
# 1. STUDENT MENTAL HEALTH DATASET
# -------------------------------------------------------------------

student_path = find_file(
    "student_mental_health.csv",
    "Student Mental health.csv",
    "Student Mental health(1).csv",
)

print(f"Using student dataset: {student_path}")

student_raw = pd.read_csv(student_path)
student_raw.columns = [clean_col(c) for c in student_raw.columns]

student = student_raw.rename(columns={
    "timestamp": "timestamp",
    "choose_your_gender": "gender",
    "age": "age",
    "what_is_your_course": "course",
    "your_current_year_of_study": "year_of_study",
    "what_is_your_cgpa": "cgpa_range",
    "marital_status": "marital_status",
    "do_you_have_depression": "depression",
    "do_you_have_anxiety": "anxiety",
    "do_you_have_panic_attack": "panic_attack",
    "did_you_seek_any_specialist_for_a_treatment": "specialist_treatment",
})

required_student_cols = [
    "gender", "age", "course", "year_of_study", "cgpa_range",
    "depression", "anxiety", "panic_attack", "specialist_treatment"
]

missing = [c for c in required_student_cols if c not in student.columns]
if missing:
    raise ValueError(f"Student dataset is missing required columns: {missing}")

for col in ["gender", "course", "year_of_study", "cgpa_range", "marital_status"]:
    if col in student.columns:
        student[col] = clean_text(student[col])

student["gender"] = student["gender"].str.title()

student["year_of_study"] = (
    student["year_of_study"]
    .str.lower()
    .str.extract(r"(\d+)", expand=False)
    .fillna("Unknown")
    .apply(lambda x: f"Year {x}" if x != "Unknown" else x)
)

student["year_order"] = (
    student["year_of_study"]
    .str.extract(r"(\d+)", expand=False)
    .astype(float)
)

student["cgpa_range"] = (
    student["cgpa_range"]
    .str.replace(r"\s+", " ", regex=True)
    .str.strip()
)

cgpa_order = {
    "0 - 1.99": 1,
    "2.00 - 2.49": 2,
    "2.50 - 2.99": 3,
    "3.00 - 3.49": 4,
    "3.50 - 4.00": 5,
}

student["cgpa_order"] = student["cgpa_range"].map(cgpa_order).fillna(99)
student["age"] = pd.to_numeric(student["age"], errors="coerce")

for col in ["depression", "anxiety", "panic_attack", "specialist_treatment"]:
    student[col + "_flag"] = student[col].apply(yes_no_to_int)

student["symptom_count"] = (
    student["depression_flag"] +
    student["anxiety_flag"] +
    student["panic_attack_flag"]
)

student["any_symptom_flag"] = (student["symptom_count"] > 0).astype(int)
student["multiple_symptoms_flag"] = (student["symptom_count"] >= 2).astype(int)

student["treatment_gap_flag"] = (
    (student["any_symptom_flag"] == 1) &
    (student["specialist_treatment_flag"] == 0)
).astype(int)

write_csv(student, "student_clean.csv")

total_students = len(student)

kpis = pd.DataFrame([
    {"order": 1, "indicator": "Reported depression", "short_label": "Depression", "count": int(student["depression_flag"].sum())},
    {"order": 2, "indicator": "Reported anxiety", "short_label": "Anxiety", "count": int(student["anxiety_flag"].sum())},
    {"order": 3, "indicator": "Reported panic attacks", "short_label": "Panic attacks", "count": int(student["panic_attack_flag"].sum())},
    {"order": 4, "indicator": "Sought specialist treatment", "short_label": "Treatment", "count": int(student["specialist_treatment_flag"].sum())},
    {"order": 5, "indicator": "Reported at least one symptom", "short_label": "Any symptom", "count": int(student["any_symptom_flag"].sum())},
    {"order": 6, "indicator": "Reported two or more symptoms", "short_label": "2+ symptoms", "count": int(student["multiple_symptoms_flag"].sum())},
    {"order": 7, "indicator": "Reported symptoms but no specialist treatment", "short_label": "Treatment gap", "count": int(student["treatment_gap_flag"].sum())},
])

kpis["total"] = total_students
kpis["percent"] = kpis["count"].apply(lambda c: pct(c, total_students))
kpis["percent_label"] = kpis["percent"].map(lambda x: f"{x:.1f}%")
write_csv(kpis, "student_kpis.csv")

symptom_rates = pd.DataFrame([
    {"order": 1, "symptom": "Depression", "count": int(student["depression_flag"].sum())},
    {"order": 2, "symptom": "Anxiety", "count": int(student["anxiety_flag"].sum())},
    {"order": 3, "symptom": "Panic attacks", "count": int(student["panic_attack_flag"].sum())},
])

symptom_rates["total"] = total_students
symptom_rates["percent"] = symptom_rates["count"].apply(lambda c: pct(c, total_students))
symptom_rates["label"] = symptom_rates["percent"].map(lambda x: f"{x:.1f}%")
write_csv(symptom_rates, "symptom_rates.csv")

symptom_overlap = (
    student.groupby("symptom_count")
    .size()
    .reset_index(name="count")
)

symptom_overlap["total"] = total_students
symptom_overlap["percent"] = symptom_overlap["count"].apply(lambda c: pct(c, total_students))
symptom_overlap["symptom_group"] = symptom_overlap["symptom_count"].map({
    0: "0 symptoms",
    1: "1 symptom",
    2: "2 symptoms",
    3: "3 symptoms"
})
symptom_overlap["label"] = symptom_overlap["percent"].map(lambda x: f"{x:.1f}%")
write_csv(symptom_overlap, "symptom_overlap.csv")

any_symptom_count = int(student["any_symptom_flag"].sum())
treatment_count = int(student["specialist_treatment_flag"].sum())
treatment_gap_count = int(student["treatment_gap_flag"].sum())

treatment_gap = pd.DataFrame([
    {"order": 1, "indicator": "Reported at least one symptom", "count": any_symptom_count, "type": "symptom"},
    {"order": 2, "indicator": "Sought specialist treatment", "count": treatment_count, "type": "support"},
    {"order": 3, "indicator": "Symptoms but no specialist treatment", "count": treatment_gap_count, "type": "gap"},
])

treatment_gap["total"] = total_students
treatment_gap["percent"] = treatment_gap["count"].apply(lambda c: pct(c, total_students))
treatment_gap["label"] = treatment_gap["percent"].map(lambda x: f"{x:.1f}%")
write_csv(treatment_gap, "treatment_gap.csv")

symptom_cols = {
    "Depression": "depression_flag",
    "Anxiety": "anxiety_flag",
    "Panic attacks": "panic_attack_flag",
    "Any symptom": "any_symptom_flag",
}


def rates_by_group(group_col, order_col=None):
    rows = []
    grouped = student.dropna(subset=[group_col]).groupby(group_col)

    for group, g in grouped:
        for symptom, col in symptom_cols.items():
            rows.append({
                "group": group,
                "symptom": symptom,
                "count": int(g[col].sum()),
                "total": len(g),
                "percent": pct(int(g[col].sum()), len(g)),
                "order": float(g[order_col].iloc[0]) if order_col and order_col in g.columns else 0,
            })

    return pd.DataFrame(rows)


gender_rates = rates_by_group("gender")
write_csv(gender_rates, "gender_symptom_rates.csv")

year_rates = rates_by_group("year_of_study", "year_order")
write_csv(year_rates, "year_symptom_rates.csv")

cgpa_rates = rates_by_group("cgpa_range", "cgpa_order")
write_csv(cgpa_rates, "cgpa_symptom_rates.csv")


# -------------------------------------------------------------------
# 2. GLOBAL MENTAL HEALTH DATASET
# -------------------------------------------------------------------

global_path = find_file(
    "global_mental_health.xlsx",
    "Mental health Depression disorder Data.xlsx",
)

print(f"Using global mental health dataset: {global_path}")

prevalence = pd.read_excel(global_path, sheet_name="prevalence-by-mental-and-substa")
prevalence.columns = [clean_col(c) for c in prevalence.columns]

prevalence = prevalence.rename(columns={
    "entity": "country",
    "code": "code",
    "year": "year",
    "anxiety_disorders": "anxiety",
    "depression": "depression",
    "schizophrenia": "schizophrenia",
    "bipolar_disorder": "bipolar",
    "eating_disorders": "eating_disorders",
    "drug_use_disorders": "drug_use",
    "alcohol_use_disorders": "alcohol_use",
})

for col in ["depression", "anxiety"]:
    if col not in prevalence.columns:
        possible = [c for c in prevalence.columns if col in c]
        if possible:
            prevalence = prevalence.rename(columns={possible[0]: col})

asean_countries = [
    "Malaysia", "Indonesia", "Singapore", "Thailand", "Vietnam",
    "Philippines", "Brunei", "Cambodia", "Laos", "Myanmar"
]

asean = prevalence[prevalence["country"].isin(asean_countries)].copy()
asean["is_malaysia"] = asean["country"].eq("Malaysia")

malaysia = prevalence[prevalence["country"].eq("Malaysia")].copy()

malaysia_trend = malaysia.melt(
    id_vars=["country", "code", "year"],
    value_vars=[c for c in ["depression", "anxiety"] if c in malaysia.columns],
    var_name="disorder",
    value_name="prevalence"
)

malaysia_trend["disorder"] = malaysia_trend["disorder"].map({
    "depression": "Depression",
    "anxiety": "Anxiety"
})

malaysia_trend["prevalence"] = pd.to_numeric(
    malaysia_trend["prevalence"], errors="coerce"
).round(3)

write_csv(malaysia_trend, "malaysia_trend.csv")

asean_depression = asean[["country", "code", "year", "depression", "is_malaysia"]].dropna().copy()
asean_depression = asean_depression.rename(columns={"depression": "prevalence"})
asean_depression["prevalence"] = pd.to_numeric(
    asean_depression["prevalence"], errors="coerce"
).round(3)

write_csv(asean_depression, "asean_depression_trend.csv")

latest_year = int(asean["year"].max())
asean_latest = asean[asean["year"].eq(latest_year)].copy()

lat_lon = {
    "Malaysia": (4.2105, 101.9758),
    "Indonesia": (-2.5489, 118.0149),
    "Singapore": (1.3521, 103.8198),
    "Thailand": (15.8700, 100.9925),
    "Vietnam": (14.0583, 108.2772),
    "Philippines": (12.8797, 121.7740),
    "Brunei": (4.5353, 114.7277),
    "Cambodia": (12.5657, 104.9910),
    "Laos": (19.8563, 102.4955),
    "Myanmar": (21.9162, 95.9560),
}

asean_latest["latitude"] = asean_latest["country"].map(lambda c: lat_lon.get(c, (None, None))[0])
asean_latest["longitude"] = asean_latest["country"].map(lambda c: lat_lon.get(c, (None, None))[1])
asean_latest["depression"] = pd.to_numeric(asean_latest["depression"], errors="coerce").round(3)
asean_latest["anxiety"] = pd.to_numeric(asean_latest["anxiety"], errors="coerce").round(3)

asean_latest = asean_latest.dropna(subset=["latitude", "longitude", "depression"])

write_csv(
    asean_latest[["country", "code", "year", "depression", "anxiety", "latitude", "longitude", "is_malaysia"]],
    "asean_latest_map.csv"
)

latest_malaysia = malaysia[malaysia["year"].eq(int(malaysia["year"].max()))].copy()

disorder_cols = [
    ("Depression", "depression"),
    ("Anxiety", "anxiety"),
    ("Bipolar disorder", "bipolar"),
    ("Eating disorders", "eating_disorders"),
    ("Schizophrenia", "schizophrenia"),
    ("Drug use disorders", "drug_use"),
    ("Alcohol use disorders", "alcohol_use"),
]

rows = []

for label, col in disorder_cols:
    if col in latest_malaysia.columns:
        value = pd.to_numeric(latest_malaysia[col].iloc[0], errors="coerce")
        if pd.notna(value):
            rows.append({
                "disorder": label,
                "prevalence": round(float(value), 3),
                "year": int(latest_malaysia["year"].iloc[0])
            })

write_csv(pd.DataFrame(rows), "malaysia_disorder_profile.csv")

try:
    age_df = pd.read_excel(global_path, sheet_name="prevalence-of-depression-by-age")
    age_df.columns = [clean_col(c) for c in age_df.columns]
    age_df = age_df.rename(columns={"entity": "country", "code": "code", "year": "year"})

    age_m = age_df[age_df["country"].eq("Malaysia")].copy()
    age_m = age_m[age_m["year"].eq(int(age_m["year"].max()))]

    age_cols = [
        c for c in age_m.columns
        if "years_old" in c or c in ["all_ages", "age_standardized"]
    ]

    age_rows = []

    for col in age_cols:
        label = col.replace("_", " ").replace("years old", "years").title()
        value = pd.to_numeric(age_m[col].iloc[0], errors="coerce")

        if pd.notna(value):
            age_rows.append({
                "age_group": label,
                "depression_prevalence": round(float(value), 3),
                "year": int(age_m["year"].iloc[0])
            })

    write_csv(pd.DataFrame(age_rows), "malaysia_depression_age_profile.csv")

except Exception as exc:
    print(f"Skipping age-profile sheet because of error: {exc}")


# -------------------------------------------------------------------
# 3. GHSH ADOLESCENT WARNING-SIGN DATASET
# -------------------------------------------------------------------

ghsh_path = find_file(
    "ghsh_adolescent.csv",
    "GHSH_Pooled_Data1.csv",
)

print(f"Using GHSH adolescent dataset: {ghsh_path}")

ghsh = pd.read_csv(ghsh_path)
ghsh.columns = [clean_col(c) for c in ghsh.columns]

ghsh["country"] = clean_text(ghsh["country"])
ghsh["sex"] = clean_text(ghsh["sex"]).str.title()
ghsh["age_group"] = clean_text(ghsh["age_group"])

for col in ghsh.columns:
    if col not in ["country", "age_group", "sex"]:
        ghsh[col] = pd.to_numeric(ghsh[col], errors="coerce")

malaysia_ghsh = ghsh[ghsh["country"].eq("Malaysia")].copy()

if malaysia_ghsh.empty:
    raise ValueError("No Malaysia rows found in GHSH dataset.")

indicator_map = {
    "attempted_suicide": ("Attempted suicide", "Warning sign"),
    "bullied": ("Bullied", "Warning sign"),
    "no_close_friends": ("No close friends", "Warning sign"),
    "had_fights": ("Had physical fights", "Warning sign"),
    "got_seriously_injured": ("Seriously injured", "Warning sign"),
    "smoke_cig_currently": ("Currently smokes", "Risk behaviour"),
    "currently_drink_alcohol": ("Currently drinks alcohol", "Risk behaviour"),
    "have_understanding_parents": ("Understanding parents", "Protective support"),
}

warning_rows = []

for col, (label, kind) in indicator_map.items():
    if col in malaysia_ghsh.columns:
        value = malaysia_ghsh[col].mean(skipna=True)

        if pd.notna(value):
            warning_rows.append({
                "indicator": label,
                "kind": kind,
                "value": round(float(value), 1),
                "year": int(malaysia_ghsh["year"].dropna().max()),
            })

warning_df = pd.DataFrame(warning_rows)
warning_df["order"] = range(1, len(warning_df) + 1)
write_csv(warning_df, "adolescent_warning_signs.csv")

if "attempted_suicide" in malaysia_ghsh.columns:
    attempt = malaysia_ghsh[
        ["country", "year", "age_group", "sex", "attempted_suicide"]
    ].dropna().copy()

    attempt = attempt.rename(columns={"attempted_suicide": "value"})
    attempt["label"] = attempt["value"].map(lambda x: f"{x:.1f}%")

    write_csv(attempt, "attempted_suicide_age_sex.csv")

if "attempted_suicide" in ghsh.columns:
    country_attempt = (
        ghsh.groupby("country", as_index=False)["attempted_suicide"]
        .mean()
        .dropna()
        .rename(columns={"attempted_suicide": "value"})
    )

    country_attempt["value"] = country_attempt["value"].round(1)
    country_attempt["is_malaysia"] = country_attempt["country"].eq("Malaysia")
    country_attempt = country_attempt.sort_values("value", ascending=False)

    write_csv(country_attempt, "adolescent_country_attempted_suicide.csv")


# -------------------------------------------------------------------
# 4. CUSTOM PRESSURE PROFILE SUMMARY
# -------------------------------------------------------------------

malaysia_latest_for_profile = latest_malaysia.iloc[0] if len(latest_malaysia) else None


def get_kpi(short_label):
    row = kpis[kpis["short_label"].eq(short_label)]
    return float(row["percent"].iloc[0]) if len(row) else None


def get_warning(label):
    row = warning_df[warning_df["indicator"].eq(label)]
    return float(row["value"].iloc[0]) if len(row) else None


pressure_rows = [
    {"order": 1, "indicator": "Student depression", "value": get_kpi("Depression"), "source_group": "Student survey"},
    {"order": 2, "indicator": "Student anxiety", "value": get_kpi("Anxiety"), "source_group": "Student survey"},
    {"order": 3, "indicator": "Student panic attacks", "value": get_kpi("Panic attacks"), "source_group": "Student survey"},
    {"order": 4, "indicator": "Student treatment gap", "value": get_kpi("Treatment gap"), "source_group": "Student survey"},
    {"order": 5, "indicator": "Adolescents bullied", "value": get_warning("Bullied"), "source_group": "Adolescent survey"},
    {"order": 6, "indicator": "Adolescents attempted suicide", "value": get_warning("Attempted suicide"), "source_group": "Adolescent survey"},
]

if malaysia_latest_for_profile is not None:
    pressure_rows.extend([
        {
            "order": 7,
            "indicator": "Malaysia depression prevalence",
            "value": round(float(malaysia_latest_for_profile.get("depression", 0)), 1),
            "source_group": "Global estimate"
        },
        {
            "order": 8,
            "indicator": "Malaysia anxiety prevalence",
            "value": round(float(malaysia_latest_for_profile.get("anxiety", 0)), 1),
            "source_group": "Global estimate"
        },
    ])

pressure = pd.DataFrame(pressure_rows).dropna()
pressure["label"] = pressure["value"].map(lambda x: f"{x:.1f}%")

write_csv(pressure, "pressure_profile.csv")

print("\nCleaning complete. Processed files are ready in data/processed/")