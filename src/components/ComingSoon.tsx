// Dependência externa: só o tipo LucideIcon (lucide-react), para tipar o
// ícone recebido por prop. Aviso inline de seção ainda não implementada.
//
// O handoff (`PrinterControl v2.dc.html` L899-907) é explícito em não usar um
// herói centralizado aqui: é uma linha discreta, do tamanho do conteúdo que
// ela anuncia.
import type { LucideIcon } from "lucide-react";
import styles from "./ComingSoon.module.css";

interface ComingSoonProps {
  icon: LucideIcon;
  title: string;
  description: string;
}

export default function ComingSoon({ icon: Icon, title, description }: ComingSoonProps) {
  return (
    <div className={styles.notice}>
      <span className={styles.icon}>
        <Icon size={20} />
      </span>
      <div className={styles.body}>
        <h2 className={styles.title}>{title}</h2>
        <p className={styles.description}>{description}</p>
      </div>
    </div>
  );
}
