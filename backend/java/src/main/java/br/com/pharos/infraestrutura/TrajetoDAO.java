package br.com.pharos.infraestrutura;

import br.com.pharos.dominio.Alternativa;
import br.com.pharos.dominio.AlternativaDetalhe;
import br.com.pharos.dominio.EtapaDetalhe;
import br.com.pharos.dominio.IndicadorDetalhe;
import br.com.pharos.dominio.ParComAlternativas;
import br.com.pharos.dominio.ParOrigemDestino;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Timestamp;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import org.springframework.stereotype.Repository;

/**
 * Leitura dos trajetos já calculados pelo módulo de Dynamic Programming:
 * PH_PAR_ORIGEM_DESTINO, PH_ALTERNATIVA, PH_ETAPA_TRAJETO e PH_INDICADOR_OCORRENCIA.
 * A API só consulta: o cálculo (Floyd-Warshall) roda antes, em Python.
 */
@Repository
public class TrajetoDAO {

    /** Raio usado para somar as ocorrências de uma alternativa (evita contar o mesmo dado em 3 raios). */
    private static final int RAIO_TOTAL_M = 250;

    /** Busca o par e, numa única conexão, todas as alternativas com etapas e indicadores. */
    public Optional<ParComAlternativas> buscarCompleto(long idCenario, long idOrigem, long idDestino) {
        String sqlPar = "SELECT id_par_od, id_cenario, id_parada_origem, id_parada_destino, st_resultado, "
                + "dt_calculo, id_fonte FROM ph_par_origem_destino "
                + "WHERE id_cenario = ? AND id_parada_origem = ? AND id_parada_destino = ?";
        try (Connection conn = ConexaoOracle.getConnection();
             PreparedStatement ps = conn.prepareStatement(sqlPar)) {
            ps.setLong(1, idCenario);
            ps.setLong(2, idOrigem);
            ps.setLong(3, idDestino);
            ParOrigemDestino par;
            try (ResultSet rs = ps.executeQuery()) {
                if (!rs.next()) {
                    return Optional.empty();
                }
                par = mapearPar(rs);
            }
            List<AlternativaDetalhe> alternativas = new ArrayList<>();
            for (Alternativa alt : listarAlternativas(conn, par.idParOd())) {
                List<EtapaDetalhe> etapas = listarEtapas(conn, alt.idAlternativa());
                List<IndicadorDetalhe> indicadores = new ArrayList<>();
                int total = listarIndicadores(conn, alt.idAlternativa(), indicadores);
                alternativas.add(new AlternativaDetalhe(alt, etapas, indicadores, total));
            }
            return Optional.of(new ParComAlternativas(par, alternativas));
        } catch (SQLException e) {
            throw TradutorErroSql.traduzir(e, "buscar trajeto");
        }
    }

    public Optional<ParOrigemDestino> buscarParPorId(long idParOd) {
        String sql = "SELECT id_par_od, id_cenario, id_parada_origem, id_parada_destino, st_resultado, "
                + "dt_calculo, id_fonte FROM ph_par_origem_destino WHERE id_par_od = ?";
        try (Connection conn = ConexaoOracle.getConnection();
             PreparedStatement ps = conn.prepareStatement(sql)) {
            ps.setLong(1, idParOd);
            try (ResultSet rs = ps.executeQuery()) {
                return rs.next() ? Optional.of(mapearPar(rs)) : Optional.empty();
            }
        } catch (SQLException e) {
            throw TradutorErroSql.traduzir(e, "buscar par origem-destino");
        }
    }

    /** Verifica se a alternativa existe e pertence ao par informado. */
    public boolean alternativaPertenceAoPar(long idAlternativa, long idParOd) {
        String sql = "SELECT 1 FROM ph_alternativa WHERE id_alternativa = ? AND id_par_od = ?";
        try (Connection conn = ConexaoOracle.getConnection();
             PreparedStatement ps = conn.prepareStatement(sql)) {
            ps.setLong(1, idAlternativa);
            ps.setLong(2, idParOd);
            try (ResultSet rs = ps.executeQuery()) {
                return rs.next();
            }
        } catch (SQLException e) {
            throw TradutorErroSql.traduzir(e, "validar alternativa");
        }
    }

