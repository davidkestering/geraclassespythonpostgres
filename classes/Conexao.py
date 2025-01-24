import psycopg2
from psycopg2.extras import DictCursor
from psycopg2.extensions import AsIs
import constantes as ct

class Conexao:
    def __init__(self, sServidor='BANCO'):
        self.pConexao = None
        self.pConsulta = None
        self.pBanco = None
        self.sErro = None
        self.sSqlError = None
        self.nQtdTabelas = None
        self.nQtdCampos = None
        self.sServidor = sServidor
        self.setServidor(sServidor)
        if sServidor == 'LOCAL':
            self.conectaBD('localhost', 'postgres', 'tudobem', 'painelpadrao')
        elif sServidor == 'BANCO':
            self.conectaBD('localhost', 'postgres', 'tudobem', 'painelpadrao')
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
    #     self.pConsulta = self.pConexao.cursor(cursor_factory=DictCursor)
    #     try:
    #         self.pConsulta.execute(sSql)
    #         #self.pConsulta.commit()
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
            with self.pConexao.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                sSqlErroExecucao = f"INSERT INTO seg_erros_sql (erro,ip,publicado) VALUES ('{self.escapeString(self.getErro())}','{ct.IP_SERVIDOR}',1)"
                cursor.execute(sSqlErroExecucao)
                self.pConexao.commit()
        except psycopg2.Error as e:
            self.sSqlError = str(e)
            self.sErro = f'Ocorreu o seguinte erro na inserção do erro na tabela seg_erros_sql: {self.sSqlError} <br> Query: {sSqlErroExecucao}'

    def recordCount(self):
        if self.pConsulta.description is not None:
            return self.pConsulta.rowcount()

    def fetchObject(self):
        if self.pConsulta.description is not None:
            return self.pConsulta.fetchone()

    def close(self):
        self.pConexao.close()

    def getErroSql(self):
        return self.sSqlError

    def setConexao(self,sBanco):
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

    def setQtdTabelas(self,nQtdTabelas):
        self.nQtdTabelas = nQtdTabelas

    def getQtdTabelas(self):
        return self.nQtdTabelas

    def setQtdCampos(self,nQtdCampos):
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

    def pegaCampos(self,sNomeBanco, sNomeTabela, sSchema='public'):
        sSql = f"""select T.TABLE_CATALOG, T.TABLE_SCHEMA, T.TABLE_NAME, C.COLUMN_NAME, C.DATA_TYPE, substring(substring(CCU.CONSTRAINT_NAME,length(ccu.constraint_name)-3,length(ccu.constraint_name)),1,2) as PRI from INFORMATION_SCHEMA.TABLES T
                    join INFORMATION_SCHEMA.COLUMNS C
                        on C.TABLE_CATALOG = T.TABLE_CATALOG
                        and C.TABLE_NAME = T.TABLE_NAME
                        and C.TABLE_SCHEMA = T.TABLE_SCHEMA
                    left join INFORMATION_SCHEMA.CONSTRAINT_COLUMN_USAGE CCU
                        on CCU.TABLE_CATALOG = C.TABLE_CATALOG
                        and CCU.TABLE_NAME = C.TABLE_NAME
                        and CCU.TABLE_SCHEMA = C.TABLE_SCHEMA
                        and CCU.COLUMN_NAME = C.COLUMN_NAME
                        and substring(CCU.CONSTRAINT_NAME,length(ccu.constraint_name)-3,length(ccu.constraint_name)) = 'pkey'
                    where T.TABLE_CATALOG = '{sNomeBanco}' AND T.table_schema = '{sSchema}' and T.TABLE_NAME = '{sNomeTabela}' order by C.ORDINAL_POSITION"""
        self.execute(sSql)
        voObjeto = []
        while True:
            oReg = self.fetchObject()
            if not oReg:
                break
            voObjeto.append(oReg)
        return voObjeto


