package br.com.pharos.dominio;

/** Etapa de uma alternativa já com o código da linha e os nomes das paradas, para exibição. */
public record EtapaDetalhe(
        Long idEtapa,
        Integer nrSequencia,
        Long idLinha,
        String cdLinha,
        Long idParadaEmbarque,
        String nmParadaEmbarque,
        Long idParadaDesembarque,
        String nmParadaDesembarque) {
}
