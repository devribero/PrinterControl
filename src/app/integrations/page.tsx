import { Plug } from "lucide-react";
import ComingSoon from "../../components/ComingSoon";
import RequireRole from "../../components/RequireRole";

export default function IntegrationsPage() {
  return (
    <RequireRole role="admin">
      <ComingSoon icon={Plug} title="Integrações" description="Conecte o painel a outras ferramentas em breve." />
    </RequireRole>
  );
}
