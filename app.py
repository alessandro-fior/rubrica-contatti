from pathlib import Path
import sqlite3

from flask import Flask, abort, flash, g, redirect, render_template, request, url_for


BASE_DIR = Path(__file__).resolve().parent
DATABASE = BASE_DIR / "database.db"
SCHEMA = BASE_DIR / "schema.sql"

app = Flask(__name__)
app.config["SECRET_KEY"] = "dev-secret-key"


def get_db() -> sqlite3.Connection:
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exception: Exception | None) -> None:
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db() -> None:
    db = sqlite3.connect(DATABASE)
    with SCHEMA.open("r", encoding="utf-8") as schema_file:
        db.executescript(schema_file.read())
    db.close()


def ensure_db() -> None:
    if not DATABASE.exists():
        init_db()


def get_contact(contact_id: int) -> sqlite3.Row:
    contact = get_db().execute(
        """
        SELECT id, name, email, phone, note, created_at
        FROM contacts
        WHERE id = ?
        """,
        (contact_id,),
    ).fetchone()
    if contact is None:
        abort(404)
    return contact


@app.route("/")
def home():
    return redirect(url_for("list_contacts"))


@app.route("/contacts")
def list_contacts():
    ensure_db()
    contacts = get_db().execute(
        """
        SELECT id, name, email, phone, created_at
        FROM contacts
        ORDER BY id DESC
        """
    ).fetchall()
    return render_template("contacts/index.html", contacts=contacts)


@app.route("/contacts/new", methods=("GET", "POST"))
def create_contact():
    ensure_db()
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        note = request.form.get("note", "").strip()

        error = None
        if not name:
            error = "Il nome e obbligatorio."
        elif not email:
            error = "L'email e obbligatoria."
        elif "@" not in email:
            error = "Inserisci un indirizzo email valido."

        if error is not None:
            flash(error, "error")
        else:
            db = get_db()
            db.execute(
                """
                INSERT INTO contacts (name, email, phone, note)
                VALUES (?, ?, ?, ?)
                """,
                (name, email, phone, note),
            )
            db.commit()
            flash("Contatto creato con successo.", "success")
            return redirect(url_for("list_contacts"))

    return render_template(
        "contacts/form.html",
        contact=None,
        page_title="Nuovo contatto",
        submit_label="Crea contatto",
    )


@app.route("/contacts/<int:contact_id>")
def show_contact(contact_id: int):
    ensure_db()
    contact = get_contact(contact_id)
    return render_template("contacts/show.html", contact=contact)


@app.route("/contacts/<int:contact_id>/edit", methods=("GET", "POST"))
def edit_contact(contact_id: int):
    ensure_db()
    contact = get_contact(contact_id)

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        note = request.form.get("note", "").strip()

        error = None
        if not name:
            error = "Il nome e obbligatorio."
        elif not email:
            error = "L'email e obbligatoria."
        elif "@" not in email:
            error = "Inserisci un indirizzo email valido."

        if error is not None:
            flash(error, "error")
        else:
            db = get_db()
            db.execute(
                """
                UPDATE contacts
                SET name = ?, email = ?, phone = ?, note = ?
                WHERE id = ?
                """,
                (name, email, phone, note, contact_id),
            )
            db.commit()
            flash("Contatto aggiornato con successo.", "success")
            return redirect(url_for("show_contact", contact_id=contact_id))

    return render_template(
        "contacts/form.html",
        contact=contact,
        page_title="Modifica contatto",
        submit_label="Salva modifiche",
    )


@app.route("/contacts/<int:contact_id>/delete", methods=("POST",))
def delete_contact(contact_id: int):
    ensure_db()
    get_contact(contact_id)
    db = get_db()
    db.execute("DELETE FROM contacts WHERE id = ?", (contact_id,))
    db.commit()
    flash("Contatto eliminato con successo.", "success")
    return redirect(url_for("list_contacts"))


@app.errorhandler(404)
def not_found(error):
    return render_template("404.html"), 404


with app.app_context():
    ensure_db()


if __name__ == "__main__":
    app.run(debug=True)
