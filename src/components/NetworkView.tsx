"use client";

/**
 * Mapeamento de Rede (rota "/network") — orquestra os blocos de
 * `components/network/`:
 *
 *   ServerGrid        -> escopos (Todos, cada Print Server, Sem servidor);
 *                        selecionar é a ação principal, o resto fica no
 *                        menu "⋯" de cada cartão (admin).
 *   SyncPanel         -> andamento/resultado de "Sincronizar agora".
 *   DiscoveryPanel    -> andamento/resultado de "Descobrir filas".
 *   ScopePrinterTable -> impressoras cadastradas no escopo.
 *   DriversCard       -> drivers em uso nas filas ativas do escopo.
 *
 * Servidores reais sincronizam sozinhos (backend: ao cadastrar e a cada
 * 6 h), então Descobrir e Sincronizar são ações secundárias. As duas rodam
 * em segundo plano: o estado vive nos hooks abaixo, não nos painéis, e o
 * usuário pode trocar de escopo enquanto uma descoberta lenta termina.
 *
 * A lista de servidores e o escopo NÃO são estado desta tela: vivem no
 * AppDataProvider, porque o mesmo escopo manda no painel inteiro.
 */
import { useMemo, useState } from "react";
import { useAppData } from "../lib/app-data";
import type { PrintServer } from "../types";
import DiscoveryPanel from "./network/DiscoveryPanel";
import DriversCard from "./network/DriversCard";
import ScopePrinterTable from "./network/ScopePrinterTable";
import SelectedServerNotice from "./network/SelectedServerNotice";
import type { ServerAction } from "./network/ServerActionsMenu";
import { DeleteServerModal, SyncConfirmModal, ToggleServerModal } from "./network/ServerConfirmModals";
import ServerFormModal from "./network/ServerFormModal";
import ServerGrid from "./network/ServerGrid";
import SyncPanel from "./network/SyncPanel";
import { useAutoSyncWatcher } from "./network/useAutoSyncWatcher";
import { useServerDiscovery } from "./network/useServerDiscovery";
import { useServerSync } from "./network/useServerSync";
import shared from "./network/shared.module.css";

/** Diálogo aberto no momento; um por vez. `server: null` em "form" = criar. */
type Dialog =
  | { kind: "form"; server: PrintServer | null }
  | { kind: "toggle" | "delete" | "sync"; server: PrintServer }
  | null;

export default function NetworkView() {
  const {
    can,
    printers,
    usingRealData,
    servers,
    serversLoading,
    serversError,
    refreshServers,
    serverScope,
    setServerScope,
    serverCounts,
    allActiveCount,
    units,
    scopeUnit,
  } = useAppData();

  const discovery = useServerDiscovery();
  const sync = useServerSync();
  useAutoSyncWatcher();

  const [dialog, setDialog] = useState<Dialog>(null);
  const closeDialog = () => setDialog(null);

  const selected = useMemo(() => servers.find((s) => s.host === serverScope) ?? null, [servers, serverScope]);

  /** Só aparece quando existe: cadastro à mão é exceção, não categoria fixa. */
  const semServidor = serverCounts[""] ?? 0;

  function handleAction(action: ServerAction, server: PrintServer) {
    switch (action) {
      case "edit":
        setDialog({ kind: "form", server });
        break;
      case "discover":
        // Seleciona o servidor para o resultado aparecer no contexto dele.
        setServerScope(server.host);
        void discovery.start(server);
        break;
      case "sync":
        setDialog({ kind: "sync", server });
        break;
      case "toggle":
        setDialog({ kind: "toggle", server });
        break;
      case "delete":
        setDialog({ kind: "delete", server });
        break;
    }
  }

  function confirmarSync(server: PrintServer) {
    setServerScope(server.host);
    void sync.start(server);
  }

  const discoveryJob = discovery.job;
  const discoveryServer = discoveryJob ? (servers.find((s) => s.id === discoveryJob.serverId) ?? null) : null;

  const scopeLabel = selected ? ` de ${selected.host}` : scopeUnit ? ` da unidade ${scopeUnit.name}` : "";

  return (
    <div className={shared.page}>
      <ServerGrid
        servers={servers}
        loading={serversLoading}
        error={serversError}
        serverScope={serverScope}
        canAdmin={can.canAdmin}
        allActiveCount={allActiveCount}
        unassignedCount={semServidor}
        onSelect={setServerScope}
        onRefresh={() => void refreshServers()}
        onCreate={() => setDialog({ kind: "form", server: null })}
        onAction={handleAction}
        discoveringServerId={discovery.running && discoveryJob ? discoveryJob.serverId : null}
        syncingServerId={sync.running && sync.job ? sync.job.serverId : null}
      />

      {selected && <SelectedServerNotice server={selected} canAdmin={can.canAdmin} />}

      {sync.job && <SyncPanel key={sync.job.id} job={sync.job} onDismiss={sync.dismiss} />}

      {discoveryJob && (
        <DiscoveryPanel
          key={discoveryJob.id}
          job={discoveryJob}
          isCurrent={selected?.id === discoveryJob.serverId}
          canRetry={discoveryServer?.active === true}
          onShow={() => setServerScope(discoveryJob.host)}
          onRetry={() => {
            if (discoveryServer) void discovery.start(discoveryServer);
          }}
          onDismiss={discovery.dismiss}
        />
      )}

      {servers.length > 0 && (
        <ScopePrinterTable
          printers={printers}
          selected={selected}
          serverScope={serverScope}
          scopeUnit={scopeUnit}
          usingRealData={usingRealData}
        />
      )}

      {servers.length > 0 && <DriversCard printers={printers} scopeLabel={scopeLabel} />}

      {/* Diálogos: montados só enquanto abertos, com key estável — o estado
          de cada formulário mora dentro dele (ver ServerFormModal). */}
      {dialog?.kind === "form" && (
        <ServerFormModal
          key={dialog.server?.id ?? "novo"}
          server={dialog.server}
          units={units}
          onClose={closeDialog}
        />
      )}
      {dialog?.kind === "toggle" && (
        <ToggleServerModal key={dialog.server.id} server={dialog.server} onClose={closeDialog} />
      )}
      {dialog?.kind === "delete" && (
        <DeleteServerModal key={dialog.server.id} server={dialog.server} onClose={closeDialog} />
      )}
      {dialog?.kind === "sync" && (
        <SyncConfirmModal
          key={dialog.server.id}
          server={dialog.server}
          onClose={closeDialog}
          onConfirm={confirmarSync}
        />
      )}
    </div>
  );
}
