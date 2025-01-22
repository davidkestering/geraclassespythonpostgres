from flask import Flask, request, render_template

app = Flask(__name__, template_folder='templates')

@app.route('/')
def index():
    return render_template('index/index.html')

@app.route('/listar_tabelas', methods=["GET", "POST"])
def listar_tabelas():
    # Itera sobre a propriedade args -GET
    # for key, value in request.args.items():
    #     print(f"{key}: {value}")

    # Itera sobre a propriedade form - POST
    # for key, value in request.form.items():
    #     print(f"{key}: {value}")

    #print(request.form["fHost"])

    import constantes as ct
    from classes.Conexao import Conexao
    oConexao = Conexao(ct.BANCO)
    sSchema = request.form['fSchema']
    nQtdTabelas = oConexao.carregaQtdTabelas(sSchema)
    sNomeBanco = request.form['fNome']
    voTabelas = oConexao.pegaTabelas(sSchema)
    #print(voTabelas)
    return render_template('listar_tabelas/lista_tabelas.html', nQtdTabelas = nQtdTabelas, sNomeBanco = sNomeBanco, sSchema = sSchema, voTabelas = voTabelas)

@app.route('/processa', methods=["GET", "POST"])
def processa():
    import constantes as ct
    from classes.Conexao import Conexao
    from classes.Construtor import Construtor
    from classes.GeradoraBasica import GeradoraBasica
    from classes.GeradoraBD import GeradoraBD
    from classes.GeradoraInteriorFachada import GeradoraInteriorFachada
    from classes.GeradoraFachada import GeradoraFachada
    oConexao = Conexao(ct.BANCO)
    #Itera sobre a propriedade form - POST
    # for key, value in request.form.items():
    #     print(f"{key}: {value}")
    sNomeBanco = request.form['fNomeBanco']
    sSchema = request.form['fSchema']
    tabelas_selecionadas = request.form.getlist("fTabelas")
    # for value in tabelas_selecionadas:
    #     print(f"{value}")
    vNomeClasses = []
    vsFachada = []
    for tabela in tabelas_selecionadas:
        nQtdCampos = oConexao.carregaQtdCampos(sNomeBanco,tabela,sSchema)
        #print("Para a tabela ",tabela," existem ",nQtdCampos," campos")
        voCampos = oConexao.pegaCampos(sNomeBanco,tabela,sSchema)
        oConstrutor = Construtor(sNomeBanco,tabela,sSchema)
        oGeradoraBasica = GeradoraBasica(oConstrutor)
        oGeradoraBasica.gera()
        oGeradoraBD = GeradoraBD(oConstrutor)
        oGeradoraBD.gera()
        vNomeClasses.append(oConstrutor.sClasse)
        oGeradoraInteriorFachada = GeradoraInteriorFachada(oConstrutor)
        oGeradoraInteriorFachada.gera()
        vsFachada.append(oGeradoraInteriorFachada.sInteriorFachada)

    #print(vsFachada)
    oGeradoraFachada = GeradoraFachada(sNomeBanco, vsFachada, vNomeClasses)
    oGeradoraFachada.gera()

    return 'OK'

if __name__ == '__main__':
    app.run(debug=True)