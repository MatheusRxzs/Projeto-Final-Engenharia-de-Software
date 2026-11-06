"""Achados e Perdidos UNIMA - back end (Flask + SQLite)."""
import os
import sqlite3
from datetime import date
from functools import wraps

from flask import Flask, g, jsonify, request, session
from werkzeug.security import check_password_hash, generate_password_hash

BASE = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, static_folder=os.path.join(BASE, "static"), static_url_path="")
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "troque-esta-chave-em-producao")
app.config["DATABASE"] = os.path.join(BASE, "achados.db")

TIPOS = ("perdido", "achado")
CAMPOS_ITEM = ("tipo", "titulo", "descricao", "categoria", "local", "data", "contato_email", "contato_telefone")
CATEGORIAS = ("Documentos", "Eletrônicos", "Material escolar", "Roupas e acessórios", "Chaves", "Outros")

SCHEMA = """
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    senha_hash TEXT NOT NULL,
    criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS itens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo TEXT NOT NULL CHECK (tipo IN ('perdido','achado')),
    titulo TEXT NOT NULL,
    descricao TEXT NOT NULL DEFAULT '',
    categoria TEXT NOT NULL,
    local TEXT NOT NULL,
    data TEXT NOT NULL,
    contato_email TEXT NOT NULL DEFAULT '',
    contato_telefone TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL DEFAULT 'aberto' CHECK (status IN ('aberto','devolvido')),
    usuario_id INTEGER NOT NULL REFERENCES usuarios(id),
    criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""


def db():
    if "db" not in g:
        g.db = sqlite3.connect(app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


@app.teardown_appcontext
def close_db(_exc):
    conn = g.pop("db", None)
    if conn is not None:
        conn.close()


def init_db():
    conn = sqlite3.connect(app.config["DATABASE"])
    conn.executescript(SCHEMA)
    cols = {r[1] for r in conn.execute("PRAGMA table_info(itens)")}
    for col in ("contato_email", "contato_telefone"):  # migração de bancos antigos
        if col not in cols:
            conn.execute(f"ALTER TABLE itens ADD COLUMN {col} TEXT NOT NULL DEFAULT ''")
    conn.commit()
    conn.close()


def erro(msg, code=400):
    return jsonify({"erro": msg}), code


def login_required(fn):
    @wraps(fn)
    def wrapper(*a, **kw):
        if "uid" not in session:
            return erro("Entre na sua conta para continuar.", 401)
        return fn(*a, **kw)
    return wrapper


def item_json(row, logado):
    d = dict(row)
    d["meu"] = session.get("uid") == d.pop("usuario_id")
    email = d.pop("contato_email") or d["autor_email"]
    tel = d.pop("contato_telefone")
    d.pop("autor_email")
    d["contato"] = {"email": email, "telefone": tel} if logado else None  # contato só para logados
    return d


QUERY = """SELECT i.*, u.nome AS autor, u.email AS autor_email
           FROM itens i JOIN usuarios u ON u.id = i.usuario_id"""


# ---------- Autenticação (RF01) ----------
@app.post("/api/register")
def register():
    d = request.get_json(silent=True) or {}
    nome, email, senha = (d.get("nome") or "").strip(), (d.get("email") or "").strip().lower(), d.get("senha") or ""
    if not nome or "@" not in email or len(senha) < 6:
        return erro("Informe nome, e-mail válido e senha com ao menos 6 caracteres.")
    try:
        cur = db().execute("INSERT INTO usuarios (nome,email,senha_hash) VALUES (?,?,?)",
                           (nome, email, generate_password_hash(senha)))
        db().commit()
    except sqlite3.IntegrityError:
        return erro("Este e-mail já está cadastrado.", 409)
    session["uid"], session["nome"] = cur.lastrowid, nome
    return jsonify({"nome": nome, "email": email}), 201


@app.post("/api/login")
def login():
    d = request.get_json(silent=True) or {}
    u = db().execute("SELECT * FROM usuarios WHERE email=?", ((d.get("email") or "").strip().lower(),)).fetchone()
    if not u or not check_password_hash(u["senha_hash"], d.get("senha") or ""):
        return erro("E-mail ou senha incorretos.", 401)
    session["uid"], session["nome"] = u["id"], u["nome"]
    return jsonify({"nome": u["nome"], "email": u["email"]})


@app.post("/api/logout")
def logout():
    session.clear()
    return jsonify({"ok": True})


@app.get("/api/me")
def me():
    if "uid" not in session:
        return jsonify(None)
    row = db().execute("SELECT email FROM usuarios WHERE id=?", (session["uid"],)).fetchone()
    return jsonify({"nome": session["nome"], "email": row["email"] if row else ""})


# ---------- Itens (RF02-RF05) ----------
def validar_item(d):
    campos = {k: (d.get(k) or "").strip() for k in
              ("tipo", "titulo", "descricao", "categoria", "local", "data", "contato_email", "contato_telefone")}
    if campos["tipo"] not in TIPOS:
        return None, "Tipo deve ser 'perdido' ou 'achado'."
    if not campos["titulo"] or not campos["local"]:
        return None, "Título e local são obrigatórios."
    if campos["categoria"] not in CATEGORIAS:
        return None, "Categoria inválida."
    campos["data"] = campos["data"] or date.today().isoformat()
    try:
        date.fromisoformat(campos["data"])
    except ValueError:
        return None, "Data inválida (use AAAA-MM-DD)."
    campos["contato_email"] = campos["contato_email"].lower()
    campos["contato_telefone"] = "".join(ch for ch in campos["contato_telefone"] if ch.isdigit())
    if not campos["contato_email"] and not campos["contato_telefone"]:
        return None, "Informe ao menos um contato: e-mail ou telefone."
    if campos["contato_email"] and "@" not in campos["contato_email"]:
        return None, "E-mail de contato inválido."
    if campos["contato_telefone"] and not 10 <= len(campos["contato_telefone"]) <= 13:
        return None, "Telefone inválido. Use DDD + número, ex.: (82) 99999-8888."
    return campos, None


@app.get("/api/categorias")
def categorias():
    return jsonify(CATEGORIAS)


@app.get("/api/itens")
def listar():
    sql, args = QUERY + " WHERE 1=1", []
    q = (request.args.get("q") or "").strip()
    if q:
        sql += " AND (i.titulo LIKE ? OR i.descricao LIKE ? OR i.local LIKE ?)"
        args += [f"%{q}%"] * 3
    for campo in ("tipo", "categoria", "status"):
        v = request.args.get(campo)
        if v:
            sql += f" AND i.{campo} = ?"
            args.append(v)
    if request.args.get("meus") and "uid" in session:
        sql += " AND i.usuario_id = ?"
        args.append(session["uid"])
    rows = db().execute(sql + " ORDER BY i.status ASC, i.data DESC, i.id DESC", args).fetchall()
    return jsonify([item_json(r, "uid" in session) for r in rows])


@app.post("/api/itens")
@login_required
def criar():
    campos, msg = validar_item(request.get_json(silent=True) or {})
    if msg:
        return erro(msg)
    cur = db().execute(
        "INSERT INTO itens (tipo,titulo,descricao,categoria,local,data,contato_email,contato_telefone,usuario_id)"
        " VALUES (?,?,?,?,?,?,?,?,?)",
        (*[campos[k] for k in CAMPOS_ITEM], session["uid"]))
    db().commit()
    row = db().execute(QUERY + " WHERE i.id=?", (cur.lastrowid,)).fetchone()
    return jsonify(item_json(row, True)), 201


def item_do_usuario(item_id):
    row = db().execute(QUERY + " WHERE i.id=?", (item_id,)).fetchone()
    if row is None:
        return None, erro("Item não encontrado.", 404)
    if row["usuario_id"] != session["uid"]:
        return None, erro("Você só pode alterar itens que cadastrou.", 403)
    return row, None


@app.put("/api/itens/<int:item_id>")
@login_required
def editar(item_id):
    _, e = item_do_usuario(item_id)
    if e:
        return e
    campos, msg = validar_item(request.get_json(silent=True) or {})
    if msg:
        return erro(msg)
    db().execute("UPDATE itens SET tipo=?,titulo=?,descricao=?,categoria=?,local=?,data=?,"
                 "contato_email=?,contato_telefone=? WHERE id=?",
                 (*[campos[k] for k in CAMPOS_ITEM], item_id))
    db().commit()
    return jsonify(item_json(db().execute(QUERY + " WHERE i.id=?", (item_id,)).fetchone(), True))


@app.post("/api/itens/<int:item_id>/devolver")
@login_required
def devolver(item_id):
    _, e = item_do_usuario(item_id)
    if e:
        return e
    db().execute("UPDATE itens SET status='devolvido' WHERE id=?", (item_id,))
    db().commit()
    return jsonify({"ok": True})


@app.delete("/api/itens/<int:item_id>")
@login_required
def excluir(item_id):
    _, e = item_do_usuario(item_id)
    if e:
        return e
    db().execute("DELETE FROM itens WHERE id=?", (item_id,))
    db().commit()
    return jsonify({"ok": True})


@app.get("/")
def index():
    return app.send_static_file("index.html")


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
