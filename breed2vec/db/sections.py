"""
TODO: Persist extracted document sections.

Planned: store section text + metadata (breed, section label, offsets)
to support targeted comparisons (history vs morphology, etc.).
"""

# TODO: Proposed schema sketch (SQLite):
# CREATE TABLE IF NOT EXISTS BreedSections (
#   id INTEGER PRIMARY KEY AUTOINCREMENT,
#   fciNumber INTEGER NOT NULL,
#   breedName TEXT NOT NULL,
#   sectionLabel TEXT NOT NULL,
#   sectionOrder INTEGER,
#   pageStart INTEGER,
#   pageEnd INTEGER,
#   text TEXT NOT NULL,
#   sourceTracePath TEXT,
#   createdAt TEXT DEFAULT (datetime('now')),
#   FOREIGN KEY (fciNumber) REFERENCES BreedInfo(fciNumber)
#     ON UPDATE CASCADE
#     ON DELETE CASCADE
# );
