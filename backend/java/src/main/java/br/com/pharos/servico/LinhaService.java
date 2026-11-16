package br.com.pharos.servico;

import br.com.pharos.dominio.Linha;
import br.com.pharos.excecao.RecursoNaoEncontradoException;
import br.com.pharos.excecao.RegraNegocioException;
import br.com.pharos.infraestrutura.LinhaDAO;
import java.util.List;
import java.util.Set;
import org.springframework.stereotype.Service;

/** Regras de negócio (BO) do cadastro de linhas. */
@Service
public class LinhaService {

    private static final Set<String> MODAIS = Set.of("ONIBUS", "METRO", "TREM");

    private final LinhaDAO dao;

    public LinhaService(LinhaDAO dao) {
        this.dao = dao;
    }

    public List<Linha> listar() {
        return dao.listar();
    }

    public Linha buscar(long id) {
        return dao.buscarPorId(id)
                .orElseThrow(() -> new RecursoNaoEncontradoException("Linha " + id + " não encontrada."));
    }

    public Linha cadastrar(Linha entrada) {
        Linha valida = validar(entrada);
        long id = dao.inserir(valida);
        return buscar(id);
    }

    public Linha atualizar(long id, Linha entrada) {
        Linha valida = validar(entrada);
        if (!dao.atualizar(id, valida)) {
            throw new RecursoNaoEncontradoException("Linha " + id + " não encontrada.");
        }
        return buscar(id);
    }

    public void excluir(long id) {
        if (!dao.excluir(id)) {
            throw new RecursoNaoEncontradoException("Linha " + id + " não encontrada.");
        }
    }

    Linha validar(Linha l) {
        if (l == null) {
            throw new RegraNegocioException("Corpo da requisição ausente.");
        }
        String codigo = Validacao.texto(l.cdLinha(), "cdLinha", 20);
        String itinerario = Validacao.texto(l.dsItinerario(), "dsItinerario", 300);
        String modal = Validacao.dominio(l.tpModal(), "tpModal", MODAIS, "ONIBUS");
        long fonte = Validacao.idPositivo(l.idFonte(), "idFonte");
        return new Linha(l.idLinha(), codigo, itinerario, modal, fonte);
    }
}
