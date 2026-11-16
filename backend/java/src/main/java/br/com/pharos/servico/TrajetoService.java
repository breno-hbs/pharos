package br.com.pharos.servico;

import br.com.pharos.dominio.AlternativaDetalhe;
import br.com.pharos.dominio.Cenario;
import br.com.pharos.dominio.Parada;
import br.com.pharos.dominio.ParComAlternativas;
import br.com.pharos.dominio.TrajetoResposta;
import br.com.pharos.excecao.RecursoNaoEncontradoException;
import br.com.pharos.excecao.RegraNegocioException;
import br.com.pharos.infraestrutura.ApoioDAO;
import br.com.pharos.infraestrutura.ParadaDAO;
import br.com.pharos.infraestrutura.TrajetoDAO;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.Optional;
import java.util.Set;
import org.springframework.stereotype.Service;

/** Regras de negócio (BO) da consulta de trajetos já calculados. */
@Service
public class TrajetoService {

    static final Set<String> CRITERIOS = Set.of("TEMPO", "DISTANCIA", "BALDEACOES", "OCORRENCIAS");
    private static final Set<String> TIPOS_DIA = Set.of("UTIL", "SABADO", "DOMINGO");

    private final TrajetoDAO trajetoDAO;
    private final ParadaDAO paradaDAO;
    private final ApoioDAO apoioDAO;

    public TrajetoService(TrajetoDAO trajetoDAO, ParadaDAO paradaDAO, ApoioDAO apoioDAO) {
        this.trajetoDAO = trajetoDAO;
        this.paradaDAO = paradaDAO;
        this.apoioDAO = apoioDAO;
    }

    public TrajetoResposta consultar(Long origem, Long destino, String cenario, String dia, Integer hora,
                                     String ordenar) {
        long idOrigem = Validacao.idPositivo(origem, "origem");
        long idDestino = Validacao.idPositivo(destino, "destino");
        if (idOrigem == idDestino) {
            throw new RegraNegocioException("A origem deve ser diferente do destino.");
        }
        String criterio = Validacao.dominio(ordenar, "ordenar", CRITERIOS, "TEMPO");

        Optional<Cenario> cenarioEscolhido = resolverCenario(cenario, dia, hora);
        Parada paradaOrigem = paradaDAO.buscarPorId(idOrigem)
                .orElseThrow(() -> new RecursoNaoEncontradoException("Parada de origem não encontrada."));
        Parada paradaDestino = paradaDAO.buscarPorId(idDestino)
                .orElseThrow(() -> new RecursoNaoEncontradoException("Parada de destino não encontrada."));

        if (cenarioEscolhido.isEmpty()) {
            return semDados("Não há dados calculados para esse dia e horário.", null, paradaOrigem,
                    paradaDestino, criterio);
        }
        Cenario cen = cenarioEscolhido.get();
        Optional<ParComAlternativas> encontrado =
                trajetoDAO.buscarCompleto(cen.idCenario(), idOrigem, idDestino);
        if (encontrado.isEmpty()) {
            return semDados("Ainda não há trajetos calculados para este par de paradas no cenário '"
                    + cen.nmCenario() + "'.", cen, paradaOrigem, paradaDestino, criterio);
        }

        ParComAlternativas par = encontrado.get();
        List<AlternativaDetalhe> ordenadas = ordenar(par.alternativas(), criterio);
        String mensagem = ordenadas.isEmpty()
                ? "Sem trajeto disponível para este par neste cenário (status: "
                        + par.par().stResultado() + ")."
                : null;
        return new TrajetoResposta(par.par().idParOd(), par.par().stResultado(), mensagem, cen,
                paradaOrigem, paradaDestino, criterio, ordenadas);
    }

    /** Resposta 200 com status SEM_DADOS: o cenário existe, mas ainda não tem pares calculados. */
    private TrajetoResposta semDados(String mensagem, Cenario cenario, Parada origem, Parada destino,
                                     String criterio) {
        return new TrajetoResposta(null, "SEM_DADOS", mensagem, cenario, origem, destino, criterio, List.of());
    }

    /** Código informado e inexistente gera 404; horário sem cenário cadastrado vira "sem dados". */
    private Optional<Cenario> resolverCenario(String codigo, String dia, Integer hora) {
        if (codigo != null && !codigo.isBlank()) {
            return Optional.of(apoioDAO.buscarCenarioPorCodigo(codigo.trim())
                    .orElseThrow(() -> new RecursoNaoEncontradoException(
                            "Cenário '" + codigo + "' não encontrado.")));
        }
        if (hora == null) {
            throw new RegraNegocioException("Informe o parâmetro 'cenario' ou o parâmetro 'hora' (0 a 23).");
        }
        if (hora < 0 || hora > 23) {
            throw new RegraNegocioException("O parâmetro 'hora' deve estar entre 0 e 23.");
        }
        String tipoDia = Validacao.dominio(dia, "dia", TIPOS_DIA, "UTIL");
        return apoioDAO.buscarCenarioPorHorario(tipoDia, hora);
    }

    List<AlternativaDetalhe> ordenar(List<AlternativaDetalhe> alternativas, String criterio) {
        Comparator<AlternativaDetalhe> porTempo =
                Comparator.comparing(a -> a.alternativa().nrTempoTotalMin());
        Comparator<AlternativaDetalhe> comparador = switch (criterio) {
            case "DISTANCIA" -> Comparator.<AlternativaDetalhe, Double>comparing(
                    a -> a.alternativa().nrDistanciaKm()).thenComparing(porTempo);
            case "BALDEACOES" -> Comparator.<AlternativaDetalhe, Integer>comparing(
                    a -> a.alternativa().qtBaldeacoes()).thenComparing(porTempo);
            case "OCORRENCIAS" -> Comparator.<AlternativaDetalhe, Integer>comparing(
                    AlternativaDetalhe::totalOcorrencias).thenComparing(porTempo);
            default -> porTempo;
        };
        List<AlternativaDetalhe> copia = new ArrayList<>(alternativas);
        copia.sort(comparador);
        return copia;
    }
}
