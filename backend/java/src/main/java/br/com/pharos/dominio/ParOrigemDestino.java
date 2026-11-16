package br.com.pharos.dominio;

import java.time.LocalDateTime;

/** Tabela PH_PAR_ORIGEM_DESTINO: par origem-destino já calculado para um cenário. */
public record ParOrigemDestino(
        Long idParOd,
        Long idCenario,
        Long idParadaOrigem,
        Long idParadaDestino,
        String stResultado,
        LocalDateTime dtCalculo,
        Long idFonte) {
}
