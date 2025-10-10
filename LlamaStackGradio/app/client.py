from llama_stack_client import LlamaStackClient

### Llama Params ###
HOST = "20.72.80.241"
PORT = 5001
MODEL = "meta-llama/Llama-3.2-3B-Instruct"
VECTOR_DB_ID = 'accounts_no_quotes'
EMBEDDING_MODEL = 'all-MiniLM-L6-v2'
SESSION_NAME = 'test-rag-accounts'

client = LlamaStackClient(
    base_url=f"http://{HOST}:{PORT}",
)

### Database Conection ###
# SQLite
DATABASE_URL = "sqlite:///accounts.db"
# SQL Server - Requiere pyodbc
#database_url = 'mssql+pyodbc://usuario:password@dsn'

