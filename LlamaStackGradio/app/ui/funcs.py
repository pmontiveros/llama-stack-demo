from pathlib import Path
from .gr_types import GRDocument
from llama_stack_client import APIConnectionError
from inference.funcs import (clear_rag, 
                   load_rag, 
                   data_url_from_file,
                   inference_chat,
                   get_vector_dbs,
                   query_rag,
                   create_rag,
                   client)

is_service_up = False

def gr_convert_files(file_paths: list[str]) -> list[GRDocument]:
    documents = []
    for file_path in file_paths:
        file_name = Path(file_path).stem
        file_extension = Path(file_path).suffix
        if file_extension == '.pdf':
            content = data_url_from_file(file_path)
        else:
            file = open(file_path, "r", encoding='utf-8')
            content = file.read()
            file.close()
        document = GRDocument(file=file_name,
                                file_extension=file_extension,
                                content=content,
                                path=file_path)
        documents.append(document)

    return documents

def gr_clear_rag(vector_db_id: str) -> str:
    try:
        clear_rag(vector_db_id=vector_db_id)
        response = '<span style="color:green">The RAG has been cleaned out.</span>'
    except Exception:
        response = '<span style="color:red">Error cleaning the RAG.</span>'
    return response

def gr_load_files(file_paths: list[str], file_paths_folder: list[str], vector_db_id: str, chunk_size_in_tokens: int = 128):

    if not vector_db_id:
        return '<span style="color:orange">No se selecciono ninguna DB.</span>'

    file_paths = [] if not file_paths else file_paths
    file_paths_folder = [] if not file_paths_folder else file_paths_folder
    all_file_paths = file_paths + file_paths_folder

    gr_documents = gr_convert_files(all_file_paths)

    loaded_rag = load_rag(documents=gr_documents
                          ,vector_db_id=vector_db_id
                          ,chunk_size_in_tokens=chunk_size_in_tokens)
    if loaded_rag:
        response = '<span style="color:green">Los archivos se cargaron con exito.</span>'
    else:
        response = '<span style="color:red">Error cargando los archivos al RAG.</span>'
    return response

def gr_format_sinonimo_txt(c) -> str:
    result = f'Nombre Cuenta: {c["nombre"]}\nCuenta: {c["cuenta"]}\nPath: {c["path"]}'
    return result

def gr_format_record_txt(r) -> str:
    result = f'Nombre Cuenta: {r["descripcion"]}\nCuenta: {r["account_id"]}\nPath: {r["path"]}'
    return result


def gr_inference(prompt: str, root_prompt: str, vector_db_ids: list[str], rag_mode: str = 'Directo') -> tuple[str, str]:

    if rag_mode == 'Agente':
        response, context = inference_chat(prompt=prompt, 
                                        root_prompt=root_prompt, 
                                        enable_rag=True,
                                        vector_db_ids=vector_db_ids)
    elif rag_mode == 'Directo':
        rag_response = client.tool_runtime.rag_tool.query(
            content=prompt, vector_db_ids=list(vector_db_ids)
        )
        try:
            prompt_context = rag_response.content
            prompt_context_window = '\n\n'.join(f'{i}: {x.text}' for i, x in enumerate(rag_response.content))
        except Exception:
            prompt_context = rag_response.content
            prompt_context_window = prompt_context
        extended_prompt = f"Por favor responde la siguiente consulta utilizando el contexto debajo.\n\nCONTEXTO:\n{prompt_context}\n\nCONSULTA:\n{prompt}"
        response, _ = inference_chat(prompt=extended_prompt, 
                                        root_prompt=root_prompt, 
                                        enable_rag=False)
        context = prompt_context_window
    result = (response, context)
    return result

def gr_get_vector_dbs() -> list[str]:
    return get_vector_dbs()

def gr_query_rag(query: str, vector_db_id: str) -> str:
    rag_response = query_rag(query, vector_db_id)

    return rag_response

def gr_create_rag(vector_db_id: str) -> str:
    if vector_db_id not in gr_get_vector_dbs():
        create_rag(vector_db_id)
        return '<span style="color:green">Se creo la DB con exito.</span>'
    else:
        return '<span style="color:orange">Ya existe la DB.</span>'
    
def update_is_service_up() -> None:
    global is_service_up
    try:
        client.models.list()
        is_service_up = True
    except APIConnectionError:
        is_service_up = False

def gr_health_check() -> str:
    update_is_service_up()

    if is_service_up:
        return '<h3 style="color:green;font-weight: bold;">El servicio LLM esta encendido.</h3>'
    else:
        return '<h3 style="color:red;font-weight: bold;">El servicio LLM esta apagado.</h3>'