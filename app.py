import streamlit as st
import json
import pandas as pd
import matplotlib.pyplot as plt
from streamlit_autorefresh import st_autorefresh
import numpy as np
import networkx as nx

def tls_upgrade_needed(system):
    return "TLS 1.2" in system.get("protocols", [])

st.set_page_config(layout="wide") 

# ✅ UI TITLE FIRST
st.title("🔐 PQC Cryptographic Inventory Dashboard")
st.write("Analyze systems and prioritize post-quantum cryptography migration.")

@st.cache_data
def simulate_risk(data_lifetime, max_years, trials=300):

    data_lifetime = data_lifetime or 0

    tQ = np.random.uniform(1, max_years, trials)

    return float(
        np.mean(data_lifetime >= tQ)
    )


tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10, tab11, tab12, tab13, tab14 = st.tabs([
    "📋 Inventory",
    "⚠️ Risk Analysis",
    "🧠 PQC Strategy",
    "📊 Analytics",
    "🚨 Alerts",
    "📦 Export & Reports",
    "📈 Executive Summary",
    "🛰️ HNDL Intelligence",
    "🪖 Military Readiness",
    "🕵️ Intelligence Risk",
    "🤝 Coalition Readiness",
    "📜 NIST Compliance",
    "📅 Campaign Planner",
    "💰 Cost Modeling"
])

st.sidebar.header("⚙️ Filters")

st.sidebar.subheader("Network Selection")
network_filter = st.sidebar.multiselect(
    "Select Network Types",
    ["enterprise", "operational", "tactical", "satcom", "manet"],
    default=["enterprise", "operational", "tactical", "satcom", "manet"]
)

st.sidebar.subheader("Priority Levels")
selected_categories = st.sidebar.multiselect(
    "Select Priority Categories",
    ["CRITICAL", "HIGH", "MEDIUM", "LOW"],
    default=["CRITICAL", "HIGH", "MEDIUM", "LOW"]
)

st.sidebar.divider()
st.sidebar.subheader("📂 Upload Dataset")

uploaded_file = st.sidebar.file_uploader(
    "Upload JSON or CSV",
    type=["json", "csv"]
)

st.sidebar.divider()

max_years = st.sidebar.slider("Quantum Arrival (Years)", 5, 50, 30)
future_shift = st.sidebar.slider("Threat Increase", 0, 5, 0)

def load_uploaded_file(file):
    if file is None:
        return None

    if file.type == "application/json":
        return json.load(file)

    elif file.type == "text/csv":
        df = pd.read_csv(file)

        # Convert CSV → system dict format
        systems = df.to_dict(orient="records")

        # Ensure lists for expected fields
        for s in systems:
            if isinstance(s.get("algorithms"), str):
                s["algorithms"] = s["algorithms"].split(",")
            if isinstance(s.get("protocols"), str):
                s["protocols"] = s["protocols"].split(",")

        return systems

    return None

def validate_systems(systems):
    required = ["name", "algorithms", "protocols"]

    for s in systems:
        for key in required:
            if key not in s:
                st.error(f"Missing field: {key}")
                return False
    return True


# ✅ Functions
def quantum_vulnerability_score(algorithms):
    vulnerable = {"RSA", "ECC", "DH", "ECDH", "ECDSA"}
    return sum(2 for alg in algorithms if alg in vulnerable)

def protocol_risk(protocols):
    risky = {"TLS 1.2", "SSH", "IPsec"}
    return sum(1 for p in protocols if p in risky)

def hndl_risk(system):
    if system.get("data_lifetime", 0) > 15:
        return 5
    elif system.get("data_lifetime", 0) > 5:
        return 3
    return 1

DOMAIN_WEIGHT = {
    "enterprise": 1,
    "intelligence": 2,
    "satcom": 3,
    "coalition": 3,
    "tactical": 4,
    "platform": 4,
    "operational": 3
}

def compute_priority(system):

    v = quantum_vulnerability_score(
        system.get("algorithms", [])
    )

    l = system.get("data_lifetime", 0)
    m = system.get("mission_impact", 0)
    e = system.get("exposure", 0)
    u = system.get("upgrade_difficulty", 0)

    net = network_penalty(system)

    priority = (
        v + l + m + e + u +
        net +
        protocol_risk(system.get("protocols", []))
    )

    priority += high_value_asset_score(system)
    priority += agility_penalty(system)
    priority += hndl_risk(system)
    priority += pqc_overhead_penalty(system)
    priority += mission_criticality_score(system)

    priority += migration_difficulty(system) * 2

    priority *= DOMAIN_WEIGHT.get(
        system.get("network_domain", "enterprise"),
        1
    )

    return round(priority, 2)

def mission_criticality_score(system):
    scores = {
        "nuclear_c2": 10,
        "joint_fire_control": 9,
        "air_defense": 8,
        "satcom": 7,
        "intelligence": 7,
        "enterprise_it": 3
    }

    mission = system.get("mission_type", "enterprise_it")

    return scores.get(mission, 1)

def performance_score(system):
    base_latency = 0.05
    compute_factor = 1 if system.get("compute") == "high" else 2
    return base_latency * compute_factor

def threat_surface(system):

    score = 0

    exposure = system.get("exposure", 0) or 0

    if exposure > 3:
        score += 3

    if system.get("interoperability") == "high":
        score += 2

    if system.get("network_type") in ["satcom", "tactical"]:
        score += 3

    return score

def extract_features(system):
    return {
        "alg_count": len(system.get("algorithms", [])),
        "lifetime": system.get("data_lifetime", 0),
        "impact": system.get("mission_impact", 0),
        "exposure": system.get("exposure", 0),
        "difficulty": system.get("upgrade_difficulty", 0),
        "is_tactical": 1 if system.get("network_type") == "tactical" else 0,
        "is_satcom": 1 if system.get("network_type") == "satcom" else 0,
        "low_compute": 1 if system.get("compute") == "low" else 0,
    }

