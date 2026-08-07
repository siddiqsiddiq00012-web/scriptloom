export default function EmptyState({ icon: Icon, title, description, action, secondaryAction }) {
  return (
    <div className="empty-state">
      {Icon && (
        <div className="empty-state__icon">
          <Icon size={32} color="var(--primary)" />
        </div>
      )}
      <h3 className="empty-state__title">{title}</h3>
      {description && <p className="empty-state__desc">{description}</p>}
      {action && <div style={{ marginTop: "8px" }}>{action}</div>}
      {secondaryAction && <div style={{ marginTop: "4px" }}>{secondaryAction}</div>}
    </div>
  );
}
