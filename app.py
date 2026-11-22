
import sqlite3
from pathlib import Path

from flask import Flask, render_template, request, redirect, url_for, abort

app = Flask(__name__)
DB_PATH = Path(__file__).with_name("notes.db")


def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL
            )
        """)


def get_note(note_id):
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row

        note = conn.execute(
            "SELECT * FROM notes WHERE id = ?",
            (note_id,)
        ).fetchone()

    if note is None:
        abort(404)

    return note


@app.route("/")
def index():
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row

        notes = conn.execute(
            "SELECT * FROM notes ORDER BY id DESC"
        ).fetchall()

    return render_template("index.html", notes=notes)


@app.route("/create", methods=["GET", "POST"])
def create():
    if request.method == "POST":
        title = request.form["title"].strip()
        content = request.form["content"].strip()

        if not title:
            return "Название не может быть пустым", 400

        with sqlite3.connect(DB_PATH) as conn:
            conn.execute(
                "INSERT INTO notes (title, content) VALUES (?, ?)",
                (title, content)
            )

        return redirect(url_for("index"))

    return render_template("create.html")


@app.route("/edit/<int:note_id>", methods=["GET", "POST"])
def edit(note_id):
    note = get_note(note_id)

    if request.method == "POST":
        title = request.form["title"].strip()
        content = request.form["content"].strip()

        if not title:
            return "Название не может быть пустым", 400

        with sqlite3.connect(DB_PATH) as conn:
            conn.execute(
                "UPDATE notes SET title = ?, content = ? WHERE id = ?",
                (title, content, note_id)
            )

        return redirect(url_for("index"))

    return render_template("edit.html", note=note)


@app.route("/delete/<int:note_id>", methods=["POST"])
def delete(note_id):
    get_note(note_id)

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "DELETE FROM notes WHERE id = ?",
            (note_id,)
        )

    return redirect(url_for("index"))


init_db()

if __name__ == "__main__":
    app.run(debug=True)