def generate_cbom(system):

    return {

        "system": system["name"],

        "network_domain":
        system.get("network_domain"),

        "current_algorithms":
        system.get("algorithms"),

        "recommended_pqc":
        recommended_crypto(system),

        "migration_phase":
        system.get("phase"),

        "difficulty":
        migration_difficulty(system),

        "hndl_score":
        system.get("hndl_score"),

        "readiness":
        system.get(
            "readiness_category"
        )
    }


def fast_risk(system):
    return min(
    (system.get("data_lifetime", 0) or 0)
    / max_years,
    1.0
)
    
def hybrid_needed(system):
    if not system["feasible"]:
        return True
    return False

def classify_system(priority, feasible):
    if priority >= 25:
        return "CRITICAL"
    elif priority >= 18:
        return "HIGH"
    elif priority >= 10:
        return "MEDIUM"
    else:
        return "LOW"

def classification_score(level):
    mapping = {
        "public": 1,
        "internal": 2,
        "confidential": 3,
        "secret": 4,
        "top_secret": 5
    }
    return mapping.get(level, 1)

def network_penalty(system):
    score = 0

    # Bandwidth constraints (PQC larger keys hurt)
    if system.get("bandwidth") == "low":
        score += 4
    elif system.get("bandwidth") == "medium":
        score += 2

    # Latency constraints (handshake overhead matters)
    if system.get("latency") == "high":
        score += 3
    elif system.get("latency") == "medium":
        score += 1

    # Compute constraints (PQC signatures cost more)
    if system.get("compute") == "low":
        score += 4
    elif system.get("compute") == "medium":
        score += 2

    # Long platform lifetime = higher urgency
    if system.get("platform_lifetime") == "long":
        score += 3

    # Interoperability (coalition / legacy issues)
    if system.get("interoperability") == "high":
        score += 2

    return score

def pqc_feasibility(system):
    if system.get("network_type") in ["tactical", "manet"] and system.get("compute") == "low":
        return False
    return True


def analyze_systems(file_path):
    with open(file_path, "r") as f:
        systems = json.load(f)

    results = []

    for system in systems:
        priority = compute_priority(system)
        risk = simulate_risk(
    system.get("data_lifetime"),
    max_years
)
        feasible = pqc_feasibility(system)
        category = classify_system(priority, feasible)

        recommendation = generate_recommendation(system, feasible, category)

        results.append({
            "name": system.get("name"),
            "priority": round(priority, 2),
            "risk": round(risk, 2),
            "feasible": feasible,
            "category": category,
            "recommendation": recommendation
        })

    return results

def generate_recommendation(system, feasible, category):
    if not feasible:
        return "Use hybrid crypto or delay PQC—hardware constraints"

    if system.get("network_type") == "enterprise":
        return "Immediate PQC migration (TLS, PKI, VPN)"

    if system.get("network_type") == "operational":
        return "Adopt hybrid PQC + classical systems"

    if system.get("network_type") == "tactical":
        return "Optimize PQC (compressed keys, lightweight protocols)"

    if system.get("network_type") == "satcom":
        return "Minimize handshake overhead, prioritize latency"

    return "Monitor and plan migration"


def migration_phase(system):
    if system.get("category") == "CRITICAL":
        return "Phase 3: Prioritized Migration"
    elif system.get("category") == "HIGH":
        return "Phase 2: Pilot Migration"
    elif system.get("category") == "MEDIUM":
        return "Phase 4: Signature Migration"
    else:
        return "Phase 5: Full Migration"


def high_value_asset_score(system):
    return 5 if system.get("high_value_asset", False) else 0


def agility_penalty(system):
    if system.get("crypto_agility", "low") == "low":
        return 4
    elif system.get("crypto_agility", "low") == "medium":
        return 2
    return 0

def pqc_overhead_penalty(system):
    if system.get("network_type") in ["tactical", "manet"]:
        return 4
    if system.get("network_type") == "satcom":
        return 2
    return 1


def recommended_crypto(system):

    if (
        system["classification"]
        == "top_secret"
    ):
        return (
            "ML-KEM + ML-DSA"
        )

    if (
        system["network_type"]
        == "satcom"
    ):
        return (
            "ML-KEM-768 + Falcon"
        )

    if (
        system["network_type"]
        == "tactical"
    ):
        return (
            "ML-KEM-512 + Falcon"
        )

    return (
        "ML-KEM-768 + ML-DSA"
    )


def assign_architecture(system):
    if system.get("classification") in ["top_secret", "secret"]:
        return "HSM (Hardware Security Module)"
    elif system.get("network_type") == "enterprise":
        return "Transparent Proxy (Recommended)"
    elif system.get("network_type") == "tactical":
        return "Middleware Layer (Lightweight)"
    else:
        return "Inline Encryption"

def deployment_strategy(system):
    if system.get("category") == "CRITICAL":
        return "Immediate Hybrid PQC Deployment"
    elif system.get("category") == "HIGH":
        return "Pilot PQC Deployment"
    else:
        return "Planned Migration"

@st.cache_data
def generate_cbom_all(systems, shift):
    def _shift(s):
        shifted = dict(s)
        shifted["exposure"] = shifted.get("exposure", 0) + shift
        return generate_cbom(shifted)

    return [_shift(s) for s in systems]

scenario = st.selectbox(
    "Adversary",
    [
        "Regional Actor",
        "Near Peer",
        "Nation State"
    ]
)

threat_modifier = {
    "Regional Actor": 1,
    "Near Peer": 2,
    "Nation State": 3
}

future_shift += threat_modifier[scenario]

def crypto_agility_maturity(system):

    maturity = {
        "hardcoded": 1,
        "limited": 2,
        "agile": 3,
        "hybrid": 4,
        "dynamic": 5
    }

    return maturity.get(
        system.get("crypto_agility", "limited"),
        2
    )

def hndl_intelligence(system):

    data_lifetime = system.get("data_lifetime", 0) or 0
    exposure = system.get("exposure", 0) or 0

    return (
        data_lifetime
        * exposure
        * classification_score(
            system.get("classification", "public")
        )
    )

