from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import engine, Base, SessionLocal
from app import models, schemas, crud
from app.distribution import find_or_create_lead, assign_contact

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Mini-CRM API")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def read_root():
    return {"message": "Mini-CRM API"}


@app.post("/operators", response_model=schemas.OperatorResponse)
def create_operator(operator: schemas.OperatorCreate, db: Session = Depends(get_db)):
    existing = crud.get_operator_by_name(db, operator.name)
    if existing:
        raise HTTPException(status_code=400, detail="Operator with this name already exists")
    return crud.create_operator(db, operator)


@app.get("/operators", response_model=list[schemas.OperatorResponse])
def get_operators(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_operators(db, skip, limit)


@app.patch("/operators/{operator_id}", response_model=schemas.OperatorResponse)
def update_operator(operator_id: int, operator: schemas.OperatorCreate, db: Session = Depends(get_db)):
    db_operator = crud.get_operator(db, operator_id)
    if not db_operator:
        raise HTTPException(status_code=404, detail="Operator not found")
    return crud.update_operator(db, operator_id, operator)


@app.post("/sources", response_model=schemas.SourceResponse)
def create_source(source: schemas.SourceCreate, db: Session = Depends(get_db)):
    existing = crud.get_source_by_name(db, source.name)
    if existing:
        raise HTTPException(status_code=400, detail="Source with this name already exists")
    return crud.create_source(db, source)


@app.get("/sources", response_model=list[schemas.SourceResponse])
def get_sources(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_sources(db, skip, limit)


@app.post("/sources/{source_id}/operators/{operator_id}/weight")
def set_operator_weight(source_id: int, operator_id: int, weight: float, db: Session = Depends(get_db)):
    source = crud.get_source(db, source_id)
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    operator = crud.get_operator(db, operator_id)
    if not operator:
        raise HTTPException(status_code=404, detail="Operator not found")
    result = crud.set_operator_source_weight(db, operator_id, source_id, weight)
    return {"operator_id": result.operator_id, "source_id": result.source_id, "weight": result.weight}


@app.post("/contacts", response_model=schemas.ContactResponse)
def create_contact(contact: schemas.ContactCreate, db: Session = Depends(get_db)):
    lead = db.query(models.Lead).filter(models.Lead.id == contact.lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    source = crud.get_source(db, contact.source_id)
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")

    result = assign_contact(db, contact.lead_id, contact.source_id)
    return result


@app.post("/leads")
def create_lead(external_id: str, phone: str = None, email: str = None, source_id: int = None, db: Session = Depends(get_db)):
    if not source_id:
        raise HTTPException(status_code=400, detail="source_id is required")

    source = crud.get_source(db, source_id)
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")

    lead = find_or_create_lead(db, external_id, phone, email, source_id)
    contact = assign_contact(db, lead.id, source_id)

    return {
        "lead_id": lead.id,
        "external_id": lead.external_id,
        "phone": lead.phone,
        "email": lead.email,
        "contact_id": contact.id,
        "operator_id": contact.operator_id
    }


@app.get("/contacts")
def get_contacts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    contacts = db.query(models.Contact).offset(skip).limit(limit).all()
    return contacts


@app.get("/leads")
def get_leads(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    leads = db.query(models.Lead).offset(skip).limit(limit).all()
    return leads


@app.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    stats = crud.get_statistics(db)

    operators_load = []
    operators = crud.get_operators(db, 0, 1000)
    for operator in operators:
        load = crud.get_operator_load(db, operator.id)
        operators_load.append({
            "operator_id": operator.id,
            "name": operator.name,
            "current_load": load,
            "max_load": operator.max_load
        })

    source_distribution = []
    sources = crud.get_sources(db, 0, 1000)
    for source in sources:
        count = crud.get_source_contacts_count(db, source.id)
        source_distribution.append({
            "source_id": source.id,
            "name": source.name,
            "contacts_count": count
        })

    return {
        "general": stats,
        "operators_load": operators_load,
        "source_distribution": source_distribution
    }
