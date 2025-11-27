from sqlalchemy.orm import Session
from sqlalchemy import func
from app import models, schemas


def create_operator(db: Session, operator: schemas.OperatorCreate) -> models.Operator:
    db_operator = models.Operator(
        name=operator.name,
        is_active=operator.is_active,
        max_load=operator.max_load
    )
    db.add(db_operator)
    db.commit()
    db.refresh(db_operator)
    return db_operator


def get_operator(db: Session, operator_id: int) -> models.Operator:
    return db.query(models.Operator).filter(models.Operator.id == operator_id).first()


def get_operators(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Operator).offset(skip).limit(limit).all()


def get_operator_by_name(db: Session, name: str) -> models.Operator:
    return db.query(models.Operator).filter(models.Operator.name == name).first()


def update_operator(db: Session, operator_id: int, operator: schemas.OperatorCreate) -> models.Operator:
    db_operator = get_operator(db, operator_id)
    if db_operator:
        db_operator.name = operator.name
        db_operator.is_active = operator.is_active
        db_operator.max_load = operator.max_load
        db.commit()
        db.refresh(db_operator)
    return db_operator


def create_source(db: Session, source: schemas.SourceCreate) -> models.Source:
    db_source = models.Source(
        name=source.name,
        description=source.description
    )
    db.add(db_source)
    db.commit()
    db.refresh(db_source)
    return db_source


def get_source(db: Session, source_id: int) -> models.Source:
    return db.query(models.Source).filter(models.Source.id == source_id).first()


def get_sources(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Source).offset(skip).limit(limit).all()


def get_source_by_name(db: Session, name: str) -> models.Source:
    return db.query(models.Source).filter(models.Source.name == name).first()


def update_source(db: Session, source_id: int, source: schemas.SourceCreate) -> models.Source:
    db_source = get_source(db, source_id)
    if db_source:
        db_source.name = source.name
        db_source.description = source.description
        db.commit()
        db.refresh(db_source)
    return db_source


def set_operator_source_weight(db: Session, operator_id: int, source_id: int, weight: float) -> models.OperatorSourceWeight:
    db_weight = db.query(models.OperatorSourceWeight).filter(
        models.OperatorSourceWeight.operator_id == operator_id,
        models.OperatorSourceWeight.source_id == source_id
    ).first()

    if db_weight:
        db_weight.weight = weight
    else:
        db_weight = models.OperatorSourceWeight(
            operator_id=operator_id,
            source_id=source_id,
            weight=weight
        )
        db.add(db_weight)

    db.commit()
    db.refresh(db_weight)
    return db_weight


def get_operator_source_weights(db: Session, operator_id: int):
    return db.query(models.OperatorSourceWeight).filter(
        models.OperatorSourceWeight.operator_id == operator_id
    ).all()


def get_source_operator_weights(db: Session, source_id: int):
    return db.query(models.OperatorSourceWeight).filter(
        models.OperatorSourceWeight.source_id == source_id
    ).all()


def get_operator_load(db: Session, operator_id: int) -> int:
    return db.query(func.count(models.Contact.id)).filter(
        models.Contact.operator_id == operator_id,
        models.Contact.is_active == True
    ).scalar()


def get_source_contacts_count(db: Session, source_id: int) -> int:
    return db.query(func.count(models.Contact.id)).filter(
        models.Contact.source_id == source_id
    ).scalar()


def get_statistics(db: Session):
    operators_count = db.query(func.count(models.Operator.id)).scalar()
    sources_count = db.query(func.count(models.Source.id)).scalar()
    leads_count = db.query(func.count(models.Lead.id)).scalar()
    contacts_count = db.query(func.count(models.Contact.id)).scalar()
    active_contacts_count = db.query(func.count(models.Contact.id)).filter(
        models.Contact.is_active == True
    ).scalar()

    return {
        "operators": operators_count,
        "sources": sources_count,
        "leads": leads_count,
        "contacts": contacts_count,
        "active_contacts": active_contacts_count
    }
