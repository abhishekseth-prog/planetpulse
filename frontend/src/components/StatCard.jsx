function StatCard({ label, icon, value, unit, footer, variant = "", iconClass = "", valueClass = "", children }) {
  return (
    <article className={`stat-card ${variant}`}>
      <div className="stat-head">
        <span>{label}</span>
        <span className={`stat-icon ${iconClass}`}>{icon}</span>
      </div>
      <div className={`stat-number ${valueClass}`}>
        {value}{unit && <small>{unit}</small>}
      </div>
      {children}
      {footer && <div className="stat-foot">{footer}</div>}
      {variant.includes("stat-total") && <div className="stat-orbit" aria-hidden="true"/>}
    </article>
  );
}

export default StatCard;
