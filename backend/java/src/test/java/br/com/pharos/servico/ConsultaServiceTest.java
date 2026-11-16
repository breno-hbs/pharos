package br.com.pharos.servico;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyLong;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import br.com.pharos.dominio.Consulta;
import br.com.pharos.dominio.ConsultaAtualizacao;
import br.com.pharos.dominio.ParOrigemDestino;
import br.com.pharos.excecao.RecursoNaoEncontradoException;
import br.com.pharos.excecao.RegraNegocioException;
import br.com.pharos.infraestrutura.ConsultaDAO;
import br.com.pharos.infraestrutura.TrajetoDAO;
import java.time.LocalDateTime;
import java.util.Optional;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

@ExtendWith(MockitoExtension.class)
class ConsultaServiceTest {

    @Mock
    ConsultaDAO consultaDAO;
    @Mock
    TrajetoDAO trajetoDAO;

    private ParOrigemDestino par() {
        return new ParOrigemDestino(5L, 1L, 10L, 20L, "COM_ALTERNATIVAS", LocalDateTime.now(), 1L);
    }

    @Test
    void cadastraConsultaValida() {
        ConsultaService service = new ConsultaService(consultaDAO, trajetoDAO);
        Consulta gravada = new Consulta(100L, 5L, null, "TEMPO", LocalDateTime.now(), 120, null, "N");
        when(trajetoDAO.buscarParPorId(5L)).thenReturn(Optional.of(par()));
        when(consultaDAO.inserir(any(Consulta.class))).thenReturn(100L);
        when(consultaDAO.buscarPorId(100L)).thenReturn(Optional.of(gravada));

        Consulta resultado = service.cadastrar(new Consulta(null, 5L, null, "tempo", null, 120, null, null));

        assertEquals(100L, resultado.idConsulta());
        assertEquals("TEMPO", resultado.tpCriterioOrdenacao());
    }

    @Test
    void rejeitaCriterioInvalido() {
        ConsultaService service = new ConsultaService(consultaDAO, trajetoDAO);
        when(trajetoDAO.buscarParPorId(5L)).thenReturn(Optional.of(par()));

        assertThrows(RegraNegocioException.class,
                () -> service.cadastrar(new Consulta(null, 5L, null, "PRECO", null, null, null, null)));
        verify(consultaDAO, never()).inserir(any());
    }

    @Test
    void rejeitaParInexistente() {
        ConsultaService service = new ConsultaService(consultaDAO, trajetoDAO);
        when(trajetoDAO.buscarParPorId(5L)).thenReturn(Optional.empty());

        assertThrows(RecursoNaoEncontradoException.class,
                () -> service.cadastrar(new Consulta(null, 5L, null, "TEMPO", null, null, null, null)));
    }

    @Test
    void rejeitaAvaliacaoForaDoIntervalo() {
        ConsultaService service = new ConsultaService(consultaDAO, trajetoDAO);
        Consulta atual = new Consulta(100L, 5L, null, "TEMPO", LocalDateTime.now(), null, null, "N");
        when(consultaDAO.buscarPorId(100L)).thenReturn(Optional.of(atual));

        assertThrows(RegraNegocioException.class,
                () -> service.atualizar(100L, new ConsultaAtualizacao(null, 6)));
        verify(consultaDAO, never()).atualizar(anyLong(), any(), any());
    }

    @Test
    void rejeitaAlternativaDeOutroPar() {
        ConsultaService service = new ConsultaService(consultaDAO, trajetoDAO);
        Consulta atual = new Consulta(100L, 5L, null, "TEMPO", LocalDateTime.now(), null, null, "N");
        when(consultaDAO.buscarPorId(100L)).thenReturn(Optional.of(atual));
        when(trajetoDAO.alternativaPertenceAoPar(77L, 5L)).thenReturn(false);

        assertThrows(RegraNegocioException.class,
                () -> service.atualizar(100L, new ConsultaAtualizacao(77L, 4)));
    }
}
