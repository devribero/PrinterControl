import PageHeader from "../../components/PageHeader";
import RequireRole from "../../components/RequireRole";
import UnitsView from "../../components/UnitsView";

/**
 * Rota "/units" — Unidades. Somente admin: criar unidades, apontar o
 * webhook do Teams de cada uma e ver quantos servidores e usuarios ela tem.
 * A associacao de servidores fica no Mapeamento de rede e a de usuarios em
 * Usuarios, onde cada um ja e editado.
 */
export default function UnitsPage() {
  return (
    <RequireRole role="admin">
      <PageHeader
        section="Administração"
        title="Unidades"
        subtitle="Agrupam Print Servers e usuários. Definem o filtro inicial do painel e o canal de alertas de cada região."
      />

      <UnitsView />
    </RequireRole>
  );
}
