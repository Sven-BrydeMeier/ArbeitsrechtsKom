"""
JuraConnect - RA-Micro Aktenimport Modul
=========================================
Importiert Akten aus RA-Micro PDF-Exporten mit:
- Aktenvorblatt-Erkennung
- Parteien-Extraktion
- Dokumentklassifizierung (30+ Muster)
- OCR für gescannte PDFs
- Batch-Import für mehrere Akten
- JuraConnect-Integration

Version: 2.0.0
"""

import os
import re
import json
import tempfile
from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import io

# PDF-Verarbeitung
try:
    import pdfplumber
    from pypdf import PdfReader, PdfWriter
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    print("⚠️ PDF-Bibliotheken nicht verfügbar")

# OCR-Unterstützung (optional)
try:
    from PIL import Image
    import pytesseract
    from pdf2image import convert_from_path
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False


@dataclass
class Partei:
    """Repräsentiert eine Partei (Auftraggeber, Gegner, etc.)"""
    rolle: str = ""
    name: str = ""
    anschrift: str = ""
    plz_ort: str = ""
    telefon1: str = ""
    telefon2: str = ""
    fax: str = ""
    email: str = ""
    ansprechpartner: str = ""


@dataclass
class Aktenvorblatt:
    """Daten aus dem Aktenvorblatt einer RA-Micro Akte"""
    rubrum: str = ""
    aktennummer: str = ""
    wegen: str = ""
    gegenstandswert: float = 0.0
    angelegt_am: str = ""
    instanz_1_gericht: str = ""
    instanz_1_az: str = ""
    instanz_2_gericht: str = ""
    instanz_2_az: str = ""
    rechtsgebiet: str = "Arbeitsrecht"
    parteien: List[Partei] = field(default_factory=list)


@dataclass
class Dokument:
    """Ein einzelnes Dokument innerhalb der Akte"""
    id: int = 0
    titel: str = ""
    kategorie: str = ""
    seite_von: int = 0
    seite_bis: int = 0
    datum: str = ""
    inhalt_vorschau: str = ""
    dateiname: str = ""
    ocr_text: str = ""
    konfidenz: float = 0.0


@dataclass
class ImportErgebnis:
    """Ergebnis eines Aktenimports"""
    erfolg: bool = True
    aktenvorblatt: Optional[Aktenvorblatt] = None
    dokumente: List[Dokument] = field(default_factory=list)
    qualitaet: str = "gut"
    qualitaet_score: int = 0
    fehler: List[str] = field(default_factory=list)
    warnungen: List[str] = field(default_factory=list)


