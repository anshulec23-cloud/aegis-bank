"""
Offline LangGraph Pipeline Evaluation
=====================================
Executes the compiled LangGraph pipeline against a test suite of ICS telemetry profiles.
Does not require starting the FastAPI API, MQTT broker, or database.

Usage:
  python scripts/evaluate_pipeline.py
"""
import sys
import os
import json

# Insert backend directory into the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

# Disable DB and OLLAMA dependencies where possible, or use standard configurations
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["LLM_ENABLED"] = "False"  # Force rule-based signature fallback for offline eval

try:
    from pipeline.graph import run_pipeline
    from pipeline.state import empty_state
    from ml.model import get_model
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Please make sure all dependencies in backend/requirements.txt are installed.")
    sys.exit(1)

# Synthetic test cases matching various states
TEST_CASES = [
    {
        "name": "Normal Operation (SCADA Factory)",
        "telemetry": {
            "device_id": "device-factory-01",
            "device_type": "factory",
            "location": "Sector-4",
            "temperature": 75.0,
            "pressure": 250.0,
            "flow_rate": 120.0,
            "voltage": 230.0,
        }
    },
    {
        "name": "Denial of Service (Power Plant)",
        "telemetry": {
            "device_id": "device-pp-02",
            "device_type": "power_plant",
            "location": "Sector-1",
            "temperature": 90.0,   # High anomaly
            "pressure": 7.0,       # High anomaly
            "flow_rate": 8.0,      # Low anomaly
            "voltage": 230.0,
        }
    },
    {
        "name": "Physical Tampering (Oil Refinery)",
        "telemetry": {
            "device_id": "device-or-03",
            "device_type": "oil_refinery",
            "location": "Sector-3",
            "temperature": 115.0,  # Extreme
            "pressure": 9.5,       # Extreme
            "flow_rate": 0.5,      # Critical drop
            "voltage": 230.0,
        }
    },
    {
        "name": "Spoofing Attack (Water Treatment)",
        "telemetry": {
            "device_id": "device-wt-04",
            "device_type": "water_treatment",
            "location": "Sector-2",
            "temperature": 65.0,   # Suspiciously flat signature values
            "pressure": 4.5,
            "flow_rate": 120.0,
            "voltage": 230.0,
        }
    }
]

def run_evaluation():
    print("=" * 80)
    print("        ICS CYBERRISK platform — LANGGRAPH OFFLINE PIPELINE EVALUATION        ")
    print("=" * 80)
    
    # Pre-train/load ML model first
    print("\n[ML] Initializing Random Forest model...")
    get_model()
    print("[ML] Random Forest model ready.\n")
    
    for case in TEST_CASES:
        name = case["name"]
        telemetry = case["telemetry"]
        
        print(f"\n> Running Case: {name}")
        print(f"  Telemetry: Temp={telemetry['temperature']}°C, Pres={telemetry['pressure']}bar, Flow={telemetry['flow_rate']}L/s, Volt={telemetry['voltage']}V")
        
        # Execute pipeline
        state = run_pipeline(telemetry)
        
        # Display Results
        anomaly = state.get("anomaly", {})
        classification = state.get("classification", {})
        isolation = state.get("isolation", {})
        financial = state.get("financial_risk", {})
        
        print(f"  [Detector]     Is Anomaly: {anomaly.get('is_anomaly')} (Score: {anomaly.get('anomaly_score')})")
        
        if anomaly.get("is_anomaly"):
            print(f"  [Classifier]   Attack Type: {classification.get('attack_type')} | Severity: {classification.get('severity').upper()}")
            print(f"  [Isolator]     Action: {isolation.get('action_taken')} | Command: {isolation.get('command')}")
            print(f"  [Risk Exposure] Total Cost: ${financial.get('total_exposure_usd', 0):,.2f} | Risk Flag: {financial.get('credit_risk_flag')}")
            print(f"                 (Downtime: ${financial.get('downtime_cost_usd', 0):,.2f}, SLA: ${financial.get('sla_penalty_usd', 0):,.2f}, NERC Fine: ${financial.get('regulatory_fine_usd', 0):,.2f})")
        else:
            print("  [Detector]     No anomaly detected. Pipeline exited early.")
            
        print("-" * 60)

if __name__ == "__main__":
    run_evaluation()
