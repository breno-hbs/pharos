package br.com.pharos.dominio;

import java.util.List;

/** Resposta de GET /trajetos: par consultado, cenário e alternativas ordenadas pelo critério. */
public record TrajetoResposta(
        Long idParOd,
        String stResultado,
        String mensagem,
        Cenario cenario,
        Parada origem,
        Parada destino,
        String criterioOrdenacao,
        List<AlternativaDetalhe> alternativas) {
}
