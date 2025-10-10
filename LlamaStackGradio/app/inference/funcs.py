from pathlib import Path
from llama_stack_client.lib.agents.agent import Agent
from llama_stack_client.types.agents.turn import Turn
from llama_stack_client.types import Document, UserMessage
try:
    from ..client import client, MODEL, VECTOR_DB_ID, EMBEDDING_MODEL, SESSION_NAME
except ImportError:
    from client import client, MODEL, VECTOR_DB_ID, EMBEDDING_MODEL, SESSION_NAME
from os import listdir
from os.path import isfile, join, exists
import base64
import mimetypes

def data_url_from_file(file_path: str) -> str:
    if not exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    with open(file_path, "rb") as file:
        file_content = file.read()

    base64_content = base64.b64encode(file_content).decode("utf-8")
    mime_type, _ = mimetypes.guess_type(file_path)

    data_url = f"data:{mime_type};base64,{base64_content}"
    return data_url

def create_rag(vector_db_id: str = None):
    vector_providers = [
        provider for provider in client.providers.list() if provider.api == "vector_io"
    ]
    if not vector_providers:
        raise Exception('No available vector_io providers.')

    selected_vector_provider = vector_providers[0]

    # Create new rag
    client.vector_dbs.register(
        vector_db_id=vector_db_id if vector_db_id else VECTOR_DB_ID,
        embedding_model=EMBEDDING_MODEL,
        embedding_dimension=384,
        provider_id=selected_vector_provider.provider_id,
    )

def clear_rag(vector_db_id: str) -> None:
    # Delete existing rag
    try:
        client.vector_dbs.unregister(vector_db_id)
        global fileid 
        fileid = 1
    except Exception:
        pass

    create_rag(vector_db_id=vector_db_id)
    return

def get_mime_type(file_extension: str):
    mime_type = 'text/plain'

    if file_extension == '.csv':
        mime_type = 'text/csv'
    elif file_extension == '.json':
        mime_type = 'application/json'

    return mime_type


def load_rag(documents: list[dict], vector_db_id: str, truncate_rag: bool = False, chunk_size_in_tokens: int = 64) -> bool:

    if 'fileid' not in globals():
        global fileid
        fileid = 1

    parsed_documents = []

    if truncate_rag:
        clear_rag()

    # Chunk size
    n = 100
    batchs = [documents[i:i + n] for i in range(0, len(documents), n)]

    try:
        for batch in batchs:
            for document in batch:
                parsed_doc = Document(
                    document_id=f'{document["file"]}{document["file_extension"]}-{fileid}',
                    content=document["content"],
                    mime_type=get_mime_type(document["file_extension"]),
                    metadata={},
                )
                parsed_documents.append(parsed_doc)
                fileid += 1
                
            # Insert documents using the RAG tool
            client.tool_runtime.rag_tool.insert(
                documents=parsed_documents,
                vector_db_id=vector_db_id,
                chunk_size_in_tokens=chunk_size_in_tokens,
            )

    except Exception as e:
        print(e)
        return False
    return True

def load_files(folder: str):

    documents = []
    errors = []

    all_file_paths = [join(folder, f) for f in listdir(folder) if isfile(join(folder, f))]

    for file_path in all_file_paths:
        try:
            file_name = Path(file_path).stem
            file_extension = Path(file_path).suffix
            file = open(file_path, "r", encoding='utf-8')
            content = file.read()
            file.close()
            document = {'file': file_name, 'content': content, 'file_extension': file_extension}
            documents.append(document)
        except Exception:
            errors.append(f'Error loading file {file_path}. Skipping')
            continue

    loaded_rag = load_rag(documents)
    if loaded_rag:
        if len(errors) > 0:
            print("\n".join(errors))
    return

def inference_with_rag(prompt: str, root_prompt: str = None, enable_rag: bool = False, vector_db_ids: list[str] = []) -> Turn:
    available_shields = [shield.identifier for shield in client.shields.list()]

    toolgroups = []

    if enable_rag:
        rag_tool = {
                "name": "builtin::rag/knowledge_search",
                "args": {"vector_db_ids": vector_db_ids},
                }
        toolgroups.append(rag_tool)

    root_prompt = "" if root_prompt == None else root_prompt

    agent = Agent(client, 
                  model=MODEL, 
                  instructions=root_prompt,
                  sampling_params={
            "strategy": {"type": "greedy"},
        },
        tools=toolgroups,
        input_shields=available_shields if available_shields else [],
        output_shields=available_shields if available_shields else [],
        enable_session_persistence=False)
    session_id = agent.create_session(SESSION_NAME)

    response = agent.create_turn(
            messages=[
                UserMessage(role='user', content=prompt),
            ],
            session_id=session_id,
            stream=False
    )

    return response

def get_context(response: Turn) -> str:
    try:
        context_map = map(lambda x: x.text, response.input_messages[0].context)
        context = ''.join(list(context_map))
    except Exception:
        #print(f'Error al obtener el contexto. Revisar si hay algo cargado en el RAG.\nResponse: {response}')
        return
    return context

def get_output(response: Turn) -> str:
    return response.output_message.content

def inference_chat(prompt: str, root_prompt: str, enable_rag: bool = True, vector_db_ids: list[str] = None) -> tuple[str, str]:
    response = inference_with_rag(prompt=prompt, 
                                  root_prompt=root_prompt, 
                                  enable_rag=enable_rag,
                                  vector_db_ids=vector_db_ids)
    return (get_output(response), get_context(response))

def query_rag(query: str, vector_db_id: str) -> str:
    response = client.vector_io.query(vector_db_id=vector_db_id,
                       query=f'{query}')
    context = '\n\n'.join([chunk.content for chunk in response.chunks])
    
    return context

def prompt_generator(account: str) -> str:
    rag_response = query_rag(query=account, vector_db_id=VECTOR_DB_ID)

    prompt = f"""Dispones del siguiente contexto ```{rag_response}```
    
    Tu tarea es responder a que cuenta corresponde la siguiente: ```{account}```
    """
    return prompt

def prompt_account_mispelling(account: str):
    VDI_ACCOUNTS_NO_QUOTES = 'accounts_no_quotes'

    # Check if account is in context, if so then go back to lookup
    prompt = f'''Dispones del siguiente contexto 
```
{query_rag(query=account, vector_db_id=VDI_ACCOUNTS_NO_QUOTES)}
```

Debes responder si en el contexto se encuentra "{account}" respondiendo con el nombre bien escrito.
No agregues ninguna explicacion ni informacion adicional.'''
    
    response = inference_with_rag(prompt, enable_rag=False)
    output = get_output(response)

    return [prompt,output]


def get_vector_dbs() -> list[str]:
    try:
        vector_dbs = [vector_db.identifier for vector_db in client.vector_dbs.list()]
    except Exception:
        vector_dbs = ['Error Loading Vector DBs',]
    
    return vector_dbs