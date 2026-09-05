import PageHeader from "../../components/PageHeader";
import RequireRole from "../../components/RequireRole";
import UsersView from "../../components/UsersView";

export default function UsersPage() {
  return (
    <RequireRole role="admin">
      <PageHeader
        section="Administração"
        title="Usuários"
        subtitle="Contas do painel, perfis de acesso e estado de ativação."
      />

      <UsersView />
    </RequireRole>
  );
}
