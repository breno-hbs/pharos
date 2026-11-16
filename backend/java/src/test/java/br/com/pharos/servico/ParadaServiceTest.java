package br.com.pharos.servico;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import br.com.pharos.dominio.Parada;
import br.com.pharos.excecao.RecursoNaoEncontradoException;
import br.com.pharos.excecao.RegraNegocioException;
import br.com.pharos.infraestrutura.ParadaDAO;
import java.util.Optional;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

@ExtendWith(MockitoExtension.class)
class ParadaServiceTest {

    @Mock
    ParadaDAO dao;

    private Parada valida() {
        return new Parada(null, "407", "Terminal Capão Redondo", "São Paulo", null, null, null, null, 1000L);
    }

    @Test
    void cadastraParadaValidaAplicandoPadroesNosFlags() {
        ParadaService service = new ParadaService(dao);
        Parada gravada = new Parada(1000L, "407", "Terminal Capão Redondo", "São Paulo", null, null, "N", "N", 1000L);
        when(dao.inserir(any(Parada.class))).thenReturn(1000L);
        when(dao.buscarPorId(1000L)).thenReturn(Optional.of(gravada));

        Parada resultado = service.cadastrar(valida());

        assertEquals(1000L, resultado.idParada());
        assertEquals("N", resultado.flTerminal());
    }

    @Test
    void rejeitaNomeVazio() {
        ParadaService service = new ParadaService(dao);
        Parada invalida = new Parada(null, "407", " ", "São Paulo", null, null, "N", "N", 1000L);

        assertThrows(RegraNegocioException.class, () -> service.cadastrar(invalida));
        verify(dao, never()).inserir(any());
    }

    @Test
    void rejeitaLatitudeSemLongitude() {
        ParadaService service = new ParadaService(dao);
        Parada invalida = new Parada(null, "407", "Terminal", "São Paulo", -23.7, null, "N", "N", 1000L);

        assertThrows(RegraNegocioException.class, () -> service.cadastrar(invalida));
    }

    @Test
    void rejeitaFlagForaDoDominio() {
        ParadaService service = new ParadaService(dao);
        Parada invalida = new Parada(null, "407", "Terminal", "São Paulo", null, null, "X", "N", 1000L);

        assertThrows(RegraNegocioException.class, () -> service.cadastrar(invalida));
    }

    @Test
    void buscarInexistenteLancaNaoEncontrado() {
        ParadaService service = new ParadaService(dao);
        when(dao.buscarPorId(9L)).thenReturn(Optional.empty());

        assertThrows(RecursoNaoEncontradoException.class, () -> service.buscar(9L));
    }

    @Test
    void excluirInexistenteLancaNaoEncontrado() {
        ParadaService service = new ParadaService(dao);
        when(dao.excluir(9L)).thenReturn(false);

        assertThrows(RecursoNaoEncontradoException.class, () -> service.excluir(9L));
    }
}
