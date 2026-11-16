package br.com.pharos.dominio;

import java.util.List;

/** Par origem-destino calculado junto com suas alternativas (resultado da leitura no banco). */
public record ParComAlternativas(
        ParOrigemDestino par,
        List<AlternativaDetalhe> alternativas) {
}
