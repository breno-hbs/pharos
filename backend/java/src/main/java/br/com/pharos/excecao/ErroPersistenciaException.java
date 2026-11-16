package br.com.pharos.excecao;

/** Falha inesperada no acesso ao Oracle: resulta em HTTP 500 (sem expor detalhes internos). */
public class ErroPersistenciaException extends RuntimeException {
    public ErroPersistenciaException(String mensagem, Throwable causa) {
        super(mensagem, causa);
    }
}