def satcom_readiness(system):
    if system.get("network_type") != "satcom":
        return None

    score = 0
    if system.get("bandwidth") == "high":
        score += 3
    if system.get("compute") == "high":
        score += 3
    if system.get("latency") == "low":
        score += 3

    return score

def tactical_readiness(system):
    score = 0
    if system.get("compute") == "high":
        score += 3
    if system.get("bandwidth") == "high":
        score += 3
    if system.get("latency") == "low":
        score += 3
    return score

def military_architecture(system):
    if system.get("mission_type", "enterprise_it") == "nuclear_c2":
        return "Kyber + Dilithium + HSM"
    if system.get("network_type") == "satcom":
        return "Hybrid Satellite PQC"
    if system.get("network_type") == "tactical":
        return "Lightweight Hybrid PQC"
    return "Enterprise PQC Stack"

def interoperability_risk(system):
    risk = 0
    for dep in system.get("dependencies", []):
        if "PKI" in dep:
            risk += 4
        elif "SATCOM" in dep:
            risk += 3
        else:
            risk += 2
    return risk

def compliance(system):
    score = 100
    vulnerable = {"RSA", "ECC", "ECDH", "ECDSA"}
    for alg in system.get("algorithms", []):
        if alg in vulnerable:
            score -= 15
    return max(score, 0)

def military_readiness_score(system):
    score = 0
    score += system.get("agility_maturity", 0)
    score += system.get("compliance", 0) / 10
    if system.get("satcom_score"):
        score += system["satcom_score"]
    if system.get("tactical_score"):
        score += system["tactical_score"]
    score -= system.get("interop_risk", 0) / 2
    return round(score, 1)

def readiness_category(score):

    if score >= 15:
        return "READY"

    elif score >= 8:
        return "PARTIAL"

    return "AT RISK"

def strategic_archive_risk(system):

    classification = classification_score(
        system.get("classification","public")
    )

    return (
        system.get("data_lifetime",0)
        * classification
        * system.get("exposure",0)
    )

def migration_difficulty(system):

    weights = {
    "enterprise": 1,
    "intelligence": 2,
    "satcom": 3,
    "coalition": 3,
    "tactical": 4,
    "platform": 4,
    "operational": 3
}

    return weights.get(
        system.get("network_domain","enterprise"),
        1
    )

def coalition_risk(system):

    risk = 0

    if system.get("network_domain") == "coalition":
        risk += 5

    risk += interoperability_risk(system)

    return risk


def coalition_readiness(system):

    score = 100

    score -= min(system.get("coalition_risk", 0) * 5, 50)

    if system.get("compliance", 0) < 90:
        score -= 15

    return max(score, 0)

def coalition_category(score):
    if score >= 75:
        return "READY"
    elif score >= 50:
        return "PARTIAL"
    return "AT RISK"

def migration_cost(system):
    base = 50000

    return (
        base *
        system.get("upgrade_difficulty", 1) *
        migration_difficulty(system)
    )

def risk_reduction(system):

    return round(
        system["priority"]
        * system["risk"],
        2
    )

def migration_roi(system):

    cost = system["migration_cost"]

    if cost == 0:
        return 0

    return round(
        system["risk_reduction"]
        / cost,
        6
    )

def sustainment_risk(system):

    return (
        system.get("platform_age",0)
        + system.get("upgrade_difficulty",0)
        + (
            5 if system.get("compute") == "low"
            else 0
        )
    )

def satcom_overhead(system):
    if (
        system.get("network_type")
        != "satcom"
    ):
        return None

    return {
        "Latency Increase": "22%",
        "Bandwidth Increase": "18%",
        "Handshake Increase": "35%"
    }


def process_systems(systems, max_years):
    processed = []

    for s in systems:
        s = dict(s)

        s.setdefault("network_type", "enterprise")
        s.setdefault("network_domain", "enterprise")
        s.setdefault("mission_type", "enterprise_it")

        s["data_lifetime"] = s.get("data_lifetime") or 0
        s["exposure"] = s.get("exposure") or 0
        s["mission_impact"] = s.get("mission_impact") or 0
        s["upgrade_difficulty"] = s.get("upgrade_difficulty") or 0

        s.setdefault("algorithms", [])
        s.setdefault("protocols", [])
        s.setdefault("dependencies", [])

        s["agility_maturity"] = crypto_agility_maturity(s)
        s["hndl_score"] = hndl_intelligence(s)
        s["satcom_score"] = satcom_readiness(s)
        s["tactical_score"] = tactical_readiness(s)
        s["mil_architecture"] = military_architecture(s)
        s["interop_risk"] = interoperability_risk(s)
        s["compliance"] = compliance(s)
        s["military_readiness"] = military_readiness_score(s)
        s["readiness_category"] = readiness_category(s["military_readiness"])

        s["architecture"] = assign_architecture(s)
        s["latency"] = performance_score(s)
        s["threat"] = threat_surface(s)
        s["priority"] = compute_priority(s)
        s["risk"] = simulate_risk(s.get("data_lifetime", 0), max_years)
        s["data_lifetime"] = min(s.get("data_lifetime", 0), max_years)
        s["feasible"] = pqc_feasibility(s)
        s["category"] = classify_system(s["priority"], s["feasible"])
        s["deployment"] = deployment_strategy(s)
        s["recommendation"] = generate_recommendation(
            s, s["feasible"], s["category"]
        )
        s["archive_risk"] = strategic_archive_risk(s)
        s["coalition_risk"] = coalition_risk(s)
        s["coalition_readiness"] = coalition_readiness(s)
        s["coalition_category"] = coalition_category(s["coalition_readiness"])
        s["migration_cost"] = migration_cost(s)
        s["risk_reduction"] = risk_reduction(s)
        s["roi"] = migration_roi(s)
        s["phase"] = migration_phase(s)
        s["sustainment_risk"] = sustainment_risk(s)

        processed.append(s)

    return processed

