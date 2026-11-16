package br.com.pharos.controller;

import br.com.pharos.dominio.Parada;
import br.com.pharos.servico.ParadaService;
import java.net.URI;
import java.util.List;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/paradas")
public class ParadaController {

    private final ParadaService service;

    public ParadaController(ParadaService service) {
        this.service = service;
    }

    @GetMapping
    public List<Parada> listar(@RequestParam(required = false) String selecionavel) {
        return service.listar(selecionavel);
    }

    @GetMapping("/{id}")
    public Parada buscar(@PathVariable long id) {
        return service.buscar(id);
    }

    @PostMapping
    public ResponseEntity<Parada> cadastrar(@RequestBody Parada parada) {
        Parada criada = service.cadastrar(parada);
        return ResponseEntity.created(URI.create("/paradas/" + criada.idParada())).body(criada);
    }

    @PutMapping("/{id}")
    public Parada atualizar(@PathVariable long id, @RequestBody Parada parada) {
        return service.atualizar(id, parada);
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> excluir(@PathVariable long id) {
        service.excluir(id);
        return ResponseEntity.noContent().build();
    }
}
