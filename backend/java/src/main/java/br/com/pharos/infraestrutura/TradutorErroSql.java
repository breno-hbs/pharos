package br.com.pharos.infraestrutura;

import br.com.pharos.excecao.ConflitoException;
import br.com.pharos.excecao.ErroPersistenciaException;
import br.com.pharos.excecao.RegraNegocioException;
import java.sql.SQLException;

/** Converte erros ORA-xxxxx do Oracle em exceções da aplicação (e portanto em códigos HTTP). */
final class TradutorErroSql {

    private TradutorErroSql() {
    }

    static RuntimeException traduzir(SQLException e, String operacao) {
        switch (e.getErrorCode()) {
            case 1:      // ORA-00001: violação de chave única
                return new ConflitoException("Já existe um registro com esses dados únicos.");
            case 2292:   // ORA-02292: existem registros filhos
                return new ConflitoException(
                        "Registro em uso por outros dados. Remova os dependentes antes de excluir.");
            case 2291:   // ORA-02291: chave estrangeira sem pai
                return new RegraNegocioException("Referência inválida: o registro relacionado não existe.");
            case 2290:   // ORA-02290: violação de CHECK
                return new RegraNegocioException("Os dados informados violam uma restrição do banco.");
            case 12899:  // ORA-12899: valor maior que a coluna
                return new RegraNegocioException("Um dos valores excede o tamanho permitido.");
            case 1400:   // ORA-01400: NOT NULL
                return new RegraNegocioException("Campo obrigatório não informado.");
            default:
                return new ErroPersistenciaException("Erro ao acessar o banco de dados (" + operacao + ").", e);
        }
    }
}
