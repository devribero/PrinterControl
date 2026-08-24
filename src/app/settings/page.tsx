import SettingsView from "../../components/SettingsView";

/**
 * Rota "/settings" — Configurações.
 *
 * Sem RequireRole, e a remoção é o ponto da Fase 8: a página estava restrita
 * a admin desde quando era um placeholder de "preferências gerais". Isso
 * deixava viewer e operator sem acesso às PRÓPRIAS preferências — perfil,
 * senha, tema e acessibilidade.
 *
 * O que é administrativo continua protegido em dois níveis: a seção de
 * Administração só é renderizada para `can.canAdmin` (dentro do
 * SettingsView) e não edita nada crítico — apenas aponta para /users e
 * /network, onde as ações vivem e o backend as autoriza.
 */
export default function SettingsPage() {
  return <SettingsView />;
}
