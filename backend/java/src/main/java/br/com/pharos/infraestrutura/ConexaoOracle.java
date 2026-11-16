package br.com.pharos.infraestrutura;

import br.com.pharos.excecao.ErroPersistenciaException;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;

/**
 * Conexão com o Oracle da FIAP via JDBC (padrão visto em aula).
 * Credenciais vêm de variáveis de ambiente: ORACLE_URL, ORACLE_USER e ORACLE_PASSWORD.
 */
public final class ConexaoOracle {

    private ConexaoOracle() {
    }

    public static Connection getConnection() throws SQLException {
        String url = variavel("ORACLE_URL");
        String usuario = variavel("ORACLE_USER");
        String senha = variavel("ORACLE_PASSWORD");
        return DriverManager.getConnection(url, usuario, senha);
    }

    private static String variavel(String nome) {
        String valor = System.getenv(nome);
        if (valor == null || valor.isBlank()) {
            throw new ErroPersistenciaException(
                    "Configuração do banco ausente: defina a variável de ambiente " + nome + ".", null);
        }
        return valor;
    }
}
