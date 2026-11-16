package br.com.pharos.dominio;

import java.util.List;

/** Alternativa de trajeto com etapas e indicadores históricos agregados. */
public record AlternativaDetalhe(
        Alternativa alternativa,
        List<EtapaDetalhe> etapas,
        List<IndicadorDetalhe> indicadores,
        int totalOcorrencias) {
}