def train_simple_model(systems):
    if not systems:
        return None

    totals = {
        "alg_count": 0,
        "lifetime": 0,
        "impact": 0,
        "exposure": 0,
        "difficulty": 0,
        "is_tactical": 0,
        "is_satcom": 0,
        "low_compute": 0,
    }
    total_risk = 0

    for s in systems:
        f = extract_features(s)
        for k in totals:
            totals[k] += f[k]
        total_risk += s.get("risk", 0)

    n = len(systems)
    weights = {k: (totals[k] / n) for k in totals}
    avg_risk = total_risk / n if n else 0

    return weights, avg_risk


def predict_simple_ml(system, model):
    if not model:
        return None

    weights, avg_risk = model
    features = extract_features(system)
    score = sum(features.get(k, 0) * weights.get(k, 0) for k in weights)
    baseline = sum(weights.values()) or 1
    return round((score / baseline) * avg_risk, 2)


def load_data():
    """Load default sample data for systems."""
    return [
        {
    "name": "Enterprise VPN Gateway",
    "mission_type": "enterprise_it",

    "algorithms": ["RSA", "AES"],
    "protocols": ["TLS 1.2"],
    "data_lifetime": 20,
    "mission_impact": 5,
    "exposure": 4,
    "upgrade_difficulty": 2,
    "network_type": "enterprise",
    "bandwidth": "high",
    "latency": "low",
    "compute": "high",
    "platform_lifetime": "long",
    "interoperability": "high",
    "classification": "confidential",
    "crypto_agility": "medium",
    "high_value_asset": True,
    "network_domain": "enterprise"
},
        {
            "name": "Tactical Radio Network",
            "algorithms": ["ECC"],
            "protocols": ["IPsec"],
            "data_lifetime": 15,
            "mission_impact": 5,
            "exposure": 3,
            "upgrade_difficulty": 4,
            "network_type": "tactical",
            "bandwidth": "low",
            "latency": "high",
            "compute": "low",
            "platform_lifetime": "long",
            "interoperability": "high",
            "classification": "secret",
            "crypto_agility": "low",
            "high_value_asset": True,
            "feasible": False,
            "network_domain": "tactical"
        },      
        {
    "name": "SATCOM Gateway",
    "mission_type": "satcom",
    "network_type": "satcom",
    "algorithms": ["RSA"],
    "protocols": ["TLS 1.2"],
    "data_lifetime": 20,
    "mission_impact": 5,
    "exposure": 5,
    "upgrade_difficulty": 4,
    "bandwidth": "medium",
    "latency": "high",
    "compute": "medium",
    "platform_lifetime": "long",
    "interoperability": "high",
    "classification": "secret",
    "crypto_agility": "medium",
    "network_domain": "satcom",
    "dependencies": [
        "PKI Authority",
        "Mission Planning Server"
    ]
},

{
    "name": "Air Defense C2",
    "mission_type": "air_defense",
    "network_domain": "platform",

    "algorithms": ["RSA"],
    "protocols": ["TLS 1.2"],
    "data_lifetime": 25,
    "mission_impact": 5,
    "exposure": 5,
    "upgrade_difficulty": 5,
    "network_type": "operational",
    "bandwidth": "high",
    "latency": "medium",
    "compute": "high",
    "platform_lifetime": "long",
    "interoperability": "high",
    "classification": "secret",
    "crypto_agility": "medium",
    "high_value_asset": True
},
{
    "name": "Joint Fires Network",
    "mission_type": "joint_fire_control",

    "algorithms": ["RSA"],
    "protocols": ["TLS 1.2"],
    "data_lifetime": 25,
    "mission_impact": 5,
    "exposure": 5,
    "upgrade_difficulty": 5,
    "network_type": "operational",
    "bandwidth": "high",
    "latency": "medium",
    "compute": "high",
    "platform_lifetime": "long",
    "interoperability": "high",
    "classification": "secret",
    "crypto_agility": "medium",
    "high_value_asset": True,
    "network_domain": "tactical" 
},
{
    "name": "SIGINT Processing Node",
    "mission_type": "intelligence",
    "network_domain": "intelligence",
    "algorithms": ["RSA"],
    "protocols": ["TLS 1.2"],
    "data_lifetime": 25,
    "mission_impact": 5,
    "exposure": 5,
    "upgrade_difficulty": 5,
    "network_type": "operational",
    "bandwidth": "high",
    "latency": "medium",
    "compute": "high",
    "platform_lifetime": "long",
    "interoperability": "high",
    "classification": "secret",
    "crypto_agility": "medium",
    "high_value_asset": True,
        },
        {
            "name": "Fighter Aircraft Platform",
            "platform_type": "fighter_aircraft",
            "platform_age": 18,
            "refresh_cycle": 10,
            "algorithms": ["RSA"],
            "protocols": ["TLS 1.2"],
            "data_lifetime": 20,
            "mission_impact": 5,
            "exposure": 3,
            "upgrade_difficulty": 5,
            "network_type": "tactical",
            "bandwidth": "medium",
            "latency": "low",
            "compute": "high",
            "platform_lifetime": "long",
            "interoperability": "high",
            "classification": "secret",
            "crypto_agility": "low",
            "network_domain": "platform",
            "high_value_asset": True
        },
        {
    "name": "NATO Mission Network",
    "network_domain": "coalition",
    "network_type": "operational",
    "algorithms": ["RSA"],
    "protocols": ["TLS 1.2"],
    "data_lifetime": 20,
    "mission_impact": 5,
    "exposure": 5,
    "upgrade_difficulty": 4,
    "bandwidth": "high",
    "latency": "medium",
    "compute": "high",
    "interoperability": "high",
    "classification": "secret",
    "crypto_agility": "medium",
    "dependencies": [
        "Partner PKI",
        "Federated Identity Service"
    ]
}
    ]

uploaded_systems = load_uploaded_file(uploaded_file)

if uploaded_systems:
    if validate_systems(uploaded_systems):
        systems = uploaded_systems
    else:
        st.stop()
else:
    systems = load_data()


systems = process_systems(systems, max_years)
model = train_simple_model(systems)

for s in systems:
    s["ml_risk"] = predict_simple_ml(s, model)


