# Flask CRUD con SQLite

Piccolo progetto Python con Flask e CRUD completo su database SQLite.

## Funzionalita

- lista contatti
- creazione di un nuovo contatto
- visualizzazione dettaglio
- modifica di un contatto esistente
- eliminazione
- inizializzazione automatica del database al primo avvio

## Requisiti

- Python 3.10 o superiore

## Avvio

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

Poi apri nel browser:

```text
http://127.0.0.1:5000
```

## Struttura

```text
.
|-- app.py
|-- database.db
|-- README.md
|-- requirements.txt
|-- schema.sql
|-- static/
|   `-- style.css
`-- templates/
    |-- 404.html
    |-- base.html
    `-- contacts/
        |-- form.html
        |-- index.html
        `-- show.html
```
