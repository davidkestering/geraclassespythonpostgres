import psycopg2
from psycopg2 import sql
import psycopg2.extras

class Conexao:
    def __init__(self, sServidor='BANCO'):
        self.pConexao = None
        self.pConsulta = None
        self.sErro = None
        self.sSqlError = None
        self.nQtdTabelas = None
        self.nQtdCampos = None
        self.sServidor = sServidor
        self.setServidor(sServidor)
        if sServidor == 'LOCAL':
            self.conectaBD('localhost', 'postgres', 'tudobem', 'painelpadrao')
        elif sServidor == 'BANCO':
            self.conectaBD('localhost', '', '', '')
        else:
            raise Exception(f'Não foi possível conectar ao servidor: {sServidor}')

    def setServidor(self, sServidor):
        self.sServidor = sServidor

    def getServidor(self):
        return self.sServidor

    def conectaBD(self, sHost, sUser, sSenha, sBanco):
        try:
            self.pConexao = psycopg2.connect(
                host=sHost,
                user=sUser,
                password=sSenha,
                dbname=sBanco
            )
        except psycopg2.Error as e:
            self.sSqlError = str(e)
            self.sErro = f'Erro ao conectar ao banco de dados: {self.sSqlError}'
            raise Exception(self.sErro)

    # def execute(self, sSql):
    #     try:
    #         self.pConsulta = self.pConexao.cursor()
    #         self.pConsulta.execute(sSql)
    #         print(sSql)
    #     except psycopg2.Error as e:
    #         self.sSqlError = str(e)
    #         self.sErro = f'Ocorreu o seguinte erro na consulta: {self.sSqlError} <br> Query: {sSql}'
    #         self.insereErroSql(sSql)
    #         return self.getErro()
    
    def execute(self, sSql):
        try:
            self.pConsulta = self.pConexao.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            self.pConsulta.execute(sSql)
            #print(sSql)
        except psycopg2.Error as e:
            self.sSqlError = str(e)
            self.sErro = f'Ocorreu o seguinte erro na consulta: {self.sSqlError} <br> Query: {sSql}'
            self.insereErroSql(sSql)
            return self.getErro()


    def insereErroSql(self, sSql):
        try:
            with self.pConexao.cursor() as cursor:
                sSqlErroExecucao = sql.SQL("INSERT INTO seg_erros_mysql (erro, ip, publicado) VALUES (%s, %s, 1)")
                cursor.execute(sSqlErroExecucao, (self.escapeString(self.getErro()), 'IP_SERVIDOR'))
                self.pConexao.commit()
        except psycopg2.Error as e:
            self.sSqlError = str(e)
            self.sErro = f'Ocorreu o seguinte erro na inserção do erro na tabela seg_erros_mysql: {self.sSqlError} <br> Query: {sSql}'

    def fetchObject(self):
        return self.pConsulta.fetchone()

    def close(self):
        self.pConexao.close()

    def getErroSql(self):
        return self.sSqlError

    def setConexao(self, sBanco):
        self.pConexao = Conexao(sServidor=sBanco)

    def getConexao(self):
        return self.pConexao

    def getConsulta(self):
        return self.pConsulta

    def getErro(self):
        return self.sErro

    def escapeString(self, sAtributo):
        return sAtributo.replace("'", "''")

    def unescapeString(self, sEscapedString):
        sEscapedString = sEscapedString.replace("'", "")
        sEscapedString = sEscapedString.replace("\"", "")
        return sEscapedString

    def getLastId(self):
        return self.pConsulta.lastrowid

    def setQtdTabelas(self, nQtdTabelas):
        self.nQtdTabelas = nQtdTabelas

    def getQtdTabelas(self):
        return self.nQtdTabelas

    def setQtdCampos(self, nQtdCampos):
        self.nQtdCampos = nQtdCampos

    def getQtdCampos(self):
        return self.nQtdCampos

    def carregaQtdTabelas(self, sSchema='public'):
        sSql = f"SELECT count(0) as qtd FROM information_schema.tables where table_schema = '{sSchema}'"
        self.execute(sSql)
        oReg = self.pConsulta.fetchone()
        #print(oReg)
        if oReg:
            self.setQtdTabelas(oReg['qtd'])
        return self.getQtdTabelas()

    # def pegaTabelas(self, sSchema='public'):
    #     sSql = f"SELECT * FROM information_schema.tables where table_schema = '{sSchema}'"
    #     self.execute(sSql)
    #     voObjeto = []
    #     while True:
    #         oReg = self.fetchObject()
    #         if not oReg:
    #             break
    #         voObjeto.append(oReg)
    #     return voObjeto
    
    def pegaTabelas(self, sSchema='public'):
        sSql = f"SELECT * FROM information_schema.tables WHERE table_schema = '{sSchema}'"
        self.execute(sSql)
        voObjeto = []
        while True:
            oReg = self.pConsulta.fetchone()  # Usa fetchone do RealDictCursor
            if not oReg:
                break
            voObjeto.append(oReg)
        return voObjeto


    def carregaQtdCampos(self, sNomeBanco, sNomeTabela, sSchema='public'):
        sSql = f"SELECT count(column_name) as qtd FROM information_schema.columns WHERE table_catalog = '{sNomeBanco}' AND table_schema = '{sSchema}' AND table_name = '{sNomeTabela}'"
        self.execute(sSql)
        oReg = self.fetchObject()
        if oReg:
            self.setQtdCampos(oReg['qtd'])
        return self.getQtdCampos()

    def pegaCampos(self, sNomeBanco, sNomeTabela, sSchema='public'):
        sSql = f"""
        SELECT T.table_catalog, T.table_schema, T.table_name, C.column_name, C.data_type, CCU.constraint_name, substr(CCU.constraint_name,length(CCU.constraint_name)-3) as PRI
        FROM information_schema.tables T
        JOIN information_schema.columns C
        ON C.table_catalog = T.table_catalog AND C.table_name = T.table_name AND C.table_schema = T.table_schema
        LEFT JOIN information_schema.constraint_column_usage CCU
        ON CCU.table_catalog = C.table_catalog AND CCU.table_name = C.table_name AND CCU.table_schema = C.table_schema AND CCU.column_name = C.column_name
        WHERE T.table_catalog = '{sNomeBanco}' AND T.table_schema = '{sSchema}' AND T.table_name = '{sNomeTabela}'
        ORDER BY C.ordinal_position
        """
        self.execute(sSql)
        voObjeto = []
        while True:
            oReg = self.fetchObject()
            if not oReg:
                break
            voObjeto.append(oReg)
        return voObjeto
