package br.com.pharos.controller;

import br.com.pharos.dominio.Cenario;
import br.com.pharos.dominio.FonteDados;
import br.com.pharos.dominio.TipoOcorrencia;
import br.com.pharos.servico.ApoioService;
import java.util.List;
import java.util.Map;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

/** Rotas de apoio ao front e verificação de saúde (usada também para validar o deploy). */
@RestController
public class ApoioController {

    private final ApoioService service;

    public ApoioController(ApoioService service) {
        this.service = service;
    }

    @GetMapping("/cenarios")
    public List<Cenario> cenarios() {
        return service.listarCenarios();
    }

    @GetMapping("/fontes")
    public List<FonteDados> fontes() {
        return service.listarFontes();
    }

    @GetMapping("/tipos-ocorrencia")
    public List<TipoOcorrencia> tiposOcorrencia() {
        return service.listarTiposOcorrencia();
    }

    @GetMapping("/saude")
    public ResponseEntity<Map<String, String>> saude() {
        boolean banco = service.bancoDisponivel();
        Map<String, String> corpo = Map.of("api", "UP", "banco", banco ? "UP" : "DOWN");
        return banco ? ResponseEntity.ok(corpo) : ResponseEntity.status(503).body(corpo);
    }
}
