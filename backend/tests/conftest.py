from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models import MeasurementUnit, Polygon, SensorType


@pytest.fixture(scope="session")
def engine():
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=test_engine)
    yield test_engine
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture()
def db_session(engine) -> Generator[Session, None, None]:
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=Session)

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def seeded_db(db_session: Session) -> Session:
    unit_temperature = MeasurementUnit(name="Temperature", symbol="°C", description="Celsius")
    unit_humidity = MeasurementUnit(name="Humidity", symbol="%", description="Percent")
    unit_pressure = MeasurementUnit(name="Pressure", symbol="hPa", description="Pressure")
    unit_co2 = MeasurementUnit(name="CO2", symbol="ppm", description="CO2 concentration")
    unit_light = MeasurementUnit(name="Light", symbol="lx", description="Light level")
    unit_noise = MeasurementUnit(name="Noise", symbol="dB", description="Noise level")
    db_session.add_all(
        [unit_temperature, unit_humidity, unit_pressure, unit_co2, unit_light, unit_noise]
    )
    db_session.flush()

    sensor_types = [
        SensorType(name="Temperature", code="temperature", unit_id=unit_temperature.unit_id, description=None),
        SensorType(name="Humidity", code="humidity", unit_id=unit_humidity.unit_id, description=None),
        SensorType(name="Pressure", code="pressure", unit_id=unit_pressure.unit_id, description=None),
        SensorType(name="CO2", code="co2", unit_id=unit_co2.unit_id, description=None),
        SensorType(name="Light", code="light", unit_id=unit_light.unit_id, description=None),
        SensorType(name="Noise", code="noise", unit_id=unit_noise.unit_id, description=None),
    ]
    db_session.add_all(sensor_types)

    polygons = [
        Polygon(name="Polygon #1", location="North", description=None),
        Polygon(name="Polygon #2", location="Center", description=None),
        Polygon(name="Polygon #3", location="South", description=None),
    ]
    db_session.add_all(polygons)
    db_session.commit()
    return db_session


@pytest.fixture()
def client(db_session: Session) -> Generator[TestClient, None, None]:
    def _override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

