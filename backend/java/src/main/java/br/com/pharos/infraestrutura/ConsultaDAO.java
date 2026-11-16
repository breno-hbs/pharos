package br.com.pharos.infraestrutura;

import br.com.pharos.dominio.Consulta;
import br.com.pharos.excecao.ErroPersistenciaException;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Timestamp;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import org.springframework.stereotype.Repository;

/** Acesso à tabela PH_CONSULTA (registro anônimo das consultas). */
@Repository
public class ConsultaDAO {

    private static final String COLUNAS = "id_consulta, id_par_od, id_alternativa_escolhida, "
            + "tp_criterio_ordenacao, dt_consulta, nr_tempo_resposta_ms, nr_avaliacao, fl_teste";

    public List<Consulta> listarRecentes() {
        String sql = "SELECT " + COLUNAS + " FROM ph_consulta ORDER BY dt_consulta DESC "
                + "FETCH FIRST 100 ROWS ONLY";
        List<Consulta> lista = new ArrayList<>();
        try (Connection conn = ConexaoOracle.getConnection();
             PreparedStatement ps = conn.prepareStatement(sql);
             ResultSet rs = ps.executeQuery()) {
            while (rs.next()) {
                lista.add(mapear(rs));
            }
        } catch (SQLException e) {
            throw TradutorErroSql.traduzir(e, "listar consultas");
        }
        return lista;
    }

    public Optional<Consulta> buscarPorId(long id) {
        String sql = "SELECT " + COLUNAS + " FROM ph_consulta WHERE id_consulta = ?";
        try (Connection conn = ConexaoOracle.getConnection();
             PreparedStatement ps = conn.prepareStatement(sql)) {
            ps.setLong(1, id);
            try (ResultSet rs = ps.executeQuery()) {
                return rs.next() ? Optional.of(mapear(rs)) : Optional.empty();
            }
        } catch (SQLException e) {
            throw TradutorErroSql.traduzir(e, "buscar consulta");
        }
    }

    public long inserir(Consulta c) {
        String sql = "INSERT INTO ph_consulta (id_par_od, id_alternativa_escolhida, tp_criterio_ordenacao, "
                + "nr_tempo_resposta_ms, nr_avaliacao, fl_teste) VALUES (?, ?, ?, ?, ?, ?)";
        try (Connection conn = ConexaoOracle.getConnection();
             PreparedStatement ps = conn.prepareStatement(sql, new String[] {"ID_CONSULTA"})) {
            ps.setLong(1, c.idParOd());
            JdbcUtil.setLong(ps, 2, c.idAlternativaEscolhida());
            ps.setString(3, c.tpCriterioOrdenacao());
            JdbcUtil.setInt(ps, 4, c.nrTempoRespostaMs());
            JdbcUtil.setInt(ps, 5, c.nrAvaliacao());
            ps.setString(6, c.flTeste());
            ps.executeUpdate();
            try (ResultSet chaves = ps.getGeneratedKeys()) {
                if (chaves.next()) {
                    return chaves.getLong(1);
                }
            }
            throw new ErroPersistenciaException("Consulta gravada, mas o identificador não foi retornado.", null);
        } catch (SQLException e) {
            throw TradutorErroSql.traduzir(e, "inserir consulta");
        }
    }

    public boolean atualizar(long id, Long idAlternativaEscolhida, Integer avaliacao) {
        String sql = "UPDATE ph_consulta SET id_alternativa_escolhida = ?, nr_avaliacao = ? "
                + "WHERE id_consulta = ?";
        try (Connection conn = ConexaoOracle.getConnection();
             PreparedStatement ps = conn.prepareStatement(sql)) {
            JdbcUtil.setLong(ps, 1, idAlternativaEscolhida);
            JdbcUtil.setInt(ps, 2, avaliacao);
            ps.setLong(3, id);
            return ps.executeUpdate() > 0;
        } catch (SQLException e) {
            throw TradutorErroSql.traduzir(e, "atualizar consulta");
        }
    }

    public boolean excluir(long id) {
        String sql = "DELETE FROM ph_consulta WHERE id_consulta = ?";
        try (Connection conn = ConexaoOracle.getConnection();
             PreparedStatement ps = conn.prepareStatement(sql)) {
            ps.setLong(1, id);
            return ps.executeUpdate() > 0;
        } catch (SQLException e) {
            throw TradutorErroSql.traduzir(e, "excluir consulta");
        }
    }

    private Consulta mapear(ResultSet rs) throws SQLException {
        Timestamp data = rs.getTimestamp("dt_consulta");
        return new Consulta(
                rs.getLong("id_consulta"),
                rs.getLong("id_par_od"),
                JdbcUtil.getLong(rs, "id_alternativa_escolhida"),
                rs.getString("tp_criterio_ordenacao"),
                data == null ? null : data.toLocalDateTime(),
                JdbcUtil.getInt(rs, "nr_tempo_resposta_ms"),
                JdbcUtil.getInt(rs, "nr_avaliacao"),
                rs.getString("fl_teste"));
    }
}
