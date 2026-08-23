import NotificationsView from "../../components/NotificationsView";

/**
 * Rota "/notifications" — caixa pessoal de notificações.
 *
 * Sem RequireRole, e isso é deliberado: até a Fase 7 esta rota era um
 * placeholder de "preferências de alerta" e estava restrita a admin. Agora
 * ela é a caixa de mensagens de QUEM ESTÁ LOGADO — todo papel tem uma, e o
 * backend já garante o escopo (só devolve as notificações da própria sessão,
 * sem aceitar parâmetro de destinatário).
 *
 * O que continua restrito a admin é ENVIAR, e essa checagem fica dentro do
 * NotificationsView, junto do botão — o backend recusa com 403 de qualquer
 * forma.
 */
export default function NotificationsPage() {
  return <NotificationsView />;
}
