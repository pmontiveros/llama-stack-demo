from sqlalchemy.orm import Session, Query
from typing import TypedDict, List, Union, Optional
from .models import Base, Cuenta, Sinonimo
from .db import engine, SessionLocal
import pandas as pd

class AccountDB(TypedDict):
    nombre: str
    cuenta: str
    nivel: int
    path: str
    path_padre: str
    cuenta_minima: bool

def init_db():
    Base.metadata.create_all(bind=engine)

def create_account(db: Session, name: str, account: str, level: int, min_account: bool, path: str, path_father: str, synonyms: list[str] = [], id: int = None) -> Cuenta:
    cuenta = Cuenta(nombre=name, cuenta=account, path=path, 
                    path_padre=path_father, nivel=level, cuenta_minima=min_account)

    if id:
        cuenta.id = id

    for synonym in synonyms:
        if not synonym or type(synonym) == float:
            continue
        sinonimo = Sinonimo(nombre=synonym)
        cuenta.sinonimos.append(sinonimo)
        db.add(sinonimo)

    db.add(cuenta)
    db.commit()
    db.refresh(cuenta)
    return cuenta

def create_synonym(db: Session, name: str, account_id: int, id: int = None) -> Sinonimo:
    sinonimo = Sinonimo(nombre=name, cuenta_id=account_id)

    if id:
        sinonimo.id = id
    
    db.add(sinonimo)
    db.commit()
    db.refresh(sinonimo)
    return sinonimo

def fetch_results_name(db: Session, model: Cuenta|Sinonimo, name: str, level: int = None) -> list:
    if model == Sinonimo:
        if level:
            results = db.query(Sinonimo).filter(Sinonimo.nombre == name, Sinonimo.cuenta.has(nivel=level)).all()
        else:
            results = db.query(Sinonimo).filter(Sinonimo.nombre == name).all()
    else:
        if level:
            results = db.query(Cuenta).filter(Cuenta.nombre == name, Cuenta.nivel == level).all()
        else:
            results = db.query(Cuenta).filter(Cuenta.nombre == name).all()
    if not results:
        return (None, 0)
    else:
        return (results, len(results))
    
def fetch_results_account_id(db: Session, id: str) -> list:
    result = db.query(Cuenta).filter(Cuenta.cuenta == id).first()
    return result
    
def to_account_db(cuenta: Cuenta) -> AccountDB:
    return AccountDB(nombre=cuenta.nombre, cuenta=cuenta.cuenta, nivel=cuenta.nivel, 
                     path=cuenta.path, path_padre=cuenta.path_padre, cuenta_minima=cuenta.cuenta_minima)

def fetch_all_accounts(db: Session) -> list[AccountDB]:
    results_db = db.query(Cuenta).all()
    results = [to_account_db(cuenta) for cuenta in results_db]
    return results

def search_account_db(db: Session, name: str = None, account_id: str = None, level: int = None) -> tuple[List[AccountDB], int]:

    if account_id:
        cuenta = fetch_results_account_id(db=db, id=account_id)
        if cuenta:
            return ([to_account_db(cuenta)], 1)
        else:
            return ([], 0)
    else:
        cuentas, cnt = fetch_results_name(db=db, model=Cuenta, name=name, level=level)

        if not cuentas:
            sinonimos, cnt = fetch_results_name(db=db, model=Sinonimo, name=name, level=level)

            if not sinonimos:
                return ([], 0)
            else:
                results = [to_account_db(s.cuenta) for s in sinonimos]
                return ([results[0]] if cnt == 1 else results, cnt)
        else:
            results = [to_account_db(c) for c in cuentas]
            return ([results[0]] if cnt == 1 else results, cnt)

def reset_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

def load_db():
    FILE_PATH = './accounts/accounts_full.csv'
    init_db()
    db = SessionLocal()
    df = pd.read_csv(FILE_PATH, delimiter=';')
    max_sinonimos = 10

    for index, row in df.iterrows():
        sinonimos = []
        for i in range(1,max_sinonimos+1):
            sinonimos.append(row[f'Sinónimo_{i}'])
        create_account(db=db, name=row['nombre'], account=row['cuenta'], level=row['nivel'],
                       path=row['ruta'], path_father=row['ruta_padre'], min_account=row['cuenta_minima'],
                       synonyms=sinonimos)