required_keys = [
    "algorithms",
    "data_lifetime",
    "mission_impact",
    "exposure",
    "upgrade_difficulty"
]

def validate_system(system):
    for key in required_keys:
        if key not in system:
            print(f"[WARNING] Missing {key} in (system.get('name', 'Unknown'))")
            return False
        return True

def quantum_vulnerability_score(system):
    algorithms = system

    vulnerable = ["RSA", "DH", "ECDH", "ECC", "DSA", "ECDSA"]
    score = 0
    for alg in algorithms:
        if alg in vulnerable:
            score += 2

    return min(score, 5)

def compute_priority(system):
    v = quantum_vulnerability_score(system)
    l = min(system["data_lifetime"], 10) / 2
    m = system["mission_impact"]
    e = system["exposure"]
    u = system["upgrade_difficulty"]

    return round(v + l + m + e + u, 2)


systems = [
    {
        "name": "Drone System",
        "algorithms": ["RSA", "ECDH", "AES"],
        "data_lifetime": 10,
        "mission_impact": 5,
        "exposure": 4,
        "upgrade_difficulty": 4
    },
    {
        "name": "Public Website",
        "algorithms": ["RSA", "AES"],
        "protocols": ["TLS"],
        "data_lifetime": 0.01,
        "mission_impact": 1,
        "exposure": 3,
        "upgrade_difficulty": 1
    }
]

for s in systems:
    if not validate_system(s):
        continue

    s["priority"] = compute_priority(s)

for s in systems:
    print(s["name"], "Priority:", s["priority"])

import random

def simulate_risk(system, trials=1000):
    compromised = 0

    for _ in range(trials):
        tQ = random.uniform(1,30) # quantum arrives in 1-30 years

        if system["data_lifetime"] >= tQ: 
            compromised += 1

    return compromised / trials

for s in systems:
    risk = simulate_risk(s)
    print(s["name"], "Risk:", round(risk, 2))

import matplotlib.pyplot as plt # type: ignore

names = [s["name"] for s in systems]
risks = [simulate_risk(s) for s in systems]


plt.bar(names, risks)
plt.title("Quantum Risk by System")
plt.ylabel("Probability of Compromise")
plt.show()

def recommendation(system):
    if system["priority"] > 15:
        return "Immediate PQC migration"
    elif system["priority"] > 10:
        return "Hybrid cryptography"
    else:
        return "Monitor"
    
# functions
def classify(system):
    if system["priority"] > 15:
        return "CRITICAL"
    elif system["priority"] > 10:
        return "HIGH"
    else:
        return "LOW"

# main loop
for s in systems:
    print(f"{s['name']}")
    print(f"  Priority: {s['priority']}")
    print(f"  Risk: {round(simulate_risk(s), 2)}")
    print(f"  Recommendation: {recommendation(s)}")
    print(f"  Category: {classify(s)}\n")

    
print(f"Category: {classify(s)}\n")