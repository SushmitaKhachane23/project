
DEFAULT_SPEED_LIMIT = 50  
SPEED_TOLERANCE = 5  
RED_LIGHT_FINE = 2000  
SPEED_FINE_PER_KMPH = 100  


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
