import type { ReactNode } from "react";
import styles from "./PageHeader.module.css";

interface PageHeaderProps {
  section: string;
  title: string;
  subtitle?: string;
  actions?: ReactNode;
}

export default function PageHeader({ section, title, subtitle, actions }: PageHeaderProps) {
  return (
    <div className={styles.header}>
      <div className={styles.titleBlock}>
        <span className={styles.accentBar} aria-hidden="true" />
        <div>
          <div className={styles.crumb}>
            <span>{section}</span>
            <span className={styles.crumbSep}>/</span>
            <span className={styles.crumbCurrent}>{title}</span>
          </div>
          <h1 className={styles.title}>{title}</h1>
          {subtitle && <p className={styles.subtitle}>{subtitle}</p>}
        </div>
      </div>
      {actions && <div className={styles.actions}>{actions}</div>}
    </div>
  );
}
