package br.com.pharos.servico;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.when;

import br.com.pharos.dominio.Cenario;
import br.com.pharos.dominio.Parada;
import br.com.pharos.dominio.TrajetoResposta;
import br.com.pharos.excecao.RegraNegocioException;
import br.com.pharos.infraestrutura.ApoioDAO;
import br.com.pharos.infraestrutura.ParadaDAO;
import br.com.pharos.infraestrutura.TrajetoDAO;
import java.util.Optional;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

@ExtendWith(MockitoExtension.class)
class TrajetoServiceTest {

    @Mock
    TrajetoDAO trajetoDAO;
    @Mock
    ParadaDAO paradaDAO;
    @Mock
    ApoioDAO apoioDAO;

    private Parada parada(long id) {
        return new Parada(id, "P" + id, "Parada " + id, "São Paulo", null, null, "N", "S", 1L);
    }

    @Test
    void origemIgualAoDestinoEhRejeitada() {
        TrajetoService service = new TrajetoService(trajetoDAO, paradaDAO, apoioDAO);

        assertThrows(RegraNegocioException.class, () -> service.consultar(1L, 1L, "X", null, null, null));
    }

    @Test
    void cenarioSemParesRetornaSemDadosEmVezDeErro() {
        TrajetoService service = new TrajetoService(trajetoDAO, paradaDAO, apoioDAO);
        Cenario cenario = new Cenario(2L, "UTIL_TARDE", "Dia útil, tarde", "UTIL", 12, 18);
        when(apoioDAO.buscarCenarioPorCodigo("UTIL_TARDE")).thenReturn(Optional.of(cenario));
        when(paradaDAO.buscarPorId(1L)).thenReturn(Optional.of(parada(1)));
        when(paradaDAO.buscarPorId(2L)).thenReturn(Optional.of(parada(2)));
        when(trajetoDAO.buscarCompleto(2L, 1L, 2L)).thenReturn(Optional.empty());

        TrajetoResposta resposta = service.consultar(1L, 2L, "UTIL_TARDE", null, null, null);

        assertEquals("SEM_DADOS", resposta.stResultado());
        assertTrue(resposta.alternativas().isEmpty());
    }

    @Test
    void horarioSemCenarioCadastradoRetornaSemDados() {
        TrajetoService service = new TrajetoService(trajetoDAO, paradaDAO, apoioDAO);
        when(apoioDAO.buscarCenarioPorHorario("DOMINGO", 3)).thenReturn(Optional.empty());
        when(paradaDAO.buscarPorId(1L)).thenReturn(Optional.of(parada(1)));
        when(paradaDAO.buscarPorId(2L)).thenReturn(Optional.of(parada(2)));

        TrajetoResposta resposta = service.consultar(1L, 2L, null, "domingo", 3, null);

        assertEquals("SEM_DADOS", resposta.stResultado());
    }
}
