package br.com.pharos.dominio;

/** Tabela PH_ETAPA_TRAJETO: linha, parada de embarque e de desembarque de cada etapa. */
public record EtapaTrajeto(
        Long idEtapa,
        Long idAlternativa,
        Integer nrSequencia,
        Long idLinha,
        Long idParadaEmbarque,
        Long idParadaDesembarque) {
}
