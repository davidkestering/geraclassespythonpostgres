from classes.ErrosMysqlParent import ErrosMysqlParent

class ErrosMysql(ErrosMysqlParent):
    def __init__(self, nId,sErro,nIdUsuario,sIp,dDtCadastro,bPublicado,bAtivo):
        self.setId(nId)
        self.setErro(sErro)
        self.setIdUsuario(nIdUsuario)
        self.setIp(sIp)
        self.setDtCadastro(dDtCadastro)
        self.setPublicado(bPublicado)
        self.setAtivo(bAtivo)
        