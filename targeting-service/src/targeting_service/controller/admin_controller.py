from uuid import UUID

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.targeting_service.model.admin_engine import engine
from src.targeting_service.model.view.distribution_admin_model import DistributionTable
from src.targeting_service.model.view.recipient_admin_model import RecipientTable
from src.targeting_service.model.view.tag_admin_model import TagTable

router = APIRouter(prefix="/admin-api", tags=["admin-api"])


class SetTagsRequest(BaseModel):
    tag_ids: list[UUID]


class SetRecipientsRequest(BaseModel):
    recipient_ids: list[UUID]


@router.get("/tags")
def get_all_tags():
    with Session(engine) as session:
        tags = session.query(TagTable).order_by(TagTable.name).all()
        return [{"id": str(tag.id), "name": tag.name or str(tag.id)} for tag in tags]


@router.post("/recipient/{pk}/set-tags")
def set_tags_for_recipient(pk: UUID, body: SetTagsRequest):
    with Session(engine) as session:
        recipient = session.get(RecipientTable, pk)
        if not recipient:
            raise HTTPException(status_code=404, detail="Получатель не найден")

        recipient.tags = session.query(TagTable).filter(TagTable.id.in_(body.tag_ids)).all()
        session.commit()
    return {"ok": True}


@router.post("/distribution/{pk}/set-tags")
def set_tags_for_distribution(pk: UUID, body: SetTagsRequest):
    with Session(engine) as session:
        distribution = session.get(DistributionTable, pk)
        if not distribution:
            raise HTTPException(status_code=404, detail="Рассылка не найдена")

        distribution.tags = session.query(TagTable).filter(TagTable.id.in_(body.tag_ids)).all()
        session.commit()
    return {"ok": True}


@router.get("/recipients")
def get_all_recipients():
    with Session(engine) as session:
        recipients = session.query(RecipientTable).order_by(RecipientTable.name).all()
        return [
            {"id": str(r.id), "name": r.name or str(r.telegram_id) or str(r.id)} for r in recipients
        ]


@router.post("/tag/{pk}/set-recipients")
def set_recipients_for_tag(pk: UUID, body: SetRecipientsRequest):
    with Session(engine) as session:
        tag = session.get(TagTable, pk)
        if not tag:
            raise HTTPException(status_code=404, detail="Тег не найден")

        tag.recipients = (
            session.query(RecipientTable).filter(RecipientTable.id.in_(body.recipient_ids)).all()
        )
        session.commit()
    return {"ok": True}
