package br.com.pharos.dominio;

/** Corpo do PUT /consultas/{id}: alternativa escolhida e avaliação de utilidade (1 a 5). */
public record ConsultaAtualizacao(
        Long idAlternativaEscolhida,
        Integer nrAvaliacao) {
}