# ✅ TLS warning (ONLY ONCE)
for s in systems:
    if tls_upgrade_needed(s):
        st.warning(f"{s['name']} requires TLS 1.3 upgrade")

# ✅ Filter once
filtered_systems = [
    s for s in systems
    if s.get("category") in selected_categories
    and s.get("network_type", "enterprise") in network_filter
]

# ✅ CBOM
cbom = generate_cbom_all(filtered_systems, future_shift)

def architecture_icon(architecture):
    icons = {
        "HSM (Hardware Security Module)": "🔐",
        "Transparent Proxy (Recommended)": "🔄",
        "Middleware Layer (Lightweight)": "🧩",
        "Inline Encryption": "🛡️",
    }
    return icons.get(architecture, "🏗️")


def category_color(cat):
    colors = {
        "CRITICAL": "red",
        "HIGH": "orange",
        "MEDIUM": "blue",
        "LOW": "green"
    }
    return colors.get(cat, "gray")


def quantum_security_strategy(system):
    if not system.get("feasible", True):
        return "Use hybrid classical-PQC deployment with staged migration and crypto agility."
    if system["category"] == "CRITICAL":
        return "Immediate hybrid PQC rollout with key rotation and inventory monitoring."
    elif system["category"] == "HIGH":
        return "Adopt PQC in parallel with classical algorithms and test interoperability."
    elif system["category"] == "MEDIUM":
        return "Prioritize PQC-capable endpoints and plan phased migration."
    return "Monitor and prepare for gradual PQC adoption."


def pqc_roadmap(system):

    roadmap = ["Inventory"]

    if not system["feasible"]:
        roadmap.append("Hybrid Deployment")

    if system["risk"] > 0.70:
        roadmap.append("Priority Migration")

    roadmap.extend([
        "Key Exchange Migration",
        "Signature Migration",
        "Legacy Retirement"
    ])

    return roadmap


def plot_hndl_curve(system):
    years = list(range(1, max_years))
    risk = [1 if system["data_lifetime"] >= y else 0 for y in years]

    fig, ax = plt.subplots()
    ax.plot(years, risk)
    ax.set_xlabel("Years Until Quantum Capability")
    ax.set_ylabel("Compromise Risk")
    ax.set_title(f"HNDL Risk Curve: {system['name']}")
    st.pyplot(fig)


def hndl_curve(system):
    years = list(range(1, max_years + 1))
    values = [
        1 if system.get("data_lifetime", 0) >= y else 0
        for y in years
    ]
    return years, values


def io_t_classification(system):
    if system["network_type"] == "tactical":
        return "Battlefield IoT (UAV/Sensors)"
    elif system["network_type"] == "satcom":
        return "Satellite Communications"
    elif system["network_type"] == "enterprise":
        return "Command & Control Infrastructure"
    return "General Infrastructure"
    
if st.button("Explain Score"):
    st.write("Priority = Vulnerability + Lifetime + Mission Impact + ...")

if filtered_systems:
    avg_priority = sum(s["priority"] for s in filtered_systems) / len(filtered_systems)
    avg_risk = sum(s["risk"] for s in filtered_systems) / len(filtered_systems)
else:
    avg_priority, avg_risk = 0, 0

st.divider()

col1, col2, col3 = st.columns(3)

col1.metric("Systems Analyzed", len(filtered_systems))
col2.metric("Avg Priority", round(avg_priority, 2))
col3.metric("Avg Quantum Risk", round(avg_risk, 2))

st.caption("High-level overview of system readiness for post-quantum migration.")

with tab1:
    st.divider()
    st.header("📋 System Inventory")
    
    st.dataframe([
        {
            "System": s["name"],
            "Network": s["network_type"],
            "Category": s["category"],
            "Algorithms": ", ".join(s["algorithms"]),
            "Protocols": ", ".join(s["protocols"])
        }
        for s in filtered_systems
    ])

def confidence_score(system):
    variance = abs(system["ml_risk"] - system["risk"])
    return round(1 - variance, 2)
with tab2:
    st.divider()
    st.header("⚠️ Risk Analysis")

    for s in filtered_systems:
        with st.container():
            st.markdown(f"### {s['name']}")

            col1, col2, col3, col4, col5 = st.columns(5)
            col1.metric("Priority", s["priority"])
            col2.metric("Risk", s["risk"])
            col3.metric("Threat", s["threat"])
            col4.metric("ML Risk", s.get("ml_risk", "N/A"))
            col5.metric("Confidence", confidence_score(s))

            st.progress(min(s["risk"], 1.0))

            st.write(f"**Exposure:** {s['exposure']}")

            plot_hndl_curve(s)

            st.divider()

with tab3:
    st.divider()
    st.header("🧠 PQC Strategy")

    for s in filtered_systems:
        with st.expander(s["name"], expanded=False):
            if s.get("ml_risk") and s["ml_risk"] > s["risk"]:
                st.warning("⚠️ ML predicts higher future risk")

            st.markdown(f"**Feasible:** {'✅' if s['feasible'] else '❌'}")
            st.markdown(f"**Architecture:** {architecture_icon(s['architecture'])} {s['architecture']}")
            st.markdown(f"**Deployment:** {s['deployment']}")

            st.info(f"Recommended Crypto: {recommended_crypto(s)}")
            st.success(f"Strategy: {quantum_security_strategy(s)}")
            st.caption(f"Migration Phase: {s['phase']}")
            st.metric(
                "Crypto Agility",
                s["agility_maturity"]
            )
            st.progress(
    s["agility_maturity"] / 5
)
            st.metric(
    "Compliance",
    f"{s['compliance']}%"
)
            st.info(
    f"Military Architecture: {s['mil_architecture']}"
)

            roadmap = pqc_roadmap(s)

            for step in roadmap:
                st.write(f"• {step}")


# Ensure a dataframe exists for analytics (build from filtered systems)
df = pd.DataFrame(filtered_systems)

