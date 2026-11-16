package br.com.pharos.dominio;

/** Tabela PH_CENARIO: tipo de dia e janela de horário usados no cálculo das alternativas. */
public record Cenario(
        Long idCenario,
        String cdCenario,
        String nmCenario,
        String tpDia,
        Integer nrHoraInicio,
        Integer nrHoraFim) {
}