class RAMicroAktenImporter:
    """
    Importiert RA-Micro Akten aus PDF-Exporten.
    
    Unterstützt:
    - Automatische Erkennung des Aktenformblatts
    - Extraktion aller Parteien
    - Klassifizierung von 30+ Dokumenttypen
    - OCR für gescannte Dokumente
    """
    
    # Dokumentmuster für Klassifizierung
    DOKUMENT_MUSTER = [
        # Gerichtliche Dokumente
        (r"Arbeitsgericht\s+\w+.*(?:Az|Aktenzeichen)", "Gerichtsdokument", "Gericht"),
        (r"Landesarbeitsgericht", "LAG-Dokument", "Gericht"),
        (r"Bundesarbeitsgericht", "BAG-Dokument", "Gericht"),
        (r"(?:Güte|Kammer)termin.*(?:anberaumt|festgesetzt)", "Ladung", "Gericht"),
        (r"Mahnbescheid", "Mahnbescheid", "Gericht"),
        (r"Vollstreckungsbescheid", "Vollstreckungsbescheid", "Gericht"),
        (r"Urteil\s*(?:im Namen|des Volkes)", "Urteil", "Gericht"),
        (r"Beschluss", "Beschluss", "Gericht"),
        (r"Versäumnisurteil", "Versäumnisurteil", "Gericht"),
        
        # Schriftsätze
        (r"Kündigungsschutzklage", "Kündigungsschutzklage", "Schriftsatz"),
        (r"Klageerwiderung", "Klageerwiderung", "Schriftsatz"),
        (r"Schriftsatz.*(?:Kläger|Beklagte)", "Schriftsatz", "Schriftsatz"),
        (r"Antrag auf.*(?:PKH|Prozesskostenhilfe)", "PKH-Antrag", "Schriftsatz"),
        (r"Berufungsbegründung", "Berufungsbegründung", "Schriftsatz"),
        
        # Verträge
        (r"Arbeitsvertrag|Anstellungsvertrag", "Arbeitsvertrag", "Vertrag"),
        (r"Aufhebungsvertrag", "Aufhebungsvertrag", "Vertrag"),
        (r"Änderungsvertrag", "Änderungsvertrag", "Vertrag"),
        (r"Abwicklungsvertrag", "Abwicklungsvertrag", "Vertrag"),
        (r"Vergleich.*(?:geschlossen|vereinbart)", "Vergleich", "Vertrag"),
        
        # Arbeitgeber-Dokumente
        (r"Kündigung.*(?:hiermit|fristgerecht|fristlos)", "Kündigung", "Arbeitgeber"),
        (r"Abmahnung", "Abmahnung", "Arbeitgeber"),
        (r"Zeugnis|Arbeitszeugnis", "Arbeitszeugnis", "Arbeitgeber"),
        (r"Betriebsratsanhörung|§\s*102\s*BetrVG", "BR-Anhörung", "Arbeitgeber"),
        (r"Gehaltsabrechnung|Lohnabrechnung", "Gehaltsabrechnung", "Arbeitgeber"),
        
        # Korrespondenz
        (r"(?:Von|From):.*@.*\n.*(?:An|To):", "E-Mail", "Korrespondenz"),
        (r"Sehr geehrte.*Herr|Frau", "Schreiben", "Korrespondenz"),
        (r"Mit freundlichen Grüßen", "Schreiben", "Korrespondenz"),
        (r"Rechtsschutzversicherung|RSV", "RSV-Korrespondenz", "Korrespondenz"),
        (r"Deckungszusage", "Deckungszusage", "Korrespondenz"),
        
        # Sonstiges
        (r"Rechnung|Honorar", "Rechnung", "Finanzen"),
        (r"Vollmacht", "Vollmacht", "Sonstiges"),
        (r"Personalakte", "Personalakte", "Sonstiges"),
    ]
    
    def __init__(self, pdf_path: str = None, output_dir: str = None):
        self.pdf_path = pdf_path
        self.output_dir = output_dir or tempfile.mkdtemp()
        self.aktenvorblatt: Optional[Aktenvorblatt] = None
        self.dokumente: List[Dokument] = []
        self.total_pages = 0
        self.ocr_verwendet = False
        
    def analysiere_pdf(self, pdf_content: bytes = None) -> ImportErgebnis:
        """
        Analysiert eine RA-Micro Akten-PDF.
        
        Args:
            pdf_content: Optional - PDF als Bytes (alternativ zu pdf_path)
            
        Returns:
            ImportErgebnis mit allen extrahierten Daten
        """
        if not PDF_AVAILABLE:
            return ImportErgebnis(erfolg=False, fehler=["PDF-Bibliotheken nicht installiert"])
        
        ergebnis = ImportErgebnis()
        
        try:
            # PDF öffnen
            if pdf_content:
                pdf_file = io.BytesIO(pdf_content)
            else:
                pdf_file = self.pdf_path
                
            with pdfplumber.open(pdf_file) as pdf:
                self.total_pages = len(pdf.pages)
                
                # 1. Aktenvorblatt extrahieren
                self.aktenvorblatt = self._extrahiere_aktenvorblatt(pdf)
                ergebnis.aktenvorblatt = self.aktenvorblatt
                
                # 2. Dokumente erkennen
                self._erkenne_dokumente(pdf)
                ergebnis.dokumente = self.dokumente
                
                # 3. Qualitätsbewertung
                ergebnis.qualitaet_score = self._bewerte_qualitaet()
                ergebnis.qualitaet = self._qualitaet_text(ergebnis.qualitaet_score)
                
        except Exception as e:
            ergebnis.erfolg = False
            ergebnis.fehler.append(f"Fehler bei PDF-Analyse: {str(e)}")
            
        return ergebnis
    
    def _extrahiere_aktenvorblatt(self, pdf) -> Aktenvorblatt:
        """Extrahiert das Aktenvorblatt aus der ersten Seite."""
        av = Aktenvorblatt()
        
        if not pdf.pages:
            return av
            
        text = pdf.pages[0].extract_text() or ""
        
        # Rubrum (z.B. "Müller ./. Schmidt GmbH")
        rubrum_match = re.search(r"([A-ZÄÖÜ][a-zäöüß]+(?:\s+[A-ZÄÖÜ][a-zäöüß]+)*)\s*\./\.\s*(.+?)(?:\n|$)", text)
        if rubrum_match:
            av.rubrum = f"{rubrum_match.group(1)} ./. {rubrum_match.group(2).strip()}"
        
        # Aktennummer
        az_match = re.search(r"(?:Aktennummer|Aktenzeichen|Az\.?)[\s:]*(\d+[/-]\d+(?:[/-]\d+)?)", text, re.IGNORECASE)
        if az_match:
            av.aktennummer = az_match.group(1)
        
        # Wegen (Kündigungsschutz, Lohn, etc.)
        wegen_match = re.search(r"(?:wegen|Streitgegenstand)[\s:]*([^\n]+)", text, re.IGNORECASE)
        if wegen_match:
            av.wegen = wegen_match.group(1).strip()
        
        # Gegenstandswert
        wert_match = re.search(r"(?:Gegenstandswert|Streitwert)[\s:]*(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?)\s*(?:€|EUR)?", text, re.IGNORECASE)
        if wert_match:
            wert_str = wert_match.group(1).replace(".", "").replace(",", ".")
            try:
                av.gegenstandswert = float(wert_str)
            except:
                pass
        
        # Angelegt am
        datum_match = re.search(r"(?:Angelegt|Erfasst|Datum)[\s:]*(\d{2}[./-]\d{2}[./-]\d{4})", text, re.IGNORECASE)
        if datum_match:
            av.angelegt_am = datum_match.group(1)
        
        # Gericht 1. Instanz
        gericht_match = re.search(r"(?:1\.\s*Instanz|Arbeitsgericht)[\s:]*([^\n]+)", text, re.IGNORECASE)
        if gericht_match:
            av.instanz_1_gericht = gericht_match.group(1).strip()
        
        # Parteien extrahieren
        av.parteien = self._extrahiere_parteien(text)
        
        return av
    
    def _extrahiere_parteien(self, text: str) -> List[Partei]:
        """Extrahiert Parteien aus dem Aktenvorblatt-Text."""
        parteien = []
        
        # Auftraggeber/Mandant
        auftraggeber_match = re.search(
            r"(?:Auftraggeber|Mandant|Kläger)[\s:]*\n?(.*?)(?=(?:Gegner|Beklagter|$))",
            text, re.DOTALL | re.IGNORECASE
        )
        if auftraggeber_match:
            partei = self._parse_partei_block(auftraggeber_match.group(1), "Auftraggeber")
            if partei:
                parteien.append(partei)
        
        # Gegner
        gegner_match = re.search(
            r"(?:Gegner|Beklagter?)[\s:]*\n?(.*?)(?=(?:Gegnervertreter|Rechtsanwalt|$))",
            text, re.DOTALL | re.IGNORECASE
        )
        if gegner_match:
            partei = self._parse_partei_block(gegner_match.group(1), "Gegner")
            if partei:
                parteien.append(partei)
        
        # Gegnervertreter
        gegnervertreter_match = re.search(
            r"(?:Gegnervertreter|Rechtsanwalt.*Gegner)[\s:]*\n?(.*?)(?=\n\n|$)",
            text, re.DOTALL | re.IGNORECASE
        )
        if gegnervertreter_match:
            partei = self._parse_partei_block(gegnervertreter_match.group(1), "Gegnervertreter")
            if partei:
                parteien.append(partei)
        
        return parteien
    
    def _parse_partei_block(self, block: str, rolle: str) -> Optional[Partei]:
        """Parst einen Textblock zu einer Partei."""
        if not block or len(block.strip()) < 5:
            return None
            
        partei = Partei(rolle=rolle)
        lines = [l.strip() for l in block.split("\n") if l.strip()]
        
        if lines:
            partei.name = lines[0]
        
        # Adresse (zweite Zeile oft Straße)
        if len(lines) > 1:
            partei.anschrift = lines[1]
        
        # PLZ/Ort
        plz_match = re.search(r"(\d{5})\s+(.+)", block)
        if plz_match:
            partei.plz_ort = f"{plz_match.group(1)} {plz_match.group(2).strip()}"
        
        # Telefon
        tel_match = re.search(r"(?:Tel|Telefon|Fon)[\s.:]*([0-9\s/\-]+)", block, re.IGNORECASE)
        if tel_match:
            partei.telefon1 = tel_match.group(1).strip()
        
        # E-Mail
        email_match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", block)
        if email_match:
            partei.email = email_match.group(0)
        
        return partei if partei.name else None
    
    def _erkenne_dokumente(self, pdf) -> None:
        """Erkennt die einzelnen Dokumente innerhalb der PDF."""
        dokumente = []
        current_doc = None
        doc_id = 0
        
        for i, page in enumerate(pdf.pages):
            text = page.extract_text() or ""
            page_num = i + 1
            
            # Falls wenig Text, OCR versuchen
            if len(text.strip()) < 50 and OCR_AVAILABLE:
                text = self._ocr_seite(page_num)
                self.ocr_verwendet = True
            
            # Prüfe ob neue Dokumentgrenze
            doc_type, kategorie = self._klassifiziere_seite(text)
            
            if doc_type:
                if current_doc:
                    current_doc.seite_bis = page_num - 1
                    if current_doc.seite_bis >= current_doc.seite_von:
                        dokumente.append(current_doc)
                
                doc_id += 1
                current_doc = Dokument(
                    id=doc_id,
                    titel=self._extrahiere_titel(text, doc_type),
                    kategorie=kategorie,
                    seite_von=page_num,
                    seite_bis=page_num,
                    datum=self._extrahiere_datum(text),
                    inhalt_vorschau=text[:500] if text else "",
                    konfidenz=self._berechne_konfidenz(text, doc_type)
                )
            elif current_doc:
                current_doc.seite_bis = page_num
        
        if current_doc:
            current_doc.seite_bis = self.total_pages
            dokumente.append(current_doc)
        
        self.dokumente = dokumente
    
    def _klassifiziere_seite(self, text: str) -> Tuple[Optional[str], Optional[str]]:
        """Klassifiziert eine Seite anhand ihres Inhalts."""
        for pattern, doc_type, kategorie in self.DOKUMENT_MUSTER:
            if re.search(pattern, text, re.IGNORECASE | re.MULTILINE):
                return doc_type, kategorie
        return None, None
    
    def _extrahiere_titel(self, text: str, doc_type: str) -> str:
        """Extrahiert einen aussagekräftigen Titel."""
        # Betreff-Zeile
        betreff_match = re.search(r"(?:Betreff:|AW:|RE:)\s*([^\n]+)", text)
        if betreff_match:
            return betreff_match.group(1).strip()[:100]
        
        # Datum hinzufügen
        datum = self._extrahiere_datum(text)
        if datum:
            return f"{doc_type} vom {datum}"
        
        return doc_type
    
    def _extrahiere_datum(self, text: str) -> Optional[str]:
        """Extrahiert das Datum aus dem Text."""
        patterns = [
            r"(\d{2}\.\d{2}\.\d{4})",
            r"(\d{1,2}\.\s*(?:Januar|Februar|März|April|Mai|Juni|Juli|August|September|Oktober|November|Dezember)\s*\d{4})",
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        return None
    
    def _berechne_konfidenz(self, text: str, doc_type: str) -> float:
        """Berechnet Konfidenzwert für die Klassifizierung."""
        score = 0.5
        
        # Mehr Übereinstimmungen = höhere Konfidenz
        matches = sum(1 for p, _, _ in self.DOKUMENT_MUSTER 
                     if re.search(p, text, re.IGNORECASE))
        score += min(matches * 0.1, 0.3)
        
        # Textlänge
        if len(text) > 500:
            score += 0.1
        if len(text) > 1000:
            score += 0.1
            
        return min(score, 1.0)
    
    def _ocr_seite(self, page_num: int) -> str:
        """Führt OCR auf einer Seite durch."""
        if not OCR_AVAILABLE or not self.pdf_path:
            return ""
            
        try:
            images = convert_from_path(self.pdf_path, first_page=page_num, last_page=page_num)
            if images:
                text = pytesseract.image_to_string(images[0], lang='deu')
                return text
        except Exception as e:
            print(f"OCR-Fehler Seite {page_num}: {e}")
        return ""
    
    def _bewerte_qualitaet(self) -> int:
        """Bewertet die Qualität des Imports (0-100)."""
        score = 0
        
        if self.aktenvorblatt:
            if self.aktenvorblatt.rubrum:
                score += 15
            if self.aktenvorblatt.aktennummer:
                score += 15
            if self.aktenvorblatt.gegenstandswert > 0:
                score += 10
            if len(self.aktenvorblatt.parteien) >= 2:
                score += 20
        
        if self.dokumente:
            score += min(len(self.dokumente) * 5, 30)
            
            # Konfidenz der Dokumente
            avg_konfidenz = sum(d.konfidenz for d in self.dokumente) / len(self.dokumente)
            score += int(avg_konfidenz * 10)
        
        return min(score, 100)
    
    def _qualitaet_text(self, score: int) -> str:
        """Konvertiert Score in Textbewertung."""
        if score >= 80:
            return "sehr_gut"
        elif score >= 60:
            return "gut"
        elif score >= 40:
            return "akzeptabel"
        else:
            return "mangelhaft"
    
    def extrahiere_dokumente(self, nur_kategorien: List[str] = None) -> List[str]:
        """Extrahiert die erkannten Dokumente als separate PDF-Dateien."""
        if not PDF_AVAILABLE or not self.pdf_path:
            return []
            
        if not self.dokumente:
            self.analysiere_pdf()
        
        os.makedirs(self.output_dir, exist_ok=True)
        reader = PdfReader(self.pdf_path)
        erstellte_dateien = []
        
        for doc in self.dokumente:
            if nur_kategorien and doc.kategorie not in nur_kategorien:
                continue
            
            safe_title = re.sub(r'[<>:"/\\|?*]', '_', doc.titel)[:80]
            filename = f"{doc.id:03d}_{doc.kategorie}_{safe_title}.pdf"
            filepath = os.path.join(self.output_dir, filename)
            
            writer = PdfWriter()
            for page_num in range(doc.seite_von - 1, doc.seite_bis):
                if page_num < len(reader.pages):
                    writer.add_page(reader.pages[page_num])
            
            with open(filepath, "wb") as output:
                writer.write(output)
            
            doc.dateiname = filename
            erstellte_dateien.append(filepath)
        
        return erstellte_dateien
    
    def exportiere_metadaten(self, format: str = "json") -> str:
        """Exportiert die extrahierten Metadaten als JSON."""
        os.makedirs(self.output_dir, exist_ok=True)
        
        filepath = os.path.join(self.output_dir, "akten_metadaten.json")
        data = {
            "import_datum": datetime.now().isoformat(),
            "quelldatei": os.path.basename(self.pdf_path) if self.pdf_path else "upload",
            "aktenvorblatt": asdict(self.aktenvorblatt) if self.aktenvorblatt else None,
            "dokumente": [asdict(d) for d in self.dokumente],
            "ocr_verwendet": self.ocr_verwendet,
            "qualitaet_score": self._bewerte_qualitaet()
        }
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return filepath
    
    def fuer_juraconnect(self) -> Dict:
        """Bereitet die Daten für den Import in JuraConnect auf."""
        if not self.aktenvorblatt:
            return {}
        
        av = self.aktenvorblatt
        mandant = next((p for p in av.parteien if p.rolle == "Auftraggeber"), None)
        gegner = next((p for p in av.parteien if p.rolle == "Gegner"), None)
        
        return {
            "akte": {
                "aktenzeichen": av.aktennummer,
                "rubrum": av.rubrum,
                "wegen": av.wegen,
                "streitwert": av.gegenstandswert,
                "status": "aktiv",
                "angelegt_am": av.angelegt_am,
                "gericht": av.instanz_1_gericht,
                "gericht_az": av.instanz_1_az,
                "rechtsgebiet": av.rechtsgebiet,
            },
            "mandant": {
                "name": mandant.name if mandant else "",
                "anschrift": mandant.anschrift if mandant else "",
                "plz_ort": mandant.plz_ort if mandant else "",
                "telefon": mandant.telefon1 if mandant else "",
                "email": mandant.email if mandant else "",
            } if mandant else None,
            "gegner": {
                "name": gegner.name if gegner else "",
                "anschrift": gegner.anschrift if gegner else "",
                "plz_ort": gegner.plz_ort if gegner else "",
                "telefon": gegner.telefon1 if gegner else "",
                "email": gegner.email if gegner else "",
            } if gegner else None,
            "dokumente": [
                {
                    "titel": doc.titel,
                    "kategorie": doc.kategorie,
                    "datum": doc.datum,
                    "dateiname": doc.dateiname,
                    "seiten": f"{doc.seite_von}-{doc.seite_bis}"
                }
                for doc in self.dokumente
            ]
        }


class BatchImporter:
    """Importiert mehrere Akten gleichzeitig."""
    
    def __init__(self, output_base_dir: str = None):
        self.output_base_dir = output_base_dir or tempfile.mkdtemp()
        self.ergebnisse: List[Dict] = []
        
    def importiere_batch(self, pdf_dateien: List[str], 
                         progress_callback=None) -> List[ImportErgebnis]:
        """
        Importiert mehrere PDF-Dateien.
        
        Args:
            pdf_dateien: Liste der PDF-Pfade
            progress_callback: Optionaler Callback für Fortschritt
            
        Returns:
            Liste der Import-Ergebnisse
        """
        ergebnisse = []
        total = len(pdf_dateien)
        
        for i, pdf_path in enumerate(pdf_dateien):
            if progress_callback:
                progress_callback(i + 1, total, os.path.basename(pdf_path))
            
            try:
                output_dir = os.path.join(
                    self.output_base_dir, 
                    Path(pdf_path).stem
                )
                
                importer = RAMicroAktenImporter(pdf_path, output_dir)
                ergebnis = importer.analysiere_pdf()
                ergebnis_dict = {
                    "datei": pdf_path,
                    "ergebnis": ergebnis,
                    "importer": importer
                }
                ergebnisse.append(ergebnis)
                self.ergebnisse.append(ergebnis_dict)
                
            except Exception as e:
                ergebnisse.append(ImportErgebnis(
                    erfolg=False,
                    fehler=[f"Fehler bei {pdf_path}: {str(e)}"]
                ))
        
        return ergebnisse
    
    def statistiken(self) -> Dict:
        """Gibt Statistiken über den Batch-Import zurück."""
        erfolgreich = sum(1 for e in self.ergebnisse if e.get("ergebnis", {}).erfolg)
        gesamt_dokumente = sum(
            len(e.get("ergebnis", {}).dokumente or []) 
            for e in self.ergebnisse
        )
        
        return {
            "gesamt": len(self.ergebnisse),
            "erfolgreich": erfolgreich,
            "fehlgeschlagen": len(self.ergebnisse) - erfolgreich,
            "dokumente_gesamt": gesamt_dokumente,
            "durchschnitt_qualitaet": sum(
                e.get("ergebnis", {}).qualitaet_score or 0 
                for e in self.ergebnisse
            ) / max(len(self.ergebnisse), 1)
        }
