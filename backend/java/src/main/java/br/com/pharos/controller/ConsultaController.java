package br.com.pharos.controller;

import br.com.pharos.dominio.Consulta;
import br.com.pharos.dominio.ConsultaAtualizacao;
import br.com.pharos.servico.ConsultaService;
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
@RequestMapping("/consultas")
public class ConsultaController {

    private final ConsultaService service;

    public ConsultaController(ConsultaService service) {
        this.service = service;
    }

    @GetMapping
    public List<Consulta> listar() {
        return service.listar();
    }

    @GetMapping("/{id}")
    public Consulta buscar(@PathVariable long id) {
        return service.buscar(id);
    }

    @PostMapping
    public ResponseEntity<Consulta> cadastrar(@RequestBody Consulta consulta) {
        Consulta criada = service.cadastrar(consulta);
        return ResponseEntity.created(URI.create("/consultas/" + criada.idConsulta())).body(criada);
    }

    @PutMapping("/{id}")
    public Consulta atualizar(@PathVariable long id, @RequestBody ConsultaAtualizacao atualizacao) {
        return service.atualizar(id, atualizacao);
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> excluir(@PathVariable long id) {
        service.excluir(id);
        return ResponseEntity.noContent().build();
    }
}
