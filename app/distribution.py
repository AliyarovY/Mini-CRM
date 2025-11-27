import random
from sqlalchemy.orm import Session
from sqlalchemy import func
from app import models
from typing import Optional, List, Tuple


def find_or_create_lead(db: Session, external_id: str, phone: Optional[str],
                        email: Optional[str], source_id: int) -> models.Lead:
    lead = db.query(models.Lead).filter(
        models.Lead.external_id == external_id
    ).first()

    if lead:
        return lead

    lead = models.Lead(
        external_id=external_id,
        phone=phone,
        email=email,
        source_id=source_id
    )
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return lead


def get_available_operators(db: Session, source_id: int) -> List[Tuple[models.Operator, float]]:
    operator_weights = db.query(
        models.Operator,
        models.OperatorSourceWeight.weight
    ).join(
        models.OperatorSourceWeight,
        models.OperatorSourceWeight.operator_id == models.Operator.id
    ).filter(
        models.OperatorSourceWeight.source_id == source_id,
        models.Operator.is_active == True
    ).all()

    available = []

    for operator, weight in operator_weights:
        active_contacts_count = db.query(func.count(models.Contact.id)).filter(
            models.Contact.operator_id == operator.id,
            models.Contact.is_active == True
        ).scalar()

        if active_contacts_count < operator.max_load:
            available.append((operator, weight))

    return available


def select_operator_by_weight(operators_with_weights: List[Tuple[models.Operator, float]]) -> Optional[models.Operator]:
    if not operators_with_weights:
        return None

    operators = [op for op, _ in operators_with_weights]
    weights = [w for _, w in operators_with_weights]

    selected = random.choices(operators, weights=weights, k=1)
    return selected[0] if selected else None


def assign_contact(db: Session, lead_id: int, source_id: int) -> Optional[models.Contact]:
    available_operators = get_available_operators(db, source_id)
    selected_operator = select_operator_by_weight(available_operators)

    contact = models.Contact(
        lead_id=lead_id,
        source_id=source_id,
        operator_id=selected_operator.id if selected_operator else None,
        is_active=True
    )

    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact
