package br.com.pharos.infraestrutura;

import br.com.pharos.dominio.Parada;
import br.com.pharos.excecao.ErroPersistenciaException;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import org.springframework.stereotype.Repository;

/** Acesso à tabela PH_PARADA. */
@Repository
public class ParadaDAO {

    private static final String COLUNAS = "id_parada, cd_parada_gtfs, nm_parada, nm_municipio, "
            + "nr_latitude, nr_longitude, fl_terminal, fl_selecionavel, id_fonte";

    public List<Parada> listar(String selecionavel) {
        String sql = "SELECT " + COLUNAS + " FROM ph_parada"
                + (selecionavel != null ? " WHERE fl_selecionavel = ?" : "")
                + " ORDER BY nm_parada";
        List<Parada> lista = new ArrayList<>();
        try (Connection conn = ConexaoOracle.getConnection();
             PreparedStatement ps = conn.prepareStatement(sql)) {
            if (selecionavel != null) {
                ps.setString(1, selecionavel);
            }
            try (ResultSet rs = ps.executeQuery()) {
                while (rs.next()) {
                    lista.add(mapear(rs));
                }
            }
        } catch (SQLException e) {
            throw TradutorErroSql.traduzir(e, "listar paradas");
        }
        return lista;
    }

    public Optional<Parada> buscarPorId(long id) {
        String sql = "SELECT " + COLUNAS + " FROM ph_parada WHERE id_parada = ?";
        try (Connection conn = ConexaoOracle.getConnection();
             PreparedStatement ps = conn.prepareStatement(sql)) {
            ps.setLong(1, id);
            try (ResultSet rs = ps.executeQuery()) {
                return rs.next() ? Optional.of(mapear(rs)) : Optional.empty();
            }
        } catch (SQLException e) {
            throw TradutorErroSql.traduzir(e, "buscar parada");
        }
    }

    public long inserir(Parada p) {
        String sql = "INSERT INTO ph_parada (cd_parada_gtfs, nm_parada, nm_municipio, nr_latitude, "
                + "nr_longitude, fl_terminal, fl_selecionavel, id_fonte) VALUES (?, ?, ?, ?, ?, ?, ?, ?)";
        try (Connection conn = ConexaoOracle.getConnection();
             PreparedStatement ps = conn.prepareStatement(sql, new String[] {"ID_PARADA"})) {
            preencher(ps, p);
            ps.executeUpdate();
            try (ResultSet chaves = ps.getGeneratedKeys()) {
                if (chaves.next()) {
                    return chaves.getLong(1);
                }
            }
            throw new ErroPersistenciaException("Parada gravada, mas o identificador não foi retornado.", null);
        } catch (SQLException e) {
            throw TradutorErroSql.traduzir(e, "inserir parada");
        }
    }

    public boolean atualizar(long id, Parada p) {
        String sql = "UPDATE ph_parada SET cd_parada_gtfs = ?, nm_parada = ?, nm_municipio = ?, "
                + "nr_latitude = ?, nr_longitude = ?, fl_terminal = ?, fl_selecionavel = ?, id_fonte = ? "
                + "WHERE id_parada = ?";
        try (Connection conn = ConexaoOracle.getConnection();
             PreparedStatement ps = conn.prepareStatement(sql)) {
            preencher(ps, p);
            ps.setLong(9, id);
            return ps.executeUpdate() > 0;
        } catch (SQLException e) {
            throw TradutorErroSql.traduzir(e, "atualizar parada");
        }
    }

    public boolean excluir(long id) {
        String sql = "DELETE FROM ph_parada WHERE id_parada = ?";
        try (Connection conn = ConexaoOracle.getConnection();
             PreparedStatement ps = conn.prepareStatement(sql)) {
            ps.setLong(1, id);
            return ps.executeUpdate() > 0;
        } catch (SQLException e) {
            throw TradutorErroSql.traduzir(e, "excluir parada");
        }
    }

    private void preencher(PreparedStatement ps, Parada p) throws SQLException {
        ps.setString(1, p.cdParadaGtfs());
        ps.setString(2, p.nmParada());
        ps.setString(3, p.nmMunicipio());
        JdbcUtil.setDouble(ps, 4, p.nrLatitude());
        JdbcUtil.setDouble(ps, 5, p.nrLongitude());
        ps.setString(6, p.flTerminal());
        ps.setString(7, p.flSelecionavel());
        ps.setLong(8, p.idFonte());
    }

    static Parada mapear(ResultSet rs) throws SQLException {
        return new Parada(
                rs.getLong("id_parada"),
                rs.getString("cd_parada_gtfs"),
                rs.getString("nm_parada"),
                rs.getString("nm_municipio"),
                JdbcUtil.getDouble(rs, "nr_latitude"),
                JdbcUtil.getDouble(rs, "nr_longitude"),
                rs.getString("fl_terminal"),
                rs.getString("fl_selecionavel"),
                rs.getLong("id_fonte"));
    }
}