if not df.empty:
    pivot = df.pivot_table(
        index="network_type",
        columns="category",
        values="priority",
        aggfunc="mean"
    )

    fig, ax = plt.subplots()
    heatmap = ax.imshow(
        pivot.fillna(0).values,
        cmap="viridis",
        aspect="auto"
    )
for i, row in enumerate(pivot.fillna(0).values):
    for j, val in enumerate(row):
        ax.text(j, i, f"{val:.1f}", ha="center", va="center", color="white")

ax.set_xticks(range(len(pivot.columns)))
ax.set_xticklabels(pivot.columns)
ax.set_yticks(range(len(pivot.index)))
ax.set_yticklabels(pivot.index)

fig.colorbar(heatmap, ax=ax)
infeasible = [s for s in filtered_systems if not s["feasible"]]

network_counts = {}

for s in filtered_systems:
    net = s["network_type"]
    network_counts[net] = network_counts.get(net, 0) + 1

labels = list(network_counts.keys())
values = list(network_counts.values())

fig2, ax2 = plt.subplots()
ax2.bar(labels, values)

ax2.set_xlabel("Network Type")
ax2.set_ylabel("Number of Systems")

def explain_ml(system, model):
    weights, _ = model
    features = extract_features(system)

    contributions = {
        k: features[k] * weights[k] for k in weights
    }
    return contributions

def explain_risk(system):

    reasons = []

    if "RSA" in system.get("algorithms", []):
        reasons.append(
            "Uses RSA"
        )

    if system.get("data_lifetime", 0) > 15:
        reasons.append(
            "Long-term data retention"
        )

    if system.get("exposure", 0) > 3:
        reasons.append(
            "High exposure"
        )

    if (
        system.get("network_domain")
        == "coalition"
    ):
        reasons.append(
            "Coalition dependency"
        )

    return reasons

def build_network_graph(systems):

    G = nx.DiGraph()

    for s in systems:

        G.add_node(s["name"])

        for dep in s.get(
            "dependencies",
            []
        ):
            G.add_edge(
                s["name"],
                dep
            )

    return G


def blast_radius(graph):
    return nx.degree_centrality(graph)

years = list(range(1, max_years))
trend = [
    sum(1 for s in systems if s["data_lifetime"] >= y)
    for y in years
]

with tab4:
    st.subheader("💥 Blast Radius")

    graph = build_network_graph(filtered_systems)

    centrality = blast_radius(graph)

    impact = 0

    if filtered_systems:
        selected_system_name = st.selectbox(
            "System",
            [s["name"] for s in filtered_systems]
        )

        selected_system = next(
            s for s in filtered_systems
            if s["name"] == selected_system_name
        )

        years, values = hndl_curve(selected_system)

        fig, ax = plt.subplots()
        ax.plot(
            years,
            values,
            linewidth=3
        )

        st.pyplot(fig)

        st.bar_chart(explain_ml(selected_system, model))

        st.dataframe(
            pd.DataFrame.from_dict(
                centrality, orient="index", columns=["Centrality"]
            ).sort_values(by="Centrality", ascending=False)
        )

        target = selected_system

        st.metric(
            "Mission Impact Score",
            target.get("mission_impact", 0)
        )

        impact = selected_system.get("exposure", 0)

        heat_df = pd.DataFrame([
            {
                "Domain": s["network_domain"],
                "Readiness": s["readiness_category"]
            }
            for s in filtered_systems
        ])
        pivot = pd.crosstab(
            heat_df["Domain"],
            heat_df["Readiness"]
        )

        st.dataframe(pivot)

    st.metric(
        "Mission Exposure Impact",
        impact
    )

    st.divider()
    st.header("📊 ML Explainability")
    st.subheader("Quantum Risk Trend")
    st.line_chart(trend)

    st.metric(
        "Dependency Nodes",
        graph.number_of_nodes()
    )

    st.metric(
        "Dependency Edges",
        graph.number_of_edges()
    )


for s in systems:
    s["final_risk"] = round(
        0.5 * s["risk"] + 0.5 * s["ml_risk"], 2
    )

trend = [
    sum(1 for s in systems if s["data_lifetime"] >= y)
    for y in years
]

with tab5:
    st.divider()
    st.header("🚨 Critical Alerts")

    critical = [s for s in filtered_systems if s["category"] == "CRITICAL"]

    if critical:
        st.error(f"{len(critical)} Critical Systems Detected")

        for s in critical:
            st.markdown(f"- **{s['name']}** requires immediate migration")
    else:
        st.success("No critical systems ✅")

    st.divider()

    st.subheader("⚠️ PQC Feasibility Issues")

    infeasible = [s for s in filtered_systems if not s["feasible"]]

    if infeasible:
        for s in infeasible:
            st.warning(f"{s['name']} has deployment constraints")
    else:
        st.success("All systems PQC-ready ✅")


def pqc_replacement(alg):
    mapping = {
        "RSA": "Kyber",
        "ECC": "Dilithium"
    }
    return mapping.get(alg, "N/A")

def save_scatter_plot(df):
    fig, ax = plt.subplots(figsize=(8, 6), dpi=300)

    for category, color in {
        "CRITICAL": "red",
        "HIGH": "orange",
        "MEDIUM": "blue",
        "LOW": "green"
    }.items():
        subset = df[df["category"] == category]
        ax.scatter(subset["priority"], subset["risk"], label=category, color=color)

    ax.set_xlabel("Priority")
    ax.set_ylabel("Risk")
    ax.set_title("Risk vs Priority")

    ax.grid(True, linestyle='--', alpha=0.5)
    ax.legend()

    plt.tight_layout()
    plt.savefig("risk_priority.png", dpi=300)
    plt.close()


def save_network_distribution(filtered_systems):
    network_counts = {}

    for s in filtered_systems:
        net = s["network_type"]
        network_counts[net] = network_counts.get(net, 0) + 1

    labels = list(network_counts.keys())
    values = list(network_counts.values())

    fig, ax = plt.subplots(figsize=(8, 6), dpi=300)

    ax.bar(labels, values)

    ax.set_xlabel("Network Type")
    ax.set_ylabel("Number of Systems")
    ax.set_title("System Distribution by Network Type")

    ax.grid(True, linestyle='--', alpha=0.5)

    plt.tight_layout()
    plt.savefig("network_distribution.png", dpi=300)
    plt.close()

