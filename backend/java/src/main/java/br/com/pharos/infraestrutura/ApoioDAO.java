package br.com.pharos.infraestrutura;

import br.com.pharos.dominio.Cenario;
import br.com.pharos.dominio.FonteDados;
import br.com.pharos.dominio.TipoOcorrencia;
import java.sql.Connection;
import java.sql.Date;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import org.springframework.stereotype.Repository;

/** Leitura das tabelas de apoio: PH_CENARIO, PH_FONTE_DADOS e PH_TIPO_OCORRENCIA. */
@Repository
public class ApoioDAO {

    private static final String COLUNAS_CENARIO =
            "id_cenario, cd_cenario, nm_cenario, tp_dia, nr_hora_inicio, nr_hora_fim";

    public List<Cenario> listarCenarios() {
        String sql = "SELECT " + COLUNAS_CENARIO + " FROM ph_cenario ORDER BY id_cenario";
        List<Cenario> lista = new ArrayList<>();
        try (Connection conn = ConexaoOracle.getConnection();
             PreparedStatement ps = conn.prepareStatement(sql);
             ResultSet rs = ps.executeQuery()) {
            while (rs.next()) {
                lista.add(mapearCenario(rs));
            }
        } catch (SQLException e) {
            throw TradutorErroSql.traduzir(e, "listar cenários");
        }
        return lista;
    }

    public Optional<Cenario> buscarCenarioPorCodigo(String codigo) {
        String sql = "SELECT " + COLUNAS_CENARIO + " FROM ph_cenario WHERE cd_cenario = ?";
        try (Connection conn = ConexaoOracle.getConnection();
             PreparedStatement ps = conn.prepareStatement(sql)) {
            ps.setString(1, codigo);
            try (ResultSet rs = ps.executeQuery()) {
                return rs.next() ? Optional.of(mapearCenario(rs)) : Optional.empty();
            }
        } catch (SQLException e) {
            throw TradutorErroSql.traduzir(e, "buscar cenário");
        }
    }

    /** Cenário cuja janela de horário contém a hora informada (início inclusive, fim exclusive). */
    public Optional<Cenario> buscarCenarioPorHorario(String tipoDia, int hora) {
        String sql = "SELECT " + COLUNAS_CENARIO + " FROM ph_cenario "
                + "WHERE tp_dia = ? AND ? >= nr_hora_inicio AND ? < nr_hora_fim "
                + "ORDER BY id_cenario FETCH FIRST 1 ROWS ONLY";
        try (Connection conn = ConexaoOracle.getConnection();
             PreparedStatement ps = conn.prepareStatement(sql)) {
            ps.setString(1, tipoDia);
            ps.setInt(2, hora);
            ps.setInt(3, hora);
            try (ResultSet rs = ps.executeQuery()) {
                return rs.next() ? Optional.of(mapearCenario(rs)) : Optional.empty();
            }
        } catch (SQLException e) {
            throw TradutorErroSql.traduzir(e, "buscar cenário por horário");
        }
    }

    public List<FonteDados> listarFontes() {
        String sql = "SELECT id_fonte, nm_fonte, nm_orgao, ds_versao, ds_url, dt_inicio_periodo, "
                + "dt_fim_periodo, fl_simulado, ds_limitacao FROM ph_fonte_dados ORDER BY id_fonte";
        List<FonteDados> lista = new ArrayList<>();
        try (Connection conn = ConexaoOracle.getConnection();
             PreparedStatement ps = conn.prepareStatement(sql);
             ResultSet rs = ps.executeQuery()) {
            while (rs.next()) {
                Date ini = rs.getDate("dt_inicio_periodo");
                Date fim = rs.getDate("dt_fim_periodo");
                lista.add(new FonteDados(
                        rs.getLong("id_fonte"),
                        rs.getString("nm_fonte"),
                        rs.getString("nm_orgao"),
                        rs.getString("ds_versao"),
                        rs.getString("ds_url"),
                        ini == null ? null : ini.toLocalDate(),
                        fim == null ? null : fim.toLocalDate(),
                        rs.getString("fl_simulado"),
                        rs.getString("ds_limitacao")));
            }
        } catch (SQLException e) {
            throw TradutorErroSql.traduzir(e, "listar fontes");
        }
        return lista;
    }

    public List<TipoOcorrencia> listarTiposOcorrencia() {
        String sql = "SELECT id_tipo_ocorrencia, cd_tipo, nm_tipo, ds_tipo FROM ph_tipo_ocorrencia "
                + "ORDER BY id_tipo_ocorrencia";
        List<TipoOcorrencia> lista = new ArrayList<>();
        try (Connection conn = ConexaoOracle.getConnection();
             PreparedStatement ps = conn.prepareStatement(sql);
             ResultSet rs = ps.executeQuery()) {
            while (rs.next()) {
                lista.add(new TipoOcorrencia(
                        rs.getLong("id_tipo_ocorrencia"),
                        rs.getString("cd_tipo"),
                        rs.getString("nm_tipo"),
                        rs.getString("ds_tipo")));
            }
        } catch (SQLException e) {
            throw TradutorErroSql.traduzir(e, "listar tipos de ocorrência");
        }
        return lista;
    }

    /** Testa a conexão com o banco (usado por GET /saude). */
    public boolean bancoDisponivel() {
        try (Connection conn = ConexaoOracle.getConnection();
             PreparedStatement ps = conn.prepareStatement("SELECT 1 FROM dual");
             ResultSet rs = ps.executeQuery()) {
            return rs.next();
        } catch (Exception e) {
            return false;
        }
    }

    private Cenario mapearCenario(ResultSet rs) throws SQLException {
        return new Cenario(
                rs.getLong("id_cenario"),
                rs.getString("cd_cenario"),
                rs.getString("nm_cenario"),
                rs.getString("tp_dia"),
                rs.getInt("nr_hora_inicio"),
                rs.getInt("nr_hora_fim"));
    }
}
