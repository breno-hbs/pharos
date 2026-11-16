package br.com.pharos.controller;

import br.com.pharos.dominio.TrajetoResposta;
import br.com.pharos.servico.TrajetoService;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/trajetos")
public class TrajetoController {

    private final TrajetoService service;

    public TrajetoController(TrajetoService service) {
        this.service = service;
    }

    /**
     * Ex.: GET /trajetos?origem=1&destino=2&cenario=UTIL_PICO_MANHA&ordenar=TEMPO
     * ou   GET /trajetos?origem=1&destino=2&dia=UTIL&hora=7
     */
    @GetMapping
    public TrajetoResposta consultar(@RequestParam Long origem,
                                     @RequestParam Long destino,
                                     @RequestParam(required = false) String cenario,
                                     @RequestParam(required = false) String dia,
                                     @RequestParam(required = false) Integer hora,
                                     @RequestParam(required = false) String ordenar) {
        return service.consultar(origem, destino, cenario, dia, hora, ordenar);
    }
}
