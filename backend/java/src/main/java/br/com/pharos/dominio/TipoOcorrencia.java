package br.com.pharos.dominio;

/** Tabela PH_TIPO_OCORRENCIA: categorias de ocorrência adotadas pela equipe. */
public record TipoOcorrencia(
        Long idTipoOcorrencia,
        String cdTipo,
        String nmTipo,
        String dsTipo) {
}
