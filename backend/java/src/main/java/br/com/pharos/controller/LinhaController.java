package br.com.pharos.controller;

import br.com.pharos.dominio.Linha;
import br.com.pharos.servico.LinhaService;
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
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/linhas")
public class LinhaController {

    private final LinhaService service;

    public LinhaController(LinhaService service) {
        this.service = service;
    }

    @GetMapping
    public List<Linha> listar() {
        return service.listar();
    }

    @GetMapping("/{id}")
    public Linha buscar(@PathVariable long id) {
        return service.buscar(id);
    }

    @PostMapping
    public ResponseEntity<Linha> cadastrar(@RequestBody Linha linha) {
        Linha criada = service.cadastrar(linha);
        return ResponseEntity.created(URI.create("/linhas/" + criada.idLinha())).body(criada);
    }

    @PutMapping("/{id}")
    public Linha atualizar(@PathVariable long id, @RequestBody Linha linha) {
        return service.atualizar(id, linha);
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> excluir(@PathVariable long id) {
        service.excluir(id);
        return ResponseEntity.noContent().build();
    }
}
