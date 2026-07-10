import pytest
from sqlalchemy.orm import Session
from backend.db.models import Device, TelemetryEvent, Incident

def test_settings_load(test_settings):
    assert test_settings.ENVIRONMENT.value == "dev"
    assert test_settings.DATABASE_URL == "sqlite:///:memory:"

def test_create_device(test_db: Session):
    device = Device(device_id="dev-100", device_type="power_plant", location="Plant A")
    test_db.add(device)
    test_db.commit()
    
    saved = test_db.query(Device).filter_by(device_id="dev-100").first()
    assert saved is not None
    assert saved.device_type == "power_plant"
    assert saved.is_isolated is False

def test_telemetry_fixtures(sample_telemetry_normal, sample_telemetry_dos_attack):
    assert sample_telemetry_normal["temperature"] == 75.0
    assert sample_telemetry_dos_attack["temperature"] == 120.0