    private List<Alternativa> listarAlternativas(Connection conn, long idParOd) throws SQLException {
        String sql = "SELECT id_alternativa, id_par_od, nr_ordem, nr_tempo_total_min, nr_distancia_km, "
                + "qt_baldeacoes FROM ph_alternativa WHERE id_par_od = ? ORDER BY nr_ordem";
        List<Alternativa> lista = new ArrayList<>();
        try (PreparedStatement ps = conn.prepareStatement(sql)) {
            ps.setLong(1, idParOd);
            try (ResultSet rs = ps.executeQuery()) {
                while (rs.next()) {
                    lista.add(new Alternativa(
                            rs.getLong("id_alternativa"),
                            rs.getLong("id_par_od"),
                            rs.getInt("nr_ordem"),
                            JdbcUtil.getDouble(rs, "nr_tempo_total_min"),
                            JdbcUtil.getDouble(rs, "nr_distancia_km"),
                            rs.getInt("qt_baldeacoes")));
                }
            }
        }
        return lista;
    }

    private List<EtapaDetalhe> listarEtapas(Connection conn, long idAlternativa) throws SQLException {
        String sql = "SELECT e.id_etapa, e.nr_sequencia, e.id_linha, l.cd_linha, "
                + "e.id_parada_embarque, pe.nm_parada AS nm_embarque, "
                + "e.id_parada_desembarque, pd.nm_parada AS nm_desembarque "
                + "FROM ph_etapa_trajeto e "
                + "INNER JOIN ph_linha l ON l.id_linha = e.id_linha "
                + "INNER JOIN ph_parada pe ON pe.id_parada = e.id_parada_embarque "
                + "INNER JOIN ph_parada pd ON pd.id_parada = e.id_parada_desembarque "
                + "WHERE e.id_alternativa = ? ORDER BY e.nr_sequencia";
        List<EtapaDetalhe> lista = new ArrayList<>();
        try (PreparedStatement ps = conn.prepareStatement(sql)) {
            ps.setLong(1, idAlternativa);
            try (ResultSet rs = ps.executeQuery()) {
                while (rs.next()) {
                    lista.add(new EtapaDetalhe(
                            rs.getLong("id_etapa"),
                            rs.getInt("nr_sequencia"),
                            rs.getLong("id_linha"),
                            rs.getString("cd_linha"),
                            rs.getLong("id_parada_embarque"),
                            rs.getString("nm_embarque"),
                            rs.getLong("id_parada_desembarque"),
                            rs.getString("nm_desembarque")));
                }
            }
        }
        return lista;
    }

    /** Preenche a lista de indicadores e devolve o total de ocorrências no raio de referência. */
    private int listarIndicadores(Connection conn, long idAlternativa, List<IndicadorDetalhe> destino)
            throws SQLException {
        String sql = "SELECT i.id_indicador, t.cd_tipo, t.nm_tipo, i.nr_ano, i.tp_faixa_horaria, "
                + "i.nr_raio_m, i.qt_ocorrencias, f.nm_fonte, f.fl_simulado "
                + "FROM ph_indicador_ocorrencia i "
                + "INNER JOIN ph_tipo_ocorrencia t ON t.id_tipo_ocorrencia = i.id_tipo_ocorrencia "
                + "INNER JOIN ph_fonte_dados f ON f.id_fonte = i.id_fonte "
                + "WHERE i.id_alternativa = ? ORDER BY i.nr_ano, t.cd_tipo, i.tp_faixa_horaria, i.nr_raio_m";
        int total = 0;
        try (PreparedStatement ps = conn.prepareStatement(sql)) {
            ps.setLong(1, idAlternativa);
            try (ResultSet rs = ps.executeQuery()) {
                while (rs.next()) {
                    int raio = rs.getInt("nr_raio_m");
                    int qtd = rs.getInt("qt_ocorrencias");
                    if (raio == RAIO_TOTAL_M) {
                        total += qtd;
                    }
                    destino.add(new IndicadorDetalhe(
                            rs.getLong("id_indicador"),
                            rs.getString("cd_tipo"),
                            rs.getString("nm_tipo"),
                            rs.getInt("nr_ano"),
                            rs.getString("tp_faixa_horaria"),
                            raio,
                            qtd,
                            rs.getString("nm_fonte"),
                            "S".equals(rs.getString("fl_simulado"))));
                }
            }
        }
        return total;
    }

    private ParOrigemDestino mapearPar(ResultSet rs) throws SQLException {
        Timestamp calculo = rs.getTimestamp("dt_calculo");
        return new ParOrigemDestino(
                rs.getLong("id_par_od"),
                rs.getLong("id_cenario"),
                rs.getLong("id_parada_origem"),
                rs.getLong("id_parada_destino"),
                rs.getString("st_resultado"),
                calculo == null ? null : calculo.toLocalDateTime(),
                rs.getLong("id_fonte"));
    }
}
