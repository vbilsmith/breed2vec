from breed2vec.db.connection import connect_db

def init_schema(reset: bool = False):
    """Initialize all database tables."""
    with connect_db() as con:
        if reset:
            _drop_tables(con)

        _init_breedgroup_schema(con)
        _init_breed_schema(con)
        _init_documents_schema(con)
        _create_document_embeddings_table(con)

def _drop_tables(con):
    # Order matters because of foreign keys
    con.execute("DROP TABLE IF EXISTS Documents")
    con.execute("DROP TABLE IF EXISTS BreedVarieties")
    con.execute("DROP TABLE IF EXISTS BreedInfo")
    con.execute("DROP TABLE IF EXISTS BreedGroups")

def _init_breedgroup_schema(con):
    con.execute("""
    CREATE TABLE IF NOT EXISTS BreedGroups (
        groupNum TEXT PRIMARY KEY,
        groupName TEXT NOT NULL,
        url TEXT NOT NULL UNIQUE
    )
    """)


def _init_breed_schema(con):
    con.execute("""
    CREATE TABLE IF NOT EXISTS BreedInfo (
        fciNumber INTEGER PRIMARY KEY,
        breedName TEXT NOT NULL,
        country TEXT,
        groupNum TEXT NOT NULL,
        breedPageUrl TEXT NOT NULL UNIQUE,
        standardPdfUrl TEXT,
        recognitionDate TEXT,
        recognitionStatus TEXT NOT NULL DEFAULT 'Definitive',
        lastSeen TEXT DEFAULT (datetime('now')),
        FOREIGN KEY (groupNum) REFERENCES BreedGroups(groupNum)
          ON UPDATE CASCADE
          ON DELETE RESTRICT
    )
    """)

    con.execute("""
    CREATE TABLE IF NOT EXISTS BreedVarieties (
        fciNumber INTEGER NOT NULL,
        variety TEXT NOT NULL,
        PRIMARY KEY (fciNumber, variety),
        FOREIGN KEY (fciNumber) REFERENCES BreedInfo(fciNumber)
          ON UPDATE CASCADE
          ON DELETE CASCADE
    )
    """)

    _ensure_breedinfo_columns(con)


def _init_documents_schema(con):
    con.execute("""
    CREATE TABLE IF NOT EXISTS Documents (
        fciNumber INTEGER PRIMARY KEY,
        breedName TEXT NOT NULL,
        standardPdfUrl TEXT NOT NULL,
        pdfPath TEXT NOT NULL,
        text TEXT,
        sha256 TEXT,
        downloadedAt TEXT DEFAULT (datetime('now')),
        FOREIGN KEY (fciNumber) REFERENCES BreedInfo(fciNumber)
          ON UPDATE CASCADE
          ON DELETE CASCADE
    )
    """)


def _ensure_breedinfo_columns(con):
    cur = con.execute("PRAGMA table_info(BreedInfo)")
    columns = {row[1] for row in cur.fetchall()}
    if "recognitionDate" not in columns:
        con.execute("ALTER TABLE BreedInfo ADD COLUMN recognitionDate TEXT")


def _create_document_embeddings_table(con):
    """
    Create a table for storing vector embeddings for documents.

    Embeddings are stored as float32 BLOBs and reconstructed in Python.
    This table is model-aware so the same document can have multiple
    embeddings (e.g., different models or chunking strategies).
    """
    con.execute(
        """
        CREATE TABLE IF NOT EXISTS DocumentEmbeddings (
            doc_sha     TEXT NOT NULL,
            model       TEXT NOT NULL,
            dim         INTEGER NOT NULL,
            dtype       TEXT NOT NULL DEFAULT 'float32',
            embedding   BLOB NOT NULL,
            created_at  TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

            PRIMARY KEY (doc_sha, model),
            FOREIGN KEY (doc_sha) REFERENCES Documents(doc_sha)
                ON DELETE CASCADE
        );
        """
    )

    con.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_document_embeddings_model
        ON DocumentEmbeddings(model);
        """
    )
