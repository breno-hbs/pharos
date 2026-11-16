package br.com.pharos.servico;

import br.com.pharos.dominio.Consulta;
import br.com.pharos.dominio.ConsultaAtualizacao;
import br.com.pharos.excecao.RecursoNaoEncontradoException;
import br.com.pharos.excecao.RegraNegocioException;
import br.com.pharos.infraestrutura.ConsultaDAO;
import br.com.pharos.infraestrutura.TrajetoDAO;
import java.util.List;
import java.util.Set;
import org.springframework.stereotype.Service;

/** Regras de negócio (BO) do registro anônimo de consultas. */
@Service
public class ConsultaService {

    private static final Set<String> SIM_NAO = Set.of("S", "N");

    private final ConsultaDAO consultaDAO;
    private final TrajetoDAO trajetoDAO;

    public ConsultaService(ConsultaDAO consultaDAO, TrajetoDAO trajetoDAO) {
        this.consultaDAO = consultaDAO;
        this.trajetoDAO = trajetoDAO;
    }

    public List<Consulta> listar() {
        return consultaDAO.listarRecentes();
    }

    public Consulta buscar(long id) {
        return consultaDAO.buscarPorId(id)
                .orElseThrow(() -> new RecursoNaoEncontradoException("Consulta " + id + " não encontrada."));
    }

    public Consulta cadastrar(Consulta entrada) {
        if (entrada == null) {
            throw new RegraNegocioException("Corpo da requisição ausente.");
        }
        long idPar = Validacao.idPositivo(entrada.idParOd(), "idParOd");
        trajetoDAO.buscarParPorId(idPar)
                .orElseThrow(() -> new RecursoNaoEncontradoException("Par origem-destino " + idPar
                        + " não encontrado."));
        String criterio = Validacao.dominio(entrada.tpCriterioOrdenacao(), "tpCriterioOrdenacao",
                TrajetoService.CRITERIOS, null);
        Integer tempo = entrada.nrTempoRespostaMs();
        if (tempo != null && tempo < 0) {
            throw new RegraNegocioException("O tempo de resposta não pode ser negativo.");
        }
        validarAvaliacao(entrada.nrAvaliacao());
        validarAlternativa(entrada.idAlternativaEscolhida(), idPar);
        String teste = Validacao.dominio(entrada.flTeste(), "flTeste", SIM_NAO, "N");

        Consulta nova = new Consulta(null, idPar, entrada.idAlternativaEscolhida(), criterio, null, tempo,
                entrada.nrAvaliacao(), teste);
        long id = consultaDAO.inserir(nova);
        return buscar(id);
    }

    public Consulta atualizar(long id, ConsultaAtualizacao entrada) {
        if (entrada == null) {
            throw new RegraNegocioException("Corpo da requisição ausente.");
        }
        Consulta atual = buscar(id);
        validarAvaliacao(entrada.nrAvaliacao());
        validarAlternativa(entrada.idAlternativaEscolhida(), atual.idParOd());
        if (!consultaDAO.atualizar(id, entrada.idAlternativaEscolhida(), entrada.nrAvaliacao())) {
            throw new RecursoNaoEncontradoException("Consulta " + id + " não encontrada.");
        }
        return buscar(id);
    }

    public void excluir(long id) {
        if (!consultaDAO.excluir(id)) {
            throw new RecursoNaoEncontradoException("Consulta " + id + " não encontrada.");
        }
    }

    private void validarAvaliacao(Integer avaliacao) {
        if (avaliacao != null && (avaliacao < 1 || avaliacao > 5)) {
            throw new RegraNegocioException("A avaliação deve ser um número de 1 a 5.");
        }
    }

    private void validarAlternativa(Long idAlternativa, long idPar) {
        if (idAlternativa != null && !trajetoDAO.alternativaPertenceAoPar(idAlternativa, idPar)) {
            throw new RegraNegocioException("A alternativa escolhida não pertence ao par origem-destino consultado.");
        }
    }
}
