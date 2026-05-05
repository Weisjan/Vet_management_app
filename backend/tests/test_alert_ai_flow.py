from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from app.db.models.alert import Alert
from app.db.models.enums import NotificationStatus, RiskLevel
from app.db.models.mention import MentionAIAnalysis
from app.db.models.notification import Notification
from app.workers.jobs import process_new_mention_with_session


def test_medium_risk_analysis_creates_alert_and_notification(
    client: TestClient,
    db_session: Session,
) -> None:
    clinic = client.post("/api/v1/clinics", json={"name": "Alert Vet"}).json()
    mention = client.post(
        f"/api/v1/clinics/{clinic['id']}/mentions",
        json={
            "source": "manual",
            "content": "The staff was rude and the visit was expensive.",
        },
    ).json()

    result = process_new_mention_with_session(db_session, mention["id"])

    assert result is not None
    assert result["risk_level"] == "medium"

    mention_id = UUID(mention["id"])
    clinic_id = UUID(clinic["id"])

    analysis = db_session.scalars(
        select(MentionAIAnalysis).where(MentionAIAnalysis.mention_id == mention_id)
    ).one()
    assert analysis.risk_level == RiskLevel.MEDIUM

    alert = db_session.scalars(select(Alert).where(Alert.mention_id == mention_id)).one()
    assert alert.clinic_id == clinic_id
    assert alert.risk_level == RiskLevel.MEDIUM

    notification = db_session.scalars(
        select(Notification).where(Notification.clinic_id == clinic_id)
    ).one()
    assert notification.status == NotificationStatus.PENDING
    assert "MEDIUM" in notification.subject

    analysis_response = client.get(f"/api/v1/mentions/{mention['id']}/ai-analysis")
    assert analysis_response.status_code == 200
    assert analysis_response.json()["risk_level"] == "medium"

    alerts_response = client.get(f"/api/v1/clinics/{clinic['id']}/alerts")
    assert alerts_response.status_code == 200
    alerts = alerts_response.json()
    assert len(alerts) == 1
    assert alerts[0]["risk_level"] == "medium"


def test_low_risk_analysis_does_not_create_alert(
    client: TestClient,
    db_session: Session,
) -> None:
    clinic = client.post("/api/v1/clinics", json={"name": "Calm Vet"}).json()
    mention = client.post(
        f"/api/v1/clinics/{clinic['id']}/mentions",
        json={
            "source": "manual",
            "content": "The clinic team was kind and excellent.",
        },
    ).json()

    result = process_new_mention_with_session(db_session, mention["id"])

    assert result is not None
    assert result["risk_level"] == "low"
    assert db_session.scalars(select(Alert)).all() == []
    assert db_session.scalars(select(Notification)).all() == []
