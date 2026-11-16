package br.com.pharos.excecao;

import java.time.LocalDateTime;

/** Formato padrão de todas as respostas de erro da API. */
public record ErroResposta(
        LocalDateTime timestamp,
        int status,
        String erro,
        String mensagem,
        String caminho) {
}
