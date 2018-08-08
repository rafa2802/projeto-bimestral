CREATE DATABASE VOTACAO;

CREATE TABLE USUARIO(
	id_usuario serial,
	nome varchar(255),
	email varchar(255),
	senha varchar(11),
	usuario varchar(30),
	primary key (id_usuario)
);

CREATE TABLE LEI(
	id_lei serial,
	id_usuario integer,
	titulo varchar(50),
	descricao text,
	votos_favor integer,
	votos_contra integer,
	data_inicio time,
	data_fim time,
	primary key(id_lei),
	foreign key(id_usuario) references USUARIO (id_usuario)
);

CREATE TABLE COMENTARIO(
	id_comentario serial,
	id_usuario integer,
	id_lei integer,
	comentario text,
	primary key (id_comentario),
	foreign key(id_usuario) references USUARIO (id_usuario),
	foreign key(id_lei) references LEI (id_lei)
);
