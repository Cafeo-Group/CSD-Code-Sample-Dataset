from psycopg2 import connect, extensions, extras
from os import getenv

def db_conn(db: str, password: str, user: str) -> extensions.connection:
    """Connects to the specified database.
    
    Args:
        db (str) - The name of the database to connect to.\n
        password (str) - The password for the user to connect with.\n
        user (str) - The user to connect with.\n
    
    Returns:
        psycopg2.extensions.connection: The connection object.
    """
    return connect(
        database = db,
        user = user,
        host = 'localhost',
        password = password,
        port = '5432'        
    )
    
def initialize_db():
    DB_PASSWORD = getenv('DB_PASSWORD')
    conn = db_conn('postgres', DB_PASSWORD, 'postgres')
    cursor = conn.cursor()
    conn.autocommit = True

    cursor.execute(f"""SELECT 1 FROM pg_catalog.pg_database WHERE datname = 'code_samples';""")
    db_exists = cursor.fetchone()

    if db_exists:
        cursor.execute("DROP DATABASE code_samples;")
        cursor.execute("DROP OWNED BY codesamples_user CASCADE;")

    cursor.execute("CREATE DATABASE code_samples;")

    cursor.execute(f"""SELECT 1 FROM pg_roles WHERE rolname = 'codesamples_user';""")
    user_exists = cursor.fetchone()

    if not user_exists:
        cursor.execute("CREATE USER codesamples_user WITH PASSWORD 'codesamples';")

    cursor.execute("GRANT ALL PRIVILEGES ON DATABASE code_samples TO codesamples_user;")

    cursor.close()
    conn.close()

    conn = db_conn('code_samples', DB_PASSWORD, 'postgres')
    conn.autocommit = True
    cursor = conn.cursor()

    cursor.execute("ALTER SCHEMA public OWNER TO codesamples_user;")

    cursor.execute("GRANT ALL ON SCHEMA public TO codesamples_user;")
    cursor.execute("ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO codesamples_user;")

    cursor.close()
    conn.close()

    conn = db_conn('code_samples', 'codesamples', 'codesamples_user')
    conn.autocommit = True
    cursor = conn.cursor()
    
    cursor.execute(f"""CREATE TABLE IF NOT EXISTS ecosystems (
        eco_name TEXT PRIMARY KEY
    );""")
    
    cursor.execute(f"""CREATE TABLE IF NOT EXISTS organizations (
        org_name TEXT PRIMARY KEY,
        eco_name TEXT,
        url TEXT,
        FOREIGN KEY (eco_name) REFERENCES ecosystems(eco_name)
    );""")
    
    cursor.execute(f"""CREATE TABLE IF NOT EXISTS repositories (
        repo_name TEXT,
        eco_name TEXT,
        org_name TEXT,
        stars INT,
        forks INT,
        watchers INT,
        contributors INT,
        language TEXT,
        size FLOAT,
        loc FLOAT,
        archived BOOLEAN,
        PRIMARY KEY (repo_name, org_name),
        FOREIGN KEY (eco_name) REFERENCES ecosystems(eco_name),
        FOREIGN KEY (org_name) REFERENCES organizations(org_name)
    );""")

    cursor.execute(f"""CREATE TABLE IF NOT EXISTS commits (
        sha TEXT,
        repo_name TEXT,
        org_name TEXT,
        timestamp TIMESTAMP,
        message TEXT,
        PRIMARY KEY (sha, repo_name, org_name),
        FOREIGN KEY (repo_name, org_name) REFERENCES repositories(repo_name, org_name)
    );""")
    
    cursor.execute(f"""CREATE TABLE IF NOT EXISTS files (
        file_name TEXT,
        repo_name TEXT,
        org_name TEXT,
        type TEXT,
        PRIMARY KEY (file_name, repo_name, org_name),
        FOREIGN KEY (repo_name, org_name) REFERENCES repositories(repo_name, org_name)
    );""")
    
    cursor.execute(f"""CREATE TABLE IF NOT EXISTS commit_files (
        repo_name TEXT,
        org_name TEXT,
        file_name TEXT,
        sha TEXT,
        content TEXT,
        change_type TEXT,
        file_mode TEXT,
        index_info TEXT,
        PRIMARY KEY (file_name, repo_name, org_name, sha),
        FOREIGN KEY (sha, repo_name, org_name) REFERENCES commits(sha, repo_name, org_name),
        FOREIGN KEY (file_name, repo_name, org_name) REFERENCES files(file_name, repo_name, org_name)
    );""")
    
    cursor.execute(f"""CREATE TABLE IF NOT EXISTS hunks (
        id SERIAL PRIMARY KEY,
        file_name TEXT,
        repo_name TEXT,
        org_name TEXT,
        sha TEXT,
        old_start INT,
        new_start INT,
        old_length INT,
        new_length INT,
        old_name TEXT,
        new_name TEXT,
        lines TEXT[],
        PRIMARY KEY (id),
        FOREIGN KEY (file_name, repo_name, org_name, sha) 
            REFERENCES commit_files(file_name, repo_name, org_name, sha)
        UNIQUE (file_name, repo_name, org_name, sha, old_start, new_start, old_length, new_length)
    );""")

    conn.commit()

    cursor.close()
    conn.close()
    
