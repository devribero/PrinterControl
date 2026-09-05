import { Plug } from "lucide-react";
import PageHeader from "../../components/PageHeader";
import ComingSoon from "../../components/ComingSoon";
import RequireRole from "../../components/RequireRole";

export default function IntegrationsPage() {
  return (
    <RequireRole role="admin">
      <PageHeader
        section="Administração"
        title="Integrações"
        subtitle="Conexão do painel com outras ferramentas corporativas."
      />

      <ComingSoon
        icon={Plug}
        title="Integrações"
        description="Conexão do painel com outras ferramentas corporativas. Em desenvolvimento."
      />
    </RequireRole>
  );
}
