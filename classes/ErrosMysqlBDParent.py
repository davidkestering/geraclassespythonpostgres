from classes.ErrosMysql import ErrosMysql
from classes.Conexao import Conexao

class ErrosMysqlBDParent(Conexao):
    def __init__(self, sBanco):
        self.pConexao = Conexao(sServidor=sBanco)

    def getConexao(self):
        return Conexao.getConexao(self.pConexao)

    def recupera(self, nId):
        oConexao = self.getConexao()
        sSql = f"select * from seg_erros_mysql where id = '{nId}'"
        oConexao.execute(sSql)
        oReg = oConexao.fetchObject()
        if oReg:
            oErrosMysql = ErrosMysql(oReg.id,oConexao.unescapeString(oReg.erro),oReg.id_usuario,oConexao.unescapeString(oReg.ip),oReg.dt_cadastro,oReg.publicado,oReg.ativo)
            return oErrosMysql
        return False

    def presente(self, nId):
        oConexao = self.getConexao()
        sSql = f"select id from seg_erros_mysql where id = '{nId}'"
        oConexao.execute(sSql)
        oReg = oConexao.fetchObject()
        if oReg:
            return len(oReg) > 0
        return 0

    def insere(self, oErrosMysql):
        oConexao = self.getConexao()
        sSql = f"insert into seg_erros_mysql (erro,id_usuario,ip,dt_cadastro,publicado,ativo) values ('{oConexao.escapeString(oErrosMysql.getErro())}','{oErrosMysql.getIdUsuario()}','{oConexao.escapeString(oErrosMysql.getIp())}','{oErrosMysql.getDtCadastro()}','{oErrosMysql.getPublicado()}','{oErrosMysql.getAtivo()}')"
        oConexao.execute(sSql)
        nId = oConexao.getLastId()
        if nId:
            return nId
        return oConexao.getConsulta()

    def altera(self, oErrosMysql):
        oConexao = self.getConexao()
        sSql = f"update seg_erros_mysql set erro = '{oConexao.escapeString(oErrosMysql.getErro())}', id_usuario = '{oErrosMysql.getIdUsuario()}', ip = '{oConexao.escapeString(oErrosMysql.getIp())}', dt_cadastro = '{oErrosMysql.getDtCadastro()}', publicado = '{oErrosMysql.getPublicado()}', ativo = '{oErrosMysql.getAtivo()}' where id = '{oErrosMysql.getId()}'"
        oConexao.execute(sSql)
        return oConexao.getConsulta()

    def recuperaTodos(self, vWhere, sOrder):
        oConexao = self.getConexao()
        if isinstance(vWhere, list) and len(vWhere) > 0:
            sSql2 = ""
            for sWhere in vWhere:
                if sWhere != "":
                    sSql2 += sWhere + " AND "
            if sSql2 != "":
                sSql = "SELECT * FROM seg_erros_mysql WHERE "
                sSql = (sSql + sSql2)[:-5]
            else:
                sSql = "SELECT * FROM seg_erros_mysql "
        else:
            sSql = "SELECT * FROM seg_erros_mysql "

        if sOrder:
            sSql += " ORDER BY " + sOrder

        oConexao.execute(sSql)
        voObjeto = []
        while oReg := oConexao.fetchObject():
            oErrosMysql = ErrosMysql(oReg.id,oConexao.unescapeString(oReg.erro),oReg.id_usuario,oConexao.unescapeString(oReg.ip),oReg.dt_cadastro,oReg.publicado,oReg.ativo)
            voObjeto.append(oErrosMysql)
            del oErrosMysql
        return voObjeto

    def exclui(self, nId):
        oConexao = self.getConexao()
        sSql = f"delete from seg_erros_mysql where id = '{nId}'"
        oConexao.execute(sSql)
        return oConexao.getConsulta()

    def desativa(self, nId):
        oConexao = self.getConexao()
        sSql = f"update seg_erros_mysql set ativo = '0' where id = '{nId}'"
        oConexao.execute(sSql)
        return oConexao.getConsulta()