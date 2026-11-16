package br.com.pharos.dominio;

/** Tabela PH_ALTERNATIVA: alternativa de deslocamento de um par origem-destino. */
public record Alternativa(
        Long idAlternativa,
        Long idParOd,
        Integer nrOrdem,
        Double nrTempoTotalMin,
        Double nrDistanciaKm,
        Integer qtBaldeacoes) {
}
