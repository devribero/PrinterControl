import PageHeader from "../../components/PageHeader";
import SettingsView from "../../components/SettingsView";

/**
 * Rota "/settings" — Configurações.
 *
 * Sem RequireRole: todo papel acessa as PRÓPRIAS preferências (perfil,
 * senha, tema, acessibilidade) e as informações do sistema, que são só de
 * leitura. O que é administrativo aparece apenas para `can.canAdmin` (dentro
 * do SettingsView) e não edita nada crítico — só aponta para /users, /units
 * e /network, onde as ações vivem e o backend as autoriza.
 */
export default function SettingsPage() {
  return (
    <>
      <PageHeader
        section="Administração"
        title="Configurações"
        subtitle="Sua conta, preferências deste dispositivo e informações do sistema."
      />

      <SettingsView />
    </>
  );
}