def general_add(table: str, values: dict):
    """Adds a row to the specified table.
    
    Args:
        table (str) - The name of the table to add the row to.\n
        values (dict) - The values to insert into the table.
    """
    conn = db_conn('code_samples', 'codesamples', 'codesamples_user')
    cursor = conn.cursor()
    
    columns = ', '.join(values.keys())
    placeholders = ', '.join([f'%({key})s' for key in values.keys()])
    
    cursor.execute(f"""INSERT INTO {table} ({columns}) VALUES ({placeholders});""", values)
    
    conn.commit()
    cursor.close()
    conn.close()
    
def general_add_in_batches(table: str, values: list):
    """Adds rows to the specified table in batches.
    
    Args:
        table (str) - The name of the table to add the rows to.\n
        values (list) - The values to insert into the table.
    """
    conn = db_conn('code_samples', 'codesamples', 'codesamples_user')
    cursor = conn.cursor()
    
    columns = ', '.join(values[0].keys())
    placeholders = ', '.join([f'%({key})s' for key in values[0].keys()])
    
    batch_size = 3000
    
    for i in range(0, len(values), batch_size):
        batch = values[i:i + batch_size]
        extras.execute_batch(cursor, f"""INSERT INTO {table} ({columns}) VALUES ({placeholders}) ON CONFLICT DO NOTHING;""", batch)
    
    conn.commit()
    cursor.close()
    conn.close()
    
def general_exists_in_batches(table: str, values: list) -> list:
    """Checks if rows exist in the specified table in batches.
    
    Args:
        table (str) - The name of the table to check.\n
        values (list) - The values to check for in the table.
        
    Returns:
        list: A list of True/False values for each row in the batch.
    """
    conn = db_conn('code_samples', 'codesamples', 'codesamples_user')
    cursor = conn.cursor()
    
    columns = ' AND '.join([f'{key} = %({key})s' for key in values[0].keys()])
    
    batch_size = 3000
    exists = []
    
    for i in range(0, len(values), batch_size):
        batch = values[i:i + batch_size]
        for row in batch:
            cursor.execute(f"""SELECT 1 FROM {table} WHERE {columns};""", row)
            exists.append(cursor.fetchone())
    
    cursor.close()
    conn.close()
    
    return exists
    
def general_exists(table: str, values: dict) -> bool:
    """Checks if a row exists in the specified table.
    
    Args:
        table (str) - The name of the table to check.\n
        values (dict) - The values to check for in the table.
        
    Returns:
        bool: True if the row exists in the table, False otherwise.
    """
    conn = db_conn('code_samples', 'codesamples', 'codesamples_user')
    cursor = conn.cursor()
    
    columns = ' AND '.join([f'{key} = %({key})s' for key in values.keys()])
    
    cursor.execute(f"""SELECT 1 FROM {table} WHERE {columns};""", values)
    exists = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    return exists

def general_fetch_by_args(table: str, values: dict) -> list:
    """Fetches rows from the specified table by unknown arguments.
    
    Args:
        table (str) - The name of the table to fetch from.\n
        values (dict) - The values to fetch from the table.
        
    Returns:
        list: A list of all rows in the table that match the values.
    """
    conn = db_conn('code_samples', 'codesamples', 'codesamples_user')
    cursor = conn.cursor()
    
    columns = ' AND '.join([f'{key} = %({key})s' for key in values.keys()])
    
    cursor.execute(f"""SELECT * FROM {table} WHERE {columns};""", values)
    rows = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    return rows

def general_fetch_all(table: str) -> list:
    """Fetches all rows from the specified table.
    
    Args:
        table (str) - The name of the table to fetch from.
        
    Returns:
        list: A list of all rows in the table.
    """
    conn = db_conn('code_samples', 'codesamples', 'codesamples_user')
    cursor = conn.cursor()
    
    cursor.execute(f"""SELECT * FROM {table};""")
    rows = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return rows