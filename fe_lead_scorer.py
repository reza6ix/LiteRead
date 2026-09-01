#!/usr/bin/env python3
"""
Final Expense Lead Scorer
--------------------------
Scores and ranks a purchased lead list (CSV) against the Final Expense
target clientele checklist.

HOW TO USE WITH CLAUDE CODE:
1. Drop your leads CSV in the same folder.
2. Tell Claude Code: "Open the COLUMN MAP below, update the values to
   match my CSV's actual column headers (leave as None if I don't have
   that data), then run: python fe_lead_scorer.py leads.csv scored.csv"
3. Output CSV is sorted best-fit first; screened-out leads sink to the
   bottom with a reason attached.
"""

import csv
import sys

# ============================================================
# 1. COLUMN MAP — point these at your CSV's actual column names.
#    Set a field to None if your list doesn't have that data;
#    the script just skips that criterion instead of erroring.
# ============================================================
COLUMNS = {
    "age": "Age",
    "annual_income": "Est_Income",
    "homeowner": "Homeowner",
    "has_group_life": None,
    "marital_status": "Marital_Status",
    "has_children": "Has_Children",
    "health_flag": "Health_Condition",
    "hospice_flag": None,
    "existing_burial_policy": None,
    "retired": "Retired",
    "turning_65_soon": None,
}

# ============================================================
# 2. SCORING WEIGHTS — tune how strongly each signal moves a
#    lead up in priority. Screen-outs are separate and always
#    sink a lead to the bottom regardless of score.
# ============================================================
WEIGHTS = {
    "age_sweet_spot": 25,
    "age_in_range": 10,
    "income_fit": 15,
    "homeowner_or_renter": 5,
    "no_group_life": 10,
    "widowed": 15,
    "retired": 10,
    "health_signal_present": 10,
    "has_children": 5,
    "turning_65": 10,
}


def get(row, key):
    col = COLUMNS.get(key)
    if col is None or col not in row:
        return None
    val = row[col].strip() if row[col] else ""
    return val if val else None


def is_yes(val):
    return val is not None and val.strip().lower() in ("y", "yes", "true", "1")


def score_lead(row):
    score = 0
    reasons = []
    screen_out = False
    screen_reasons = []

    # --- Age ---
    age_val = get(row, "age")
    age = None
    if age_val:
        try:
            age = int(float(age_val))
        except ValueError:
            age = None
    if age is not None:
        if age < 50:
            screen_out = True
            screen_reasons.append(f"age {age} < 50")
        elif 60 <= age <= 75:
            score += WEIGHTS["age_sweet_spot"]
            reasons.append("age in sweet spot 60-75")
        elif 50 <= age <= 85:
            score += WEIGHTS["age_in_range"]
            reasons.append("age in acceptable range")
        else:
            screen_out = True
            screen_reasons.append(f"age {age} above typical issue cap")

    # --- Income ---
    income_val = get(row, "annual_income")
    if income_val:
        try:
            income = float(income_val.replace(",", "").replace("$", ""))
            if income <= 45000:
                score += WEIGHTS["income_fit"]
                reasons.append("income in typical FE buyer range")
            elif income >= 150000:
                screen_out = True
                screen_reasons.append("high income - likely self-funds")
        except ValueError:
            pass

    # --- Homeowner/renter (presence just confirms modest-asset profile) ---
    if get(row, "homeowner") is not None:
        score += WEIGHTS["homeowner_or_renter"]

    # --- Group life ---
    glife = get(row, "has_group_life")
    if glife is not None and not is_yes(glife):
        score += WEIGHTS["no_group_life"]
        reasons.append("no employer group life")

    # --- Marital status ---
    marital = get(row, "marital_status")
    if marital and "widow" in marital.lower():
        score += WEIGHTS["widowed"]
        reasons.append("recently widowed signal")

    # --- Retired ---
    if is_yes(get(row, "retired")):
        score += WEIGHTS["retired"]
        reasons.append("retired")

    # --- Health signal ---
    health = get(row, "health_flag")
    if health and health.lower() not in ("n", "no", "none", "false"):
        score += WEIGHTS["health_signal_present"]
        reasons.append("health condition on file")

    # --- Children ---
    if is_yes(get(row, "has_children")):
        score += WEIGHTS["has_children"]
        reasons.append("has adult children")

    # --- Turning 65 ---
    if is_yes(get(row, "turning_65_soon")):
        score += WEIGHTS["turning_65"]
        reasons.append("turning 65 soon")

    # --- Screen-outs: hospice / terminal ---
    if is_yes(get(row, "hospice_flag")):
        screen_out = True
        screen_reasons.append("hospice/terminal flag")

    # --- Screen-outs: existing adequate coverage ---
    if is_yes(get(row, "existing_burial_policy")):
        screen_out = True
        screen_reasons.append("already has burial/whole life coverage")

    return score, screen_out, reasons, screen_reasons


def main(input_path, output_path):
    with open(input_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = reader.fieldnames

    results = []
    for row in rows:
        score, screen_out, reasons, screen_reasons = score_lead(row)
        row_out = dict(row)
        row_out["fe_score"] = score
        row_out["screen_out"] = "YES" if screen_out else ""
        row_out["match_reasons"] = "; ".join(reasons)
        row_out["screen_out_reasons"] = "; ".join(screen_reasons)
        results.append(row_out)

    results.sort(key=lambda r: (r["screen_out"] == "YES", -r["fe_score"]))

    out_fields = fieldnames + ["fe_score", "screen_out", "match_reasons", "screen_out_reasons"]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=out_fields)
        writer.writeheader()
        writer.writerows(results)

    total = len(results)
    screened = sum(1 for r in results if r["screen_out"] == "YES")
    print(f"Scored {total} leads. {screened} screened out. {total - screened} ranked and ready.")
    print(f"Output written to {output_path}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python fe_lead_scorer.py <input.csv> <output.csv>")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
