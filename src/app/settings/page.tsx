import { Settings } from "lucide-react";
import ComingSoon from "../../components/ComingSoon";
import RequireRole from "../../components/RequireRole";

export default function SettingsPage() {
  return (
    <RequireRole role="admin">
      <ComingSoon icon={Settings} title="Configurações" description="Preferências gerais do painel chegam em breve." />
    </RequireRole>
  );
}
