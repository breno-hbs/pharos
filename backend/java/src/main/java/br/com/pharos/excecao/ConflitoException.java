package br.com.pharos.excecao;

/** Conflito com o estado do banco (duplicidade, registro em uso): resulta em HTTP 409. */
public class ConflitoException extends RuntimeException {
    public ConflitoException(String mensagem) {
        super(mensagem);
    }
}
