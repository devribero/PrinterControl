import PageHeader from "../../components/PageHeader";
import NetworkView from "../../components/NetworkView";

/**
 * Rota "/network" — Mapeamento de Rede.
 *
 * Visível a qualquer sessão: ver quais Print Servers existem e quais
 * impressoras pertencem a cada um é leitura. As ações que tocam o Print
 * Server (Descobrir) ou o banco (Sincronizar) são de admin e ficam
 * escondidas para os demais papéis — o backend também as recusa (403).
 */
export default function NetworkPage() {
  return (
    <>
      <PageHeader
        section="Monitoramento"
        title="Mapeamento de rede"
        subtitle="Print Servers registrados, descoberta de filas e sincronização do cadastro."
      />

      <NetworkView />
    </>
  );
}
