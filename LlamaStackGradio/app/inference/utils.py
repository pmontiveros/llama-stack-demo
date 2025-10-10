import pandas as pd
import re
from itertools import islice
try:
    from database.db import SessionLocal
    from database.models import Cuenta
except ImportError:
    from ..database.db import SessionLocal
    from ..database.models import Cuenta

def create_df_accounts():
    db = SessionLocal()
    cuentas = db.query(Cuenta).all()
    data = [{"id": c.id, 
             'nombre': c.nombre, 
             'nivel': c.nivel, 
             'ruta': c.path, 
             'padre': str(c.path_padre).split(' > ')[-1]} for c in cuentas]

    df = pd.DataFrame.from_records(data)
    df = df.set_index("id")
    df = df.sort_index()

    db.close()
    return df

def generate_prompt_Q1(account: str) -> str:

    df = create_df_accounts()
    prompt = f'''¿La cuenta de **{account}** corresponde a un ACTIVO, PASIVO, CAPITAL CONTABLE o CUENTAS DE ORDEN?

Solamente debes responder con las opciones que se te brindaron.'''

    df_n1 = df[df['nivel'] == 2].groupby('padre').agg(
            hijos=('nombre','; '.join)
            ).reset_index()

    context = ''
    for _, row in df_n1.iterrows():
        context += f'Las siguientes son cuentas de {row.padre}: {row.hijos}\n\n'

    prompt = context + prompt

    return prompt

def generate_prompt_Q2(account: str, response_account: str, level: int = 2) -> str:
    
    df = create_df_accounts()
    prompt = f'''¿A que cuenta de **{response_account}** corresponde **{account}**? 
    
Solamente debes responder con las opciones que se te brindaron en tu contexto.'''

    cuentas = df[(df['nivel'] == level) & (df['padre'] == response_account)]['nombre']
    cuentas_str = '; '.join(cuentas)
    context = f'\n\nPara contexto: Las siguientes son cuentas de **{response_account}**: {cuentas_str}'

    prompt = prompt + context

    return prompt

def generate_chunks(iterable: list, size: int):
    # Create an iterator from the input iterable
    iterator = iter(iterable)
    
    # Loop over the iterator, taking the first element in each iteration
    for first in iterator:
        # Yield a list consisting of the first element and the next 'size-1' elements from the iterator
        yield [first] + list(islice(iterator, size - 1))

def parse_hierarchy_response(response: str) -> list[str]:
    pattern = 'ACTIVO >|PASIVO >|CAPITAL CONTABLE >|CUENTAS DE ORDEN >'
    response_path = []

    for line in response.split('\n'):
        match = re.search(pattern, line)
        if match:
            start = match.start()
            response_path.append(line[start:].rstrip())

    return response_path

#print(generate_prompt_Q1(account='Caja'))
#print(generate_prompt_Q2(account='Caja', response_account='ACTIVO', level=2))

