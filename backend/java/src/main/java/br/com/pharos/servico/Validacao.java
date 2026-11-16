package br.com.pharos.servico;

import br.com.pharos.excecao.RegraNegocioException;
import java.util.Set;

/** Regras de validação reutilizadas pela camada de negócio (BO). */
final class Validacao {

    private Validacao() {
    }

    static String texto(String valor, String campo, int max) {
        if (valor == null || valor.isBlank()) {
            throw new RegraNegocioException("O campo '" + campo + "' é obrigatório.");
        }
        String limpo = valor.trim();
        if (limpo.length() > max) {
            throw new RegraNegocioException("O campo '" + campo + "' aceita no máximo " + max + " caracteres.");
        }
        return limpo;
    }

    /** Aceita apenas valores do conjunto (sem diferenciar maiúsculas); null/vazio vira o padrão. */
    static String dominio(String valor, String campo, Set<String> permitidos, String padrao) {
        if (valor == null || valor.isBlank()) {
            if (padrao == null) {
                throw new RegraNegocioException("O campo '" + campo + "' é obrigatório.");
            }
            return padrao;
        }
        String normal = valor.trim().toUpperCase();
        if (!permitidos.contains(normal)) {
            throw new RegraNegocioException("Valor inválido para '" + campo + "'. Permitidos: "
                    + String.join(", ", permitidos.stream().sorted().toList()) + ".");
        }
        return normal;
    }

    static long idPositivo(Long valor, String campo) {
        if (valor == null || valor <= 0) {
            throw new RegraNegocioException("O campo '" + campo + "' é obrigatório e deve ser maior que zero.");
        }
        return valor;
    }
}
