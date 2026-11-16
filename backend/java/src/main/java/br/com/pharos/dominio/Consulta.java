package br.com.pharos.dominio;

import java.time.LocalDateTime;

/** Tabela PH_CONSULTA: registro anônimo de cada consulta feita na plataforma. */
public record Consulta(
        Long idConsulta,
        Long idParOd,
        Long idAlternativaEscolhida,
        String tpCriterioOrdenacao,
        LocalDateTime dtConsulta,
        Integer nrTempoRespostaMs,
        Integer nrAvaliacao,
        String flTeste) {
}
