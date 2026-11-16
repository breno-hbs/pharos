package br.com.pharos.infraestrutura;

import br.com.pharos.dominio.Linha;
import br.com.pharos.excecao.ErroPersistenciaException;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import org.springframework.stereotype.Repository;

/** Acesso à tabela PH_LINHA. */
@Repository
public class LinhaDAO {

    private static final String COLUNAS = "id_linha, cd_linha, ds_itinerario, tp_modal, id_fonte";

    public List<Linha> listar() {
        String sql = "SELECT " + COLUNAS + " FROM ph_linha ORDER BY cd_linha";
        List<Linha> lista = new ArrayList<>();
        try (Connection conn = ConexaoOracle.getConnection();
             PreparedStatement ps = conn.prepareStatement(sql);
             ResultSet rs = ps.executeQuery()) {
            while (rs.next()) {
                lista.add(mapear(rs));
            }
        } catch (SQLException e) {
            throw TradutorErroSql.traduzir(e, "listar linhas");
        }
        return lista;
    }

    public Optional<Linha> buscarPorId(long id) {
        String sql = "SELECT " + COLUNAS + " FROM ph_linha WHERE id_linha = ?";
        try (Connection conn = ConexaoOracle.getConnection();
             PreparedStatement ps = conn.prepareStatement(sql)) {
            ps.setLong(1, id);
            try (ResultSet rs = ps.executeQuery()) {
                return rs.next() ? Optional.of(mapear(rs)) : Optional.empty();
            }
        } catch (SQLException e) {
            throw TradutorErroSql.traduzir(e, "buscar linha");
        }
    }

    public long inserir(Linha l) {
        String sql = "INSERT INTO ph_linha (cd_linha, ds_itinerario, tp_modal, id_fonte) VALUES (?, ?, ?, ?)";
        try (Connection conn = ConexaoOracle.getConnection();
             PreparedStatement ps = conn.prepareStatement(sql, new String[] {"ID_LINHA"})) {
            preencher(ps, l);
            ps.executeUpdate();
            try (ResultSet chaves = ps.getGeneratedKeys()) {
                if (chaves.next()) {
                    return chaves.getLong(1);
                }
            }
            throw new ErroPersistenciaException("Linha gravada, mas o identificador não foi retornado.", null);
        } catch (SQLException e) {
            throw TradutorErroSql.traduzir(e, "inserir linha");
        }
    }

    public boolean atualizar(long id, Linha l) {
        String sql = "UPDATE ph_linha SET cd_linha = ?, ds_itinerario = ?, tp_modal = ?, id_fonte = ? "
                + "WHERE id_linha = ?";
        try (Connection conn = ConexaoOracle.getConnection();
             PreparedStatement ps = conn.prepareStatement(sql)) {
            preencher(ps, l);
            ps.setLong(5, id);
            return ps.executeUpdate() > 0;
        } catch (SQLException e) {
            throw TradutorErroSql.traduzir(e, "atualizar linha");
        }
    }

    public boolean excluir(long id) {
        String sql = "DELETE FROM ph_linha WHERE id_linha = ?";
        try (Connection conn = ConexaoOracle.getConnection();
             PreparedStatement ps = conn.prepareStatement(sql)) {
            ps.setLong(1, id);
            return ps.executeUpdate() > 0;
        } catch (SQLException e) {
            throw TradutorErroSql.traduzir(e, "excluir linha");
        }
    }

    private void preencher(PreparedStatement ps, Linha l) throws SQLException {
        ps.setString(1, l.cdLinha());
        ps.setString(2, l.dsItinerario());
        ps.setString(3, l.tpModal());
        ps.setLong(4, l.idFonte());
    }

    private Linha mapear(ResultSet rs) throws SQLException {
        return new Linha(
                rs.getLong("id_linha"),
                rs.getString("cd_linha"),
                rs.getString("ds_itinerario"),
                rs.getString("tp_modal"),
                rs.getLong("id_fonte"));
    }
}