def save_heatmap(df):
    if df.empty:
        return

    pivot = df.pivot_table(
        values="priority",
        index="network_type",
        columns="category",
        aggfunc="mean"
    )

    fig, ax = plt.subplots(figsize=(8, 6), dpi=300)
    heatmap = ax.imshow(
        pivot.fillna(0).values,
        cmap="viridis",
        aspect="auto"
    )

    ax.set_xticks(range(len(pivot.columns)))
    ax.set_xticklabels(pivot.columns)
    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels(pivot.index)

    ax.grid(True, linestyle='--', alpha=0.5)
    fig.colorbar(heatmap, ax=ax)

    plt.tight_layout()
    plt.savefig("heatmap.png", dpi=300)
    plt.close() 
if not df.empty:
    pivot = df.pivot_table(
        index="network_type",
        columns="category",
        values="priority",
        aggfunc="mean"
    )
    save_scatter_plot(df)    
    save_network_distribution(filtered_systems)    
    save_heatmap(df)

    fig, ax = plt.subplots()
    heatmap = ax.imshow(
        pivot.fillna(0).values,
        cmap="viridis",
        aspect="auto"
    )

    for i, row in enumerate(pivot.fillna(0).values):
        for j, val in enumerate(row):
            ax.text(
                j,
                i,
                f"{val:.1f}",
                ha="center",
                va="center",
                color="white"
            )

    ax.set_xticks(range(len(pivot.columns)))
    ax.set_xticklabels(pivot.columns)
    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels(pivot.index)

    fig.colorbar(heatmap, ax=ax)


    

with tab6: 
    st.divider() 
    st.header("📦 Export Center")

    st.markdown("Download analysis results and cryptographic migration plans.")

    col1, col2 = st.columns(2)

    with col1:
        st.download_button(
            label="⬇️ Download CSV Report",
            data=df.to_csv(index=False),
            file_name="pqc_analysis.csv",
            mime="text/csv"
        )

    with col2:
        st.download_button(
            label="⬇️ Download CBOM",
            data=json.dumps(cbom, indent=2),
            file_name="cbom.json",
            mime="application/json"
        )

    st.divider()

    with st.expander("🔍 Debug Output"):
        st.json(filtered_systems)


with tab7:

    st.subheader("Executive KPIs")

    critical_count = sum(1 for s in filtered_systems if s["category"] == "CRITICAL")
    portfolio_cost = sum(
        s.get("migration_cost", 0)
        for s in filtered_systems
    )
    portfolio_risk_reduction = sum(
        s.get("risk_reduction", 0)
        for s in filtered_systems
    )

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric("Systems", len(filtered_systems))
    col2.metric("Critical", critical_count)
    avg_readiness = (
        sum(s["military_readiness"] for s in filtered_systems)
        / len(filtered_systems)
        if filtered_systems
        else 0
    )

    col3.metric(
        "Avg Readiness",
        round(avg_readiness, 1)
    )
    col4.metric("Portfolio Cost", f"${portfolio_cost:,.0f}")
    col5.metric("Risk Reduction", round(portfolio_risk_reduction, 1))

    st.header("📈 Executive Summary")
    st.metric("Critical Systems", critical_count)

    top_risks = sorted(filtered_systems, key=lambda x: x["final_risk"], reverse=True)[:5]
    for s in top_risks:
        st.write(f"{s['name']} → Risk: {s['final_risk']}")

auto_refresh = st.sidebar.checkbox("Enable Auto Refresh")

if auto_refresh:
    st_autorefresh(interval=10000, key="datarefresh")
    
if st.sidebar.button("🔄 Re-run Analysis"):
    st.rerun()

st.sidebar.write("🔄 Auto-refresh enabled")


st.info("ML risk is based on learned feature patterns")


with tab8:

    st.header("🛰️ HNDL Intelligence")

    hndl_df = pd.DataFrame([
        {
            "System": s["name"],
            "HNDL": s["hndl_score"],
            "Risk": s["risk"],
            "Mission": s.get("mission_type")
        }
        for s in filtered_systems
    ])

    st.bar_chart(
        hndl_df.set_index("System")["HNDL"]
    )

    st.dataframe(hndl_df)

avg_readiness = (
    sum(s["military_readiness"] for s in filtered_systems)
    / len(filtered_systems)
    if filtered_systems
    else 0
)

with tab9:

    st.header("🪖 Military Readiness Assessment")

    ready_count = sum(1 for s in filtered_systems if s["readiness_category"] == "READY")

    ranking = sorted(
        filtered_systems,
        key=lambda x: x["military_readiness"],
        reverse=True
    )

    rank_df = pd.DataFrame([
    {
        "System": s.get("name", "Unknown"),
        "Readiness Score": s.get("military_readiness", 0),
        "Category": s.get("readiness_category", "Unknown"),
        "Mission": s.get("mission_type", "Unknown")
    }
    for s in ranking
])

    st.metric(
        "Mission Ready Systems",
        ready_count
    )

    st.subheader("🏆 Readiness Ranking")
    st.dataframe(rank_df)

    st.divider()

    for s in ranking:
        with st.expander(s["name"]):

            col1, col2, col3 = st.columns(3)

            col1.metric(
                "Mission Type",
                s.get("mission_type", "Unknown")
            )

            col2.metric(
                "Readiness Score",
                s["military_readiness"]
            )

            col3.metric(
                "Compliance %",
                s["compliance"]
            )

            if s["readiness_category"] == "READY":
                st.success("READY")
            elif s["readiness_category"] == "PARTIAL":
                st.warning("PARTIAL")
            else:
                st.error("AT RISK")

NETWORK_DOMAINS = [
    "enterprise",
    "intelligence",
    "satcom",
    "tactical",
    "coalition",
    "platform"
]

