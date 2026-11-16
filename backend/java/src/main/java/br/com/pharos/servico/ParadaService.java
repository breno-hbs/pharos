package br.com.pharos.servico;

import br.com.pharos.dominio.Parada;
import br.com.pharos.excecao.RecursoNaoEncontradoException;
import br.com.pharos.excecao.RegraNegocioException;
import br.com.pharos.infraestrutura.ParadaDAO;
import java.util.List;
import java.util.Set;
import org.springframework.stereotype.Service;

/** Regras de negócio (BO) do cadastro de paradas. */
@Service
public class ParadaService {

    private static final Set<String> SIM_NAO = Set.of("S", "N");

    private final ParadaDAO dao;

    public ParadaService(ParadaDAO dao) {
        this.dao = dao;
    }

    public List<Parada> listar(String selecionavel) {
        String filtro = selecionavel == null || selecionavel.isBlank()
                ? null
                : Validacao.dominio(selecionavel, "selecionavel", SIM_NAO, null);
        return dao.listar(filtro);
    }

    public Parada buscar(long id) {
        return dao.buscarPorId(id)
                .orElseThrow(() -> new RecursoNaoEncontradoException("Parada " + id + " não encontrada."));
    }

    public Parada cadastrar(Parada entrada) {
        Parada valida = validar(entrada);
        long id = dao.inserir(valida);
        return buscar(id);
    }

    public Parada atualizar(long id, Parada entrada) {
        Parada valida = validar(entrada);
        if (!dao.atualizar(id, valida)) {
            throw new RecursoNaoEncontradoException("Parada " + id + " não encontrada.");
        }
        return buscar(id);
    }

    public void excluir(long id) {
        if (!dao.excluir(id)) {
            throw new RecursoNaoEncontradoException("Parada " + id + " não encontrada.");
        }
    }

    Parada validar(Parada p) {
        if (p == null) {
            throw new RegraNegocioException("Corpo da requisição ausente.");
        }
        String codigo = Validacao.texto(p.cdParadaGtfs(), "cdParadaGtfs", 20);
        String nome = Validacao.texto(p.nmParada(), "nmParada", 150);
        String municipio = Validacao.texto(p.nmMunicipio(), "nmMunicipio", 60);
        String terminal = Validacao.dominio(p.flTerminal(), "flTerminal", SIM_NAO, "N");
        String selecionavel = Validacao.dominio(p.flSelecionavel(), "flSelecionavel", SIM_NAO, "N");
        long fonte = Validacao.idPositivo(p.idFonte(), "idFonte");

        Double lat = p.nrLatitude();
        Double lon = p.nrLongitude();
        if ((lat == null) != (lon == null)) {
            throw new RegraNegocioException("Informe latitude e longitude juntas ou nenhuma das duas.");
        }
        if (lat != null && (lat < -90 || lat > 90)) {
            throw new RegraNegocioException("A latitude deve estar entre -90 e 90.");
        }
        if (lon != null && (lon < -180 || lon > 180)) {
            throw new RegraNegocioException("A longitude deve estar entre -180 e 180.");
        }
        return new Parada(p.idParada(), codigo, nome, municipio, lat, lon, terminal, selecionavel, fonte);
    }
}
