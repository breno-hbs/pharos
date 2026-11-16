package br.com.pharos.dominio;

/** Indicador histórico agregado com tipo e fonte, indicando se o dado é simulado. */
public record IndicadorDetalhe(
        Long idIndicador,
        String cdTipo,
        String nmTipo,
        Integer nrAno,
        String tpFaixaHoraria,
        Integer nrRaioM,
        Integer qtOcorrencias,
        String nmFonte,
        boolean simulado) {
}
