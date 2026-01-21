"""
JuraConnect - Datenbank-Modul
SQLite-Datenbank für Akten, Mandanten, Fristen
"""

import sqlite3
from datetime import datetime, date, timedelta
from dataclasses import dataclass
from typing import List, Dict, Optional
from pathlib import Path


@dataclass
class Mandant:
    id: Optional[int] = None
    typ: str = "person"
    anrede: str = ""
    vorname: str = ""
    nachname: str = ""
    firma: str = ""
    strasse: str = ""
    plz: str = ""
    ort: str = ""
    telefon: str = ""
    email: str = ""
    erstellt_am: str = ""
    
    @property
    def name_komplett(self) -> str:
        return self.firma if self.typ == "firma" else f"{self.vorname} {self.nachname}".strip()


@dataclass
class Akte:
    id: Optional[int] = None
    aktenzeichen: str = ""
    rubrum: str = ""
    mandant_id: int = 0
    gegner_name: str = ""
    sachgebiet: str = "Arbeitsrecht"
    status: str = "aktiv"
    angelegt_am: str = ""
    streitwert: float = 0.0
    notizen: str = ""


@dataclass
class Frist:
    id: Optional[int] = None
    akte_id: int = 0
    bezeichnung: str = ""
    fristdatum: str = ""
    vorfrist: str = ""
    erledigt: bool = False
    prioritaet: str = "normal"
    notizen: str = ""


@dataclass
class Dokument:
    id: Optional[int] = None
    akte_id: int = 0
    titel: str = ""
    kategorie: str = ""
    dateiname: str = ""
    dateipfad: str = ""
    datum: str = ""


class JuraConnectDB:
    """Datenbank-Klasse für JuraConnect"""
    
    def __init__(self, db_pfad: str = None):
        if db_pfad is None:
            home = Path.home()
            db_dir = home / ".juraconnect"
            db_dir.mkdir(exist_ok=True)
            db_pfad = str(db_dir / "juraconnect.db")
        
        self.db_pfad = db_pfad
        self._init_db()
    
    def _init_db(self):
        with sqlite3.connect(self.db_pfad) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS mandanten (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    typ TEXT DEFAULT 'person',
                    anrede TEXT, vorname TEXT, nachname TEXT, firma TEXT,
                    strasse TEXT, plz TEXT, ort TEXT, telefon TEXT, email TEXT,
                    erstellt_am TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS akten (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    aktenzeichen TEXT UNIQUE, rubrum TEXT, mandant_id INTEGER,
                    gegner_name TEXT, sachgebiet TEXT DEFAULT 'Arbeitsrecht',
                    status TEXT DEFAULT 'aktiv', angelegt_am TEXT DEFAULT CURRENT_TIMESTAMP,
                    streitwert REAL DEFAULT 0, notizen TEXT,
                    FOREIGN KEY (mandant_id) REFERENCES mandanten(id)
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS fristen (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    akte_id INTEGER, bezeichnung TEXT, fristdatum TEXT,
                    vorfrist TEXT, erledigt INTEGER DEFAULT 0,
                    prioritaet TEXT DEFAULT 'normal', notizen TEXT,
                    FOREIGN KEY (akte_id) REFERENCES akten(id)
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS dokumente (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    akte_id INTEGER, titel TEXT, kategorie TEXT,
                    dateiname TEXT, dateipfad TEXT, datum TEXT,
                    FOREIGN KEY (akte_id) REFERENCES akten(id)
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS zeiterfassung (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    akte_id INTEGER, datum TEXT, dauer_minuten INTEGER,
                    taetigkeit TEXT, bearbeiter TEXT, abrechenbar INTEGER DEFAULT 1,
                    FOREIGN KEY (akte_id) REFERENCES akten(id)
                )
            """)
            
            conn.commit()
    
    def mandant_erstellen(self, mandant: Mandant) -> int:
        with sqlite3.connect(self.db_pfad) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO mandanten (typ, anrede, vorname, nachname, firma,
                    strasse, plz, ort, telefon, email)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (mandant.typ, mandant.anrede, mandant.vorname, mandant.nachname,
                  mandant.firma, mandant.strasse, mandant.plz, mandant.ort,
                  mandant.telefon, mandant.email))
            conn.commit()
            return cursor.lastrowid
    
    def mandanten_suchen(self, suchbegriff: str = "") -> List[Mandant]:
        with sqlite3.connect(self.db_pfad) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            if suchbegriff:
                cursor.execute("""
                    SELECT * FROM mandanten 
                    WHERE vorname LIKE ? OR nachname LIKE ? OR firma LIKE ?
                    ORDER BY nachname
                """, (f"%{suchbegriff}%",) * 3)
            else:
                cursor.execute("SELECT * FROM mandanten ORDER BY nachname")
            return [Mandant(**dict(row)) for row in cursor.fetchall()]
    
    def akte_erstellen(self, akte: Akte) -> int:
        with sqlite3.connect(self.db_pfad) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO akten (aktenzeichen, rubrum, mandant_id, gegner_name,
                    sachgebiet, status, streitwert, notizen)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (akte.aktenzeichen, akte.rubrum, akte.mandant_id, akte.gegner_name,
                  akte.sachgebiet, akte.status, akte.streitwert, akte.notizen))
            conn.commit()
            return cursor.lastrowid
    
    def akten_laden(self, status: str = None) -> List[Akte]:
        with sqlite3.connect(self.db_pfad) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            if status:
                cursor.execute("SELECT * FROM akten WHERE status = ? ORDER BY angelegt_am DESC", (status,))
            else:
                cursor.execute("SELECT * FROM akten ORDER BY angelegt_am DESC")
            return [Akte(**dict(row)) for row in cursor.fetchall()]
    
    def frist_erstellen(self, frist: Frist) -> int:
        with sqlite3.connect(self.db_pfad) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO fristen (akte_id, bezeichnung, fristdatum, vorfrist,
                    erledigt, prioritaet, notizen)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (frist.akte_id, frist.bezeichnung, frist.fristdatum,
                  frist.vorfrist, frist.erledigt, frist.prioritaet, frist.notizen))
            conn.commit()
            return cursor.lastrowid
    
    def fristen_laden(self, nur_offen: bool = True) -> List[Frist]:
        with sqlite3.connect(self.db_pfad) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            if nur_offen:
                cursor.execute("SELECT * FROM fristen WHERE erledigt = 0 ORDER BY fristdatum")
            else:
                cursor.execute("SELECT * FROM fristen ORDER BY fristdatum")
            return [Frist(**dict(row)) for row in cursor.fetchall()]
    
    def statistik_dashboard(self) -> Dict:
        with sqlite3.connect(self.db_pfad) as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM akten WHERE status = 'aktiv'")
            aktive_akten = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM mandanten")
            mandanten = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM fristen WHERE erledigt = 0")
            offene_fristen = cursor.fetchone()[0]
            
            heute = date.today().isoformat()
            cursor.execute("SELECT COUNT(*) FROM fristen WHERE fristdatum < ? AND erledigt = 0", (heute,))
            ueberfaellig = cursor.fetchone()[0]
            
            return {
                "aktive_akten": aktive_akten,
                "mandanten": mandanten,
                "offene_fristen": offene_fristen,
                "ueberfaellige_fristen": ueberfaellig
            }


_db_instance = None

def get_db(db_pfad: str = None) -> JuraConnectDB:
    global _db_instance
    if _db_instance is None:
        _db_instance = JuraConnectDB(db_pfad)
    return _db_instance
