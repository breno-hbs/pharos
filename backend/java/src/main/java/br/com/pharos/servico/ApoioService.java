package br.com.pharos.servico;

import br.com.pharos.dominio.Cenario;
import br.com.pharos.dominio.FonteDados;
import br.com.pharos.dominio.TipoOcorrencia;
import br.com.pharos.infraestrutura.ApoioDAO;
import java.util.List;
import org.springframework.stereotype.Service;

/** Consultas de apoio ao front: cenários, fontes de dados, tipos de ocorrência e saúde do banco. */
@Service
public class ApoioService {

    private final ApoioDAO dao;

    public ApoioService(ApoioDAO dao) {
        this.dao = dao;
    }

    public List<Cenario> listarCenarios() {
        return dao.listarCenarios();
    }

    public List<FonteDados> listarFontes() {
        return dao.listarFontes();
    }

    public List<TipoOcorrencia> listarTiposOcorrencia() {
        return dao.listarTiposOcorrencia();
    }

    public boolean bancoDisponivel() {
        return dao.bancoDisponivel();
    }
}
