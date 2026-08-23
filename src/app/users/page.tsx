import RequireRole from "../../components/RequireRole";
import UsersView from "../../components/UsersView";

export default function UsersPage() {
  return (
    <RequireRole role="admin">
      <UsersView />
    </RequireRole>
  );
}
