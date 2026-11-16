package br.com.pharos.infraestrutura;

import java.math.BigDecimal;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Types;

/** Auxiliares para ler e gravar colunas que aceitam NULL. */
final class JdbcUtil {

    private JdbcUtil() {
    }

    static Long getLong(ResultSet rs, String coluna) throws SQLException {
        long v = rs.getLong(coluna);
        return rs.wasNull() ? null : v;
    }

    static Integer getInt(ResultSet rs, String coluna) throws SQLException {
        int v = rs.getInt(coluna);
        return rs.wasNull() ? null : v;
    }

    static Double getDouble(ResultSet rs, String coluna) throws SQLException {
        BigDecimal v = rs.getBigDecimal(coluna);
        return v == null ? null : v.doubleValue();
    }

    static void setLong(PreparedStatement ps, int pos, Long valor) throws SQLException {
        if (valor == null) {
            ps.setNull(pos, Types.NUMERIC);
        } else {
            ps.setLong(pos, valor);
        }
    }

    static void setInt(PreparedStatement ps, int pos, Integer valor) throws SQLException {
        if (valor == null) {
            ps.setNull(pos, Types.NUMERIC);
        } else {
            ps.setInt(pos, valor);
        }
    }

    static void setDouble(PreparedStatement ps, int pos, Double valor) throws SQLException {
        if (valor == null) {
            ps.setNull(pos, Types.NUMERIC);
        } else {
            ps.setDouble(pos, valor);
        }
    }
}