with tab10:

    st.header("🕵️ Intelligence Risk")

    intel = [
        s for s in filtered_systems
        if s.get("network_domain")
        == "intelligence"
    ]

    intel_df = pd.DataFrame([
        {
            "System": s["name"],
            "Archive Risk": s["archive_risk"],
            "HNDL": s["hndl_score"]
        }
        for s in intel
    ])

    st.dataframe(intel_df)

with tab11:

    st.header("🤝 Coalition Readiness")

    coalition = [
        s for s in filtered_systems
        if s.get("network_domain") == "coalition"
    ]

    if coalition:

        col1, col2 = st.columns(2)

        col1.metric(
            "Coalition Systems",
            len(coalition)
        )

        col2.metric(
            "Average Coalition Readiness",
            round(
                sum(
                    s["coalition_readiness"]
                    for s in coalition
                ) / len(coalition),
                1
            )
        )

        coalition_df = pd.DataFrame([
            {
                "System": s["name"],
                "Coalition Risk": s["coalition_risk"],
                "Coalition Category": s["coalition_category"],
                "Readiness": s["readiness_category"],
                "Interoperability Risk": s["interop_risk"],
                "Compliance": s["compliance"],
                "Coalition Readiness": s["coalition_readiness"]
            }
            for s in coalition
        ])

        st.dataframe(coalition_df)

    else:
        st.warning(
            "No coalition-domain systems available."
        )


with tab12:

    st.header("📜 NIST Compliance")

    total = len(filtered_systems)

    compliant = sum(
        1 for s in filtered_systems
        if s["compliance"] >= 90
    )

    progress = compliant / total if total else 0

    st.metric(
        "Compliant Systems",
        compliant
    )

    st.progress(progress)

    st.metric(
        "Compliance %",
        round(progress * 100, 1)
    )
    st.subheader("🚀 Migration Queue")

    def migration_queue(systems):
        return sorted(
            systems,
            key=lambda s: (
                s["priority"],
                s["archive_risk"]
            ),
            reverse=True
        )

    queue = migration_queue(
        filtered_systems
    )

    st.dataframe(
        pd.DataFrame([
            {
                "System": s["name"],
                "Priority": s["priority"],
                "Risk": s["risk"]
            }
            for s in queue[:10]
        ])
    )


def generate_coa(systems):

    critical = sum(
        1
        for s in systems
        if s["category"] == "CRITICAL"
    )

    return {

        "Aggressive":
        f"Migrate all {critical} critical systems by FY28.",

        "Balanced":
        "Migrate CRITICAL and HIGH systems first.",

        "Budget":
        "Protect intelligence and coalition assets first."
    }

def campaign_plan(
    systems,
    annual_budget,
    start_year=2027
):

    queue = sorted(
        systems,
        key=lambda s: (
            s["priority"],
            s["archive_risk"]
        ),
        reverse=True
    )

    plan = {}

    year = start_year
    budget_remaining = annual_budget

    plan[year] = []

    for system in queue:

        cost = system["migration_cost"]

        if cost > budget_remaining:

            year += 1
            budget_remaining = annual_budget

            plan[year] = []

        plan[year].append({
            "System": system["name"],
            "Cost": cost,
            "Priority": system["priority"]
        })

        budget_remaining -= cost

    return plan

with tab13:

    st.header("📅 PQC Campaign Planner")

    annual_budget = st.slider(
        "Annual Migration Budget ($)",
        100000,
        5000000,
        1000000,
        step=100000
    )

    start_year = st.number_input(
        "Starting Fiscal Year",
        value=2027
    )

    plan = campaign_plan(
        filtered_systems,
        annual_budget,
        start_year
    )

    st.metric(
        "Years To Complete",
        len(plan)
    )

    with st.expander("COA"):

        coa = generate_coa(
            filtered_systems
        )

        for name, text in coa.items():

            st.subheader(name)

            st.write(text)

    for year, projects in plan.items():

        st.subheader(f"FY{year}")

        if projects:

            st.dataframe(
                pd.DataFrame(projects)
            )

with tab14:

    st.header("💰 Cost Modeling")
    cost_df = pd.DataFrame([
        {
            "System": s["name"],
            "Migration Cost":
                s["migration_cost"],

            "Priority":
                s["priority"],

            "Risk Reduction":
                s["risk_reduction"],

            "ROI":
                s["roi"]
        }
        for s in filtered_systems
    ])

    st.dataframe(cost_df)

    # Sort by ROI and show best candidate
    roi_df = cost_df.sort_values(
        "ROI",
        ascending=False
    )

    if not roi_df.empty:
        best = roi_df.iloc[0]
        st.success(f"Best ROI Candidate: {best['System']}")

    st.divider()

    st.metric(
    "Risk Reduction Potential",
    round(
        cost_df['Risk Reduction'].sum(),
        1
    )
)

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Portfolio Cost",
        f"${cost_df['Migration Cost'].sum():,.0f}"
    )

    col2.metric(
        "Total Risk Reduction",
        round(
            cost_df[
                "Risk Reduction"
            ].sum(),
            1
        )
    )

    avg_roi = (
        cost_df["ROI"].mean()
        if not cost_df.empty
        else 0
    )

    col3.metric(
        "Average ROI",
        round(avg_roi, 6)
    )
    st.subheader(
            "Cost Distribution"
        )

    if not cost_df.empty:
            chart_df = cost_df.set_index(
                "System"
            )
            st.bar_chart(chart_df["Migration Cost"])
    else:
            st.info("No systems match current filters.")

    col1, col2 = st.columns(2)

    col1.metric(
            "Migration Cost",
            f"${portfolio_cost:,.0f}"
        )

    col2.metric(
            "Risk Reduction Potential",
            round(
                portfolio_risk_reduction,
                1
            )
        )

    st.subheader(
            "Best ROI Candidates"
        )

    roi_df = cost_df.sort_values(
            "ROI",
            ascending=False
        )

    st.dataframe(
            roi_df.head(10)
        )

import time

start = time.time()

systems = process_systems(systems, max_years)

end = time.time()

print(end-start)
