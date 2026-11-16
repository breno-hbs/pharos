package br.com.pharos.dominio;

/** Tabela PH_PARADA: paradas e terminais da rede piloto (vértices do grafo). */
public record Parada(
        Long idParada,
        String cdParadaGtfs,
        String nmParada,
        String nmMunicipio,
        Double nrLatitude,
        Double nrLongitude,
        String flTerminal,
        String flSelecionavel,
        Long idFonte) {
}
