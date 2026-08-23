"use client";

import type { ReactNode } from "react";
import { ShieldAlert } from "lucide-react";
import { useAppData } from "../lib/app-data";
import { ROLE_LABELS, type Role } from "../lib/permissions";
import styles from "./RequireRole.module.css";

/**
 * Envolve uma área que só faz sentido para determinado papel. Quem não tem o
 * papel vê uma explicação em vez do conteúdo.
 *
 * Isto é experiência de uso, não autorização: qualquer dado sensível continua
 * protegido pelas dependências do backend (`require_admin` e cia.). O objetivo
 * é não levar o usuário a uma tela cujas ações voltariam 403.
 */
export default function RequireRole({ role, children }: { role: Role; children: ReactNode }) {
  const { account, can } = useAppData();

  const allowed = role === "admin" ? can.canAdmin : role === "operator" ? can.canOperate : can.canView;
  if (allowed) return <>{children}</>;

  return (
    <div className={styles.wrap}>
      <div className={styles.iconWrap}>
        <ShieldAlert size={26} />
      </div>
      <h2 className={styles.title}>Acesso restrito</h2>
      <p className={styles.text}>
        Esta área é exclusiva para o perfil <strong>{ROLE_LABELS[role]}</strong>.
        {account ? ` Sua conta tem o perfil ${ROLE_LABELS[account.role]}.` : ""}
      </p>
      <p className={styles.hint}>Peça a um administrador se precisar deste acesso.</p>
    </div>
  );
}
