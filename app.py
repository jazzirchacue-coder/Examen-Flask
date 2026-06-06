from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "clave_secreta_2025"

DB_NAME = "database.db"


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def crear_bd():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS usuarios(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        password TEXT NOT NULL,
        nombre TEXT NOT NULL
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS productos(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo TEXT UNIQUE,
        nombre TEXT,
        descripcion TEXT,
        precio REAL,
        stock INTEGER,
        categoria TEXT
    )
    """)

    cur.execute("SELECT * FROM usuarios")
    usuarios = cur.fetchall()

    if len(usuarios) == 0:
        cur.execute("""
        INSERT INTO usuarios(username,password,nombre)
        VALUES('admin','1234','Administrador')
        """)

    cur.execute("SELECT * FROM productos")
    productos = cur.fetchall()

    if len(productos) == 0:
        datos = [
            ('P001', 'Laptop HP', 'Laptop Core i5', 2500, 10, 'Tecnologia'),
            ('P002', 'Mouse Logitech', 'Mouse Inalambrico', 80, 50, 'Accesorios'),
            ('P003', 'Teclado Redragon', 'Teclado Gamer', 150, 20, 'Accesorios')
        ]

        cur.executemany("""
        INSERT INTO productos
        (codigo,nombre,descripcion,precio,stock,categoria)
        VALUES(?,?,?,?,?,?)
        """, datos)

    conn.commit()
    conn.close()


@app.route("/")
def inicio():
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        usuario = request.form["usuario"]
        password = request.form["password"]

        conn = get_connection()

        user = conn.execute("""
        SELECT * FROM usuarios
        WHERE username=? AND password=?
        """, (usuario, password)).fetchone()

        conn.close()

        if user:
            session["usuario"] = user["nombre"]
            return redirect(url_for("principal"))

        return render_template(
            "login.html",
            error="Usuario o contraseña incorrectos"
        )

    return render_template("login.html")


@app.route("/principal")
def principal():

    if "usuario" not in session:
        return redirect(url_for("login"))

    return render_template(
        "principal.html",
        usuario=session["usuario"]
    )


@app.route("/buscador")
def buscador():

    if "usuario" not in session:
        return redirect(url_for("login"))

    return render_template("buscador.html")


@app.route("/api/buscar_producto", methods=["POST"])
def buscar_producto():

    data = request.get_json()
    codigo = data.get("codigo")

    conn = get_connection()

    producto = conn.execute("""
    SELECT * FROM productos
    WHERE codigo=?
    """, (codigo,)).fetchone()

    conn.close()

    if producto:
        return jsonify({
            "encontrado": True,
            "codigo": producto["codigo"],
            "nombre": producto["nombre"],
            "descripcion": producto["descripcion"],
            "precio": producto["precio"],
            "stock": producto["stock"],
            "categoria": producto["categoria"]
        })

    return jsonify({
        "encontrado": False
    })


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    crear_bd()
    app.run(debug=True)