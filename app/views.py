import psycopg2, psycopg2.extras

from flask import g, session, request, redirect, url_for, render_template

from app import app

from random import randint

from datetime import datetime

@app.before_request
def before_request():
   g.db = psycopg2.connect("dbname=votacao user=postgres password=sousa123")

# Disconnect database 
@app.teardown_request
def teardown_request(exception):
    g.db.close()

@app.route('/', methods = ['POST', 'GET'])
def index():
	if 'name' in session:
		cur = g.db.cursor(cursor_factory=psycopg2.extras.DictCursor)
		cur.execute("SELECT * FROM usuario WHERE usuario = '{}'".format(session['name']))
		usuario = cur.fetchall()
		cur.execute("SELECT * FROM lei ORDER BY data_inicio DESC LIMIT 10 ")
		leis = cur.fetchall()
		cur.close()
		return render_template('index.html', usuario = usuario, leis = leis)
	return render_template('index.html', erro = 'Senha incorreta')

@app.route('/login', methods = ['GET', 'POST'])
def login():
	if request.method == 'GET':
		if 'name' in session:
			return redirect(url_for('index'))
		else:
			return render_template('usuario/login.html')
	else:
		nome_usuario = request.form['id_username']
		senha = request.form['id_password']
		cur = g.db.cursor(cursor_factory=psycopg2.extras.DictCursor)
		cur.execute("SELECT * FROM usuario WHERE usuario = '{}'".format(nome_usuario))
		usuario = cur.fetchall()
		cur.close()
		print (usuario)
		if len(usuario) != 0:
			if usuario[0][4] == nome_usuario and usuario[0][3] == senha:
				session['name'] = usuario[0][4]
				return redirect(url_for('index'))
			else:
				return render_template('usuario/login.html', error='Usuário ou senha incorreta!')
		return render_template('usuario/login.html', error='Usuário não encontrado!')

@app.route('/cadastro', methods = ['GET', 'POST'])
def cadastro():
	if request.method == 'GET':
		if 'name' in session:
			return redirect(url_for('index'))
		else:
			return render_template('usuario/cadastro.html')
	else:
		nome = request.form['id_nome']
		nome_usuario = request.form['id_usuario']
		email = request.form['id_email']
		senha = request.form['id_password']
		cur = g.db.cursor(cursor_factory=psycopg2.extras.DictCursor)
		cur.execute("SELECT * FROM usuario WHERE usuario = '{}'".format(nome_usuario))
		usuario = cur.fetchall()
		if len(usuario) == 1:
			return render_template('usuario/cadastro.html', error='Nome de usuário indisponível!')
		else:
			cur.execute("INSERT INTO usuario (nome, email, senha, usuario) VALUES ('{}', '{}', '{}', '{}')".format(nome, email, senha, nome_usuario))
			g.db.commit()
			cur.close()
			return redirect(url_for('login'))

@app.route('/logout')
def sair():
	session.pop('name')
	return redirect(url_for('index'))

@app.route('/perfil')
def perfil():
	if 'name' in session:
		cur = g.db.cursor(cursor_factory=psycopg2.extras.DictCursor)
		cur.execute("SELECT * FROM usuario WHERE usuario = '{}'".format(session['name']))
		usuario = cur.fetchall()
		cur.execute("SELECT * FROM lei WHERE id_usuario = {}".format(usuario[0][0]))
		leis = cur.fetchall()
		return render_template('usuario/perfil.html', usuario = usuario, leis = leis)
	return redirect(url_for('login'))

@app.route('/criar-lei', methods = ['GET', 'POST'])
def add_lei():
	if 'name' in session:
		if request.method == 'POST':
			data_inicio = datetime.now() 
			titulo = request.form['id_titulo']
			descricao = request.form['id_descricao']
			cur = g.db.cursor(cursor_factory=psycopg2.extras.DictCursor)
			cur.execute("SELECT * FROM usuario WHERE usuario = '{}'".format(session['name']))
			usuario = cur.fetchone()
			cur.execute("INSERT INTO lei (id_usuario, titulo, descricao, data_inicio) VALUES ({}, '{}', '{}', '{}')".format(usuario[0], titulo, descricao, data_inicio))
			g.db.commit()
			cur.close()
			return redirect(url_for('perfil'))
		return render_template('leis/adicionar.html')
	return redirect(url_for('login'))

@app.route('/minhas-leis')
def minhas_leis():
	if 'name' in session:
		cur = g.db.cursor(cursor_factory=psycopg2.extras.DictCursor)
		cur.execute("SELECT * FROM usuario WHERE usuario = '{}'".format(session['name']))
		usuario = cur.fetchone()
		cur.execute("SELECT * FROM lei WHERE id_usuario = '{}'".format(usuario[0]))
		leis = cur.fetchall()
		cur.close()
		return render_template('leis/minhas-leis.html', leis = leis)
	return redirect(url_for('login'))

@app.route('/lei/<int:identificador>', methods = ['GET', 'POST'])
def lei(identificador):
	cur = g.db.cursor(cursor_factory=psycopg2.extras.DictCursor)
	cur.execute("SELECT * FROM lei where id_lei = {}".format(identificador))
	lei = cur.fetchall()
	cur.execute("SELECT * FROM usuario WHERE usuario = '{}'".format(session['name']))
	usuario = cur.fetchall()
	cur.execute("SELECT * FROM comentario WHERE id_lei = {}".format(identificador))
	comentarios = cur.fetchall()
	cur.execute("SELECT * FROM usuario")
	usuarios = cur.fetchall()
	if request.method == 'GET':
		return render_template('leis/votar.html', lei = lei, usuario = usuario, comentarios = comentarios, usuarios = usuarios)
	else:
		if 'name' in session:
			form = request.form['value']
			if form == '1':
				if lei[0][4] == None:
					cur.execute("UPDATE lei SET votos_favor = {}".format(1))
				else:
					cur.execute("UPDATE lei SET votos_favor = {}".format(int(lei[0][4]) + 1))
			else:
				if lei[0][5] == None:
					cur.execute("UPDATE lei SET votos_contra = {}".format(1))
				else:
					cur.execute("UPDATE lei SET votos_contra = {}".format(int(lei[0][5]) + 1))
			g.db.commit()
			cur.close()
			return redirect(url_for('lei', identificador = lei[0][0]))
		return redirect(url_for('login'))

@app.route('/leis-em-votacao')
def leis_votacao():
	cur = g.db.cursor(cursor_factory=psycopg2.extras.DictCursor)
	cur.execute("SELECT * FROM lei")
	leis = cur.fetchall()
	cur.execute("SELECT * FROM usuario WHERE usuario = '{}'".format(session['name']))
	usuario = cur.fetchall()
	return render_template('leis/minhas-leis.html', leis = leis, usuario = usuario)

@app.route('/comentar/<int:identificador>', methods=['GET', 'POST'])
def comentar(identificador):
	if request.method == 'POST':
		cur = g.db.cursor(cursor_factory=psycopg2.extras.DictCursor)
		cur.execute("SELECT * FROM lei where id_lei = {}".format(identificador))
		lei = cur.fetchall()
		cur.execute("SELECT * FROM usuario WHERE usuario = '{}'".format(session['name']))
		usuario = cur.fetchall()
		comentario = request.form['id_comentario']
		cur.execute("INSERT INTO comentario (id_usuario, id_lei, comentario) VALUES ({}, {}, '{}')".format(usuario[0][0], lei[0][0], comentario))
		g.db.commit()
		cur.close()
		return redirect(url_for('lei', identificador = lei[0][0]))
	return redirect(url_for('lei', identificador = identificador))


			