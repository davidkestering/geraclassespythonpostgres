from classes.ErrosMysqlBDParent import ErrosMysqlBDParent

class ErrosMysqlBD(ErrosMysqlBDParent):
    def __init__(self, sBanco):
        self.pConexao = ErrosMysqlBDParent(sBanco=sBanco)
