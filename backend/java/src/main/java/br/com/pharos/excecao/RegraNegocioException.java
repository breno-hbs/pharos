package br.com.pharos.excecao;

/** Dado inválido ou regra de negócio violada: resulta em HTTP 400. */
public class RegraNegocioException extends RuntimeException {
    public RegraNegocioException(String mensagem) {
        super(mensagem);
    }
}
