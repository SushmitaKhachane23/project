"""
ITMS Simulation - Integrated Traffic Management System (Individual Hackathon Submission)

Program description:
This script simulates a basic Integrated Traffic Management System (ITMS) focused on
detecting common driver violations in a metro city: speeding and red-light crossing.
It aggregates violations, computes fines, and prints a summary dashboard.

Input format (stdin or piped file):
Each line represents an event with fields separated by commas:
timestamp,vehicle_id,location,speed(km/h),signal_state,action
- timestamp: ISO format or any string
- vehicle_id: e.g., KA01AB1234
- location: string identifier for the sensor location
- speed: integer or float (km/h)
- signal_state: GREEN or RED (state of the traffic signal when vehicle passed)
- action: PASS or TURN or LANE_CHANGE (used for extensibility)

Example line:
2025-11-05T09:12:33,KA01AB1234,MG_Road_01,68,RED,PASS

How to run:
$ python3 itms_simulation.py < events.csv
or
$ cat events.csv | python3 itms_simulation.py

What it does:
- Loads a small 'policy' with speed limits per location (default 50 km/h).
- Detects speeding violations (speed > speed_limit + tolerance).
- Detects red-light violations (signal_state == RED and action == PASS).
- Assigns fines: speeding -> ₹100 per km/h over limit (rounded), red-light -> ₹2000 fixed.
- Prints each violation and a final dashboard with counts and total fines per vehicle and overall.

This is a simplified simulation intended as a demonstrator for a hackathon submission.
"""

import sys
from collections import defaultdict
import math

# Policy (could be replaced by config or DB)
DEFAULT_SPEED_LIMIT = 50  # km/h
SPEED_TOLERANCE = 5  # km/h (below this no fine)
RED_LIGHT_FINE = 2000  # INR
SPEED_FINE_PER_KMPH = 100  # INR per km/h over the limit (rounded)

# Example location-specific limits (override default)
LOCATION_SPEED_LIMITS = {
    "MG_Road_01": 50,
    "Outer_Ring_2": 80,
    "School_Zone_A": 30,
    "Highway_7": 100,
}

def parse_event(line):
    parts = [p.strip() for p in line.strip().split(",")]
    if len(parts) < 6:
        return None
    timestamp, vehicle_id, location, speed_s, signal_state, action = parts[:6]
    try:
        speed = float(speed_s)
    except ValueError:
        return None
    return {
        "timestamp": timestamp,
        "vehicle_id": vehicle_id,
        "location": location,
        "speed": speed,
        "signal_state": signal_state.upper(),
        "action": action.upper()
    }

def get_speed_limit(location):
    return LOCATION_SPEED_LIMITS.get(location, DEFAULT_SPEED_LIMIT)

def evaluate_event(evt):
    violations = []
    speed_limit = get_speed_limit(evt["location"])
    if evt["speed"] > speed_limit + SPEED_TOLERANCE:
        over = evt["speed"] - speed_limit
        over_rounded = math.ceil(over)
        fine = over_rounded * SPEED_FINE_PER_KMPH
        violations.append(("SPEEDING", over_rounded, fine, f"speed {evt['speed']} > limit {speed_limit}"))
    if evt["signal_state"] == "RED" and evt["action"] == "PASS":
        violations.append(("RED_LIGHT", None, RED_LIGHT_FINE, "Passed on RED"))
    return violations

def main():
    vehicles = defaultdict(lambda: {"violations": [], "total_fine": 0})
    overall_counts = defaultdict(int)
    total_fines = 0
    input_lines = sys.stdin.read().strip().splitlines()
    if not input_lines:
        # Print sample usage and sample input
        sample = [
            "2025-11-05T09:12:33,KA01AB1234,MG_Road_01,68,RED,PASS",
            "2025-11-05T09:13:10,KA01CD5678,MG_Road_01,55,GREEN,PASS",
            "2025-11-05T09:15:00,KA02EF9999,Outer_Ring_2,95,GREEN,PASS",
            "2025-11-05T09:16:20,KA01AB1234,School_Zone_A,45,GREEN,PASS",
        ]
        print("No input detected. Sample input (pipe these lines to the program):\n")
        for s in sample:
            print(s)
        return

    for line in input_lines:
        evt = parse_event(line)
        if not evt:
            continue
        violations = evaluate_event(evt)
        if violations:
            for vtype, over, fine, desc in violations:
                vehicles[evt["vehicle_id"]]["violations"].append({
                    "type": vtype, "over": over, "fine": fine, "desc": desc, "timestamp": evt["timestamp"], "location": evt["location"]
                })
                vehicles[evt["vehicle_id"]]["total_fine"] += fine
                overall_counts[vtype] += 1
                total_fines += fine

    # Print violations per vehicle
    print("=== Violations Report ===")
    for vid, data in vehicles.items():
        if not data["violations"]:
            continue
        print(f"Vehicle: {vid}  | Total Fine: ₹{data['total_fine']}  | Violations: {len(data['violations'])}")
        for v in data["violations"]:
            if v["type"] == "SPEEDING":
                print(f"  - {v['timestamp']} | {v['location']} | SPEEDING by {v['over']} km/h -> Fine ₹{v['fine']} ({v['desc']})")
            else:
                print(f"  - {v['timestamp']} | {v['location']} | {v['type']} -> Fine ₹{v['fine']} ({v['desc']})")
        print()

    # Dashboard
    print("=== Dashboard ===")
    print(f"Total vehicles with violations: {len(vehicles)}")
    print(f"Total fines collected: ₹{total_fines}")
    for k, cnt in overall_counts.items():
        print(f"  {k}: {cnt}")
    print("\nPer-vehicle summary:")
    for vid, data in vehicles.items():
        print(f"  {vid}: Violations={len(data['violations'])}, TotalFine=₹{data['total_fine']}")

if __name__ == '__main__':
    main()
