import pytest
from fastapi.testclient import TestClient
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.compiler import compiles
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.dependencies import get_background_queue
from app.db.base import Base
from app.db.session import get_db
from app.main import app


@compiles(JSONB, "sqlite")
def compile_jsonb_for_sqlite(*args: object, **kwargs: object) -> str:
    return "TEXT"


@pytest.fixture()
def db_session() -> Session:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


def _install_dependency_overrides(db_session: Session) -> list[tuple[object, tuple[object, ...], dict[str, object]]]:
    enqueued_jobs: list[tuple[object, tuple[object, ...], dict[str, object]]] = []

    class FakeQueue:
        def enqueue(self, func: object, *args: object, **kwargs: object) -> None:
            enqueued_jobs.append((func, args, kwargs))

    def override_get_db() -> Session:
        try:
            yield db_session
        finally:
            pass

    def override_get_background_queue() -> FakeQueue:
        return FakeQueue()

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_background_queue] = override_get_background_queue
    return enqueued_jobs


@pytest.fixture()
def anonymous_client(db_session: Session) -> TestClient:
    enqueued_jobs = _install_dependency_overrides(db_session)
    try:
        test_client = TestClient(app)
        test_client.enqueued_jobs = enqueued_jobs  # type: ignore[attr-defined]
        yield test_client
    finally:
        app.dependency_overrides.clear()


@pytest.fixture()
def client(anonymous_client: TestClient) -> TestClient:
    response = anonymous_client.post(
        "/api/v1/auth/register",
        json={
            "email": "owner@example.test",
            "password": "secure-password",
            "full_name": "Clinic Owner",
        },
    )
    token = response.json()["access_token"]
    anonymous_client.headers.update({"Authorization": f"Bearer {token}"})
    return anonymous_client
