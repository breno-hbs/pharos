package br.com.pharos.dominio;

/** Tabela PH_INDICADOR_OCORRENCIA: contagem histórica agregada de ocorrências por alternativa. */
public record IndicadorOcorrencia(
        Long idIndicador,
        Long idAlternativa,
        Long idTipoOcorrencia,
        Long idFonte,
        Integer nrAno,
        String tpFaixaHoraria,
        Integer nrRaioM,
        Integer qtOcorrencias) {
}
