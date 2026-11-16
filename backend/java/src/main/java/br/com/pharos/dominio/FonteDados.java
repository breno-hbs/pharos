package br.com.pharos.dominio;

import java.time.LocalDate;

/** Tabela PH_FONTE_DADOS: origem, período e limitações de cada informação exibida. */
public record FonteDados(
        Long idFonte,
        String nmFonte,
        String nmOrgao,
        String dsVersao,
        String dsUrl,
        LocalDate dtInicioPeriodo,
        LocalDate dtFimPeriodo,
        String flSimulado,
        String dsLimitacao) {
}
