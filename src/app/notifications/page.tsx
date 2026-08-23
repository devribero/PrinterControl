import { Bell } from "lucide-react";
import ComingSoon from "../../components/ComingSoon";
import RequireRole from "../../components/RequireRole";

export default function NotificationsPage() {
  return (
    <RequireRole role="admin">
      <ComingSoon icon={Bell} title="Notificações" description="Preferências de alerta por e-mail e Teams chegam em breve." />
    </RequireRole>
  );
}
