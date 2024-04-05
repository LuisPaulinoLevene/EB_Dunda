import sqlite3
from fastapi import FastAPI, Request, Form, HTTPException, Response
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()

# Configurando o Jinja2Templates para renderizar modelos HTML
templates = Jinja2Templates(directory="templates")


# Função para criar todas as tabelas necessárias
def create_tables():
    conn = sqlite3.connect("Maquina.db")
    cursor = conn.cursor()


    # Tabela 'usuarios'
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarioss (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    # Tabela 'acessoprof'
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS acessoprof (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    # Tabela 'acessodae'
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS acessodae (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    # Commit e fechar a conexão
    conn.commit()
    conn.close()

# Chamar a função para garantir que todas as tabelas sejam criadas
create_tables()


def validate_credentials(username: str, password: str) -> str:
    # Verificar se as credenciais estão na tabela admin
    conn = sqlite3.connect("Maquina.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM admins WHERE username = ? AND password = ?", (username, password))
    admin_user = cursor.fetchone()
    conn.close()

    if admin_user:
        return "admins"

    # Verificar se as credenciais estão na tabela usuarios
    conn = sqlite3.connect("Maquina.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarioss WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    conn.close()

    if user:
        return "usuarioss"

    # Verificar se as credenciais estão na tabela acessoprof
    conn = sqlite3.connect("Maquina.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM acessoprof WHERE username = ? AND password = ?", (username, password))
    professor_user = cursor.fetchone()
    conn.close()

    if professor_user:
        return "professor"

    # Verificar se as credenciais estão na tabela acessodae
    conn = sqlite3.connect("Maquina.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM acessodae WHERE username = ? AND password = ?", (username, password))
    dae_user = cursor.fetchone()
    conn.close()

    if dae_user:
        return "dae"

    # Se as credenciais não corresponderem a nenhuma tabela
    return "invalid"


# Usar a função validate_credentials() na função login()
@app.post("/login", response_class=HTMLResponse)
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    user_type = validate_credentials(username, password)

    if user_type == "usuarioss":
        # Credenciais válidas na tabela usuarios, redireciona para a página menu2.html
        return RedirectResponse("/menu2")
    elif user_type == "professor":
        # Credenciais válidas na tabela acessoprof, redireciona para a página professores.html
        return RedirectResponse("/professores")
    elif user_type == "dae":
        # Credenciais válidas na tabela acessodae, redireciona para a página dae.html
        return RedirectResponse("/dae")
    else:
        # Credenciais inválidas, exibe a mensagem na página menu.html
        return templates.TemplateResponse("menu.html", {"request": request, "mensagem": "Credenciais inválidas"})

    # Função para registrar o usuário "maquina" na tabela 'admin'



# Rota para a página utilizadores.html
@app.get("/utilizadores.html")
async def show_utilizadores(request: Request):
    return FileResponse("templates/utilizadores.html")

# Rota para a página inicial
@app.get("/", response_class=HTMLResponse)
async def read_home(request: Request, mensagem: str = None):
    return templates.TemplateResponse("menu.html", {"request": request, "mensagem": mensagem})

# Rota para processar o formulário de registro de usuário
@app.post("/registrar_usuario")
async def registrar_usuario(
    username: str = Form(...),
    password: str = Form(...)
):
    try:
        # Conectar ao banco de dados SQLite
        conn = sqlite3.connect("Maquina.db")
        cursor = conn.cursor()

        # Inserir os dados do usuário na tabela 'usuarioss'
        cursor.execute(
            "INSERT INTO usuarioss (username, password) VALUES (?, ?)",
            (username, password)
        )

        # Commit a transação
        conn.commit()

        # Fechar a conexão com o banco de dados
        conn.close()

        # Retornar uma mensagem de sucesso
        return {"message": "Usuário registrado com sucesso!"}

    except sqlite3.Error as e:
        # Em caso de erro, imprimir uma mensagem de erro
        print("Erro ao registrar usuário:", e)
        # Retornar uma mensagem de erro ao cliente
        return {"error": "Erro ao registrar usuário. Por favor, tente novamente."}


# Rota para exibir a tabela de usuários
@app.get("/lista_usuarios", response_class=HTMLResponse)
async def show_usuarios(request: Request):
    conn = sqlite3.connect("Maquina.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarioss")
    usuarios = cursor.fetchall()
    conn.close()
    return templates.TemplateResponse("usuarios.html", {"request": request, "usuarioss": usuarios})


# Função para obter todos os usuários
def get_all_users():
    conn = sqlite3.connect("Maquina.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarioss")
    users = cursor.fetchall()
    conn.close()
    return users


# Função para excluir um usuário pelo ID
def delete_user(user_id: int):
    conn = sqlite3.connect("Maquina.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM usuarioss WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()


# Rota para a página menu2.html
@app.get("/menu2", response_class=HTMLResponse)
async def show_menu2(request: Request):
    users = get_all_users()
    return templates.TemplateResponse("menu2.html", {"request": request, "usuarios": users})


# Rota para processar a exclusão de um usuário
@app.delete("/apagar_usuario/{user_id}")
async def delete_usuario(user_id: int):
    delete_user(user_id)
    return {"message": "Usuário excluído com sucesso"}

# Rota para a página registrar_professor.html
@app.get("/registrar_professor", response_class=HTMLResponse)
async def show_registrar_professor(request: Request):
    return templates.TemplateResponse("registrar_professor.html", {"request": request})

# Rota para processar o formulário na página registrar_professor.html
@app.post("/registrar_professor", response_class=HTMLResponse)
async def registrar_professor(request: Request, username: str = Form(...), password: str = Form(...)):
    # Conectar ao banco de dados SQLite
    conn = sqlite3.connect("Maquina.db")
    cursor = conn.cursor()


    # Inserir dados na tabela
    cursor.execute("INSERT INTO acessoprof (username, password) VALUES (?, ?)", (username, password))
    conn.commit()
    conn.close()

    # Exibir mensagem de sucesso na mesma página
    mensagem = "Professor registrado com sucesso!"
    return templates.TemplateResponse("professores.html", {"request": request, "mensagem": mensagem})

# Rota para a página professores.html
@app.get("/professores", response_class=HTMLResponse)
async def show_professores(request: Request):
    return templates.TemplateResponse("professores.html", {"request": request})

# Rota para a página registrar_dae.html
@app.get("/registrar_dae", response_class=HTMLResponse)
async def show_registrar_dae(request: Request):
    return templates.TemplateResponse("registrar_dae.html", {"request": request})

# Rota para processar o formulário na página registrar_dae.html
@app.post("/registrar_dae", response_class=HTMLResponse)
async def registrar_dae(request: Request, username: str = Form(...), password: str = Form(...)):
    # Conectar ao banco de dados SQLite
    conn = sqlite3.connect("Maquina.db")
    cursor = conn.cursor()


    # Inserir dados na tabela
    cursor.execute("INSERT INTO acessodae (username, password) VALUES (?, ?)", (username, password))
    conn.commit()
    conn.close()

    # Exibir mensagem de sucesso na mesma página
    mensagem = "DAE registrado com sucesso!"
    return templates.TemplateResponse("dae.html", {"request": request, "mensagem": mensagem})

# Rota para a página dae.html
@app.get("/dae", response_class=HTMLResponse)
async def show_dae(request: Request):
    return templates.TemplateResponse("dae.html", {"request": request, "mensagem": "Página do DAE"})


# Rota para a página professores1.html
@app.get("/dae1", response_class=HTMLResponse)
async def show_professores1(request: Request, ano: str):
    return templates.TemplateResponse("dae1.html", {"request": request, "ano": ano})



# Rota para renderizar a página turma.html
@app.get("/turma", response_class=HTMLResponse)
async def show_turma(request: Request, classe: str = None):
    return templates.TemplateResponse("turma.html", {"request": request, "classe": classe})


# Rota para a página turmas.html
@app.get("/1turmaA", response_class=HTMLResponse)
async def show_turmas(request: Request, classe: str = None, turma: str = None):
    return templates.TemplateResponse("1ªturmaA.html", {"request": request, "classe": classe, "turma": turma})

# Rota para a página turmas.html
@app.get("/1turmaB", response_class=HTMLResponse)
async def show_turmas(request: Request, classe: str = None, turma: str = None):
    return templates.TemplateResponse("1ªturmaB.html", {"request": request, "classe": classe, "turma": turma})

# Rota para a página ver_turma.html
@app.get("/ver_turma.html", response_class=HTMLResponse)
async def show_ver_turma(request: Request):
    return templates.TemplateResponse("ver_turma.html", {"request": request})

# Rota para a página de lista de turmas
@app.get("/lista_de_turma", response_class=HTMLResponse)
async def lista_de_turma(request: Request, classe: str, turma: str):
    try:
        # Conectar ao banco de dados SQLite
        conn = sqlite3.connect('Maquina.db')
        cursor = conn.cursor()

        # Consulta SQL para selecionar alunos com a classe e turma especificadas
        cursor.execute("SELECT * FROM cadastroaluno WHERE classe = ? AND turma = ?", (classe, turma))
        alunos = cursor.fetchall()

        # Fechar conexão com o banco de dados
        conn.close()

        # Construir a tabela HTML com os dados dos alunos da turma específica
        table_content = "<h2>Lista nominal da {} classe, Turma: {}</h2>".format(classe, turma)
        table_content += "<table border='1'><tr><th>Código</th><th>Número</th><th>Nome Completo</th><th>Sexo</th><th>Data de Nascimento</th><th>Local de Nascimento</th><th>Nome do Encarregado</th><th>Residência</th><th>Contato</th></tr>"
        for aluno in alunos:
            table_content += f"<tr><td>{aluno[0]}</td><td>{aluno[1]}</td><td>{aluno[2]}</td><td>{aluno[3]}</td><td>{aluno[4]}</td><td>{aluno[5]}</td><td>{aluno[6]}</td><td>{aluno[7]}</td><td>{aluno[8]}</td></tr>"
        table_content += "</table>"

        # Retornar a resposta HTML
        return HTMLResponse(content=table_content)

    except Exception as e:
        print("Erro ao buscar dados dos alunos:", e)
        raise HTTPException(status_code=500, detail="Erro ao buscar dados dos alunos. Por favor, tente novamente.")

# Rota para a página de ver todos os alunos
@app.get("/ver_todos_alunos.html", response_class=HTMLResponse)
async def ver_todos_alunos(request: Request):
    # Conectar ao banco de dados SQLite
    conn = sqlite3.connect('Maquina.db')
    cursor = conn.cursor()

    try:
        # Consulta SQL para selecionar todos os alunos
        cursor.execute("SELECT * FROM cadastroaluno")
        alunos = cursor.fetchall()

        # Fechar conexão com o banco de dados
        conn.close()

        # Construir a tabela HTML com os dados dos alunos
        table_content = "<h2>Lista de todos os alunos cadastrados na escola</h2>"
        table_content += "<table border='1'><tr><th>Código</th><th>Número</th><th>Nome Completo</th><th>Sexo</th><th>Data de Nascimento</th><th>Local de Nascimento</th><th>Nome do Encarregado</th><th>Residência</th><th>Contato</th><th>Classe</th><th>Turma</th></tr>"
        for aluno in alunos:
            table_content += f"<tr><td>{aluno[0]}</td><td>{aluno[1]}</td><td>{aluno[2]}</td><td>{aluno[3]}</td><td>{aluno[4]}</td><td>{aluno[5]}</td><td>{aluno[6]}</td><td>{aluno[7]}</td><td>{aluno[8]}</td><td>{aluno[9]}</td><td>{aluno[10]}</td></tr>"
        table_content += "</table>"

        # Retornar a resposta HTML
        return HTMLResponse(content=table_content)

    except sqlite3.Error as e:
        # Em caso de erro, imprima uma mensagem de erro
        print("Erro ao buscar todos os alunos:", e)
        # Retorne uma mensagem de erro ao cliente
        return {"error": "Erro ao buscar todos os alunos. Por favor, tente novamente."}


#===================================================================================================================

# Conectar ao banco de dados SQLite e criar a tabela 'cadastroaluno'
conn = sqlite3.connect('Maquina.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS cadastroaluno (
        codigo INTEGER PRIMARY KEY AUTOINCREMENT,
        numero INTEGER,
        nome_completo TEXT,
        sexo TEXT CHECK(sexo IN ('Masculino', 'Feminino')),
        data_nascimento TEXT,
        local_nascimento TEXT,
        nome_encarregado TEXT,
        residencia TEXT,
        contacto TEXT,
        classe TEXT,
        turma TEXT
    )
''')
conn.commit()

# Função para obter o próximo número de aluno para uma determinada turma
def obter_proximo_numero_turma(turma: str) -> int:
    cursor.execute("SELECT MAX(numero) FROM cadastroaluno WHERE turma = ?", (turma,))
    ultimo_numero = cursor.fetchone()[0]
    if ultimo_numero is None:
        return 1
    else:
        return ultimo_numero + 1

# Rota para processar o formulário e inserir os dados no banco de dados
@app.post("/inserir_aluno")
async def inserir_aluno(
        nome: str = Form(...),
        sexo: str = Form(...),
        data_nascimento: str = Form(...),
        local_nascimento: str = Form(...),
        nome_encarregado: str = Form(...),
        residencia: str = Form(...),
        contacto: str = Form(...),
        classe: str = Form(...),
        turma: str = Form(...),
):
    try:
        # Obter o próximo número de aluno para a turma especificada
        numero_aluno = obter_proximo_numero_turma(turma)

        # Inserir os dados do aluno na tabela
        cursor.execute(
            "INSERT INTO cadastroaluno (numero, nome_completo, sexo, data_nascimento, local_nascimento, nome_encarregado, residencia, contacto, classe, turma) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (numero_aluno, nome, sexo, data_nascimento, local_nascimento, nome_encarregado, residencia, contacto, classe, turma))

        # Commit a transação
        conn.commit()

        # Retornar uma mensagem de sucesso
        return {"message": "Dados do aluno inseridos com sucesso!"}

    except sqlite3.Error as e:
        # Em caso de erro, imprimir uma mensagem de erro
        print("Erro ao inserir dados do aluno:", e)
        # Retornar uma mensagem de erro ao cliente
        return {"error": "Erro ao inserir dados do aluno. Por favor, tente novamente."}
