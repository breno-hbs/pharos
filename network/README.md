# Network Architect

Rede simulada no Cisco Packet Tracer para o espaço físico da solução PHAROS (CitizenTech): sub-redes, VLANs, roteamento inter-VLAN, DHCP, NAT/PAT, DNS, HTTP e controles de segurança.

## Arquivos

| Arquivo | O que é |
| --- | --- |
| `Pharos_Network_final.pkt` | Simulação final, para abrir no Cisco Packet Tracer |
| `PHAROS_Network_Architect.pdf` | Relatório da entrega (11 páginas): ficha da CitizenTech, topologia, endereçamento, configurações, testes com evidências e mapa de conferência |

## Resumo

- Faixa `192.168.10.0/24` dividida em três sub-redes `/26`: Equipe (VLAN 10), Cidadão/Wi-Fi (VLAN 20) e Servidores/Sensores (VLAN 30).
- O servidor PHAROS fica em `192.168.10.130` e publica a página com a Ficha da CitizenTech (HTTP, com nome resolvido por DNS).
- Internet simulada em `198.51.100.0/24`, com NAT/PAT na saída.
- Os comandos e os testes (ping entre VLANs, DNS, HTTP e bloqueios) estão nas seções 4 e 5 do PDF.

## Como abrir

1. Abra o `.pkt` no Cisco Packet Tracer.
2. Em um PC da rede, abra o navegador do desktop e acesse o endereço da Ficha descrito na seção 5 do PDF.

Entrega da disciplina: o `.pkt` e o PDF são enviados no Teams ou no Portal do Aluno, uma vez por equipe.
