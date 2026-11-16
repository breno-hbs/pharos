package br.com.pharos.dominio;

/** Tabela PH_LINHA: linhas de transporte da rede piloto. */
public record Linha(
        Long idLinha,
        String cdLinha,
        String dsItinerario,
        String tpModal,
        Long idFonte) {
}
