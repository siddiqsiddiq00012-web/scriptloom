import { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import "./BillingPage.css";
import {
  Check,
  X,
  Crown,
  CreditCard,
  Activity,
  History,
  ArrowLeft,
  Loader2,
  AlertTriangle,
  ShieldCheck,
  Zap,
  Download,
  FileText,
  Sparkles,
} from "lucide-react";
import {
  getPlans,
  getSubscription,
  getUsage,
  getProviderStatus,
  createCheckoutSession,
  cancelSubscription,
  getInvoices,
  formatPrice,
  formatStorage,
  formatMinutes,
} from "../../api/billing";

function UsageBar({ label, used, limit, accent }) {
  const unlimited = limit === -1 || limit === undefined || limit === null;
  const pct = !unlimited && limit > 0 ? Math.min(100, (used / limit) * 100) : 0;
  const nearLimit = !unlimited && pct >= 80;

  return (
    <div className="billing__usageRow">
      <div className="billing__usageHeader">
        <span className="billing__usageLabel">{label}</span>
        <span className="billing__usageValues">
          {unlimited ? (
            "Unlimited"
          ) : (
            <>
              <strong>{used}</strong> / {limit}
            </>
          )}
        </span>
      </div>
      {!unlimited && (
        <div className="billing__usageTrack">
          <div
            className={`billing__usageFill ${nearLimit ? "billing__usageFill--warn" : ""}`}
            style={{ width: `${pct}%`, background: accent }}
          />
        </div>
      )}
      {nearLimit && (
        <div className="billing__usageWarning">
          <AlertTriangle size={13} />
          {pct >= 100 ? "Limit reached — upgrade to continue using this feature." : "Almost at your limit — consider upgrading."}
        </div>
      )}
    </div>
  );
}

function PlanCard({ plan, currentPlanKey, paymentsConfigured, onUpgrade, busy }) {
  const isCurrent = plan.key === currentPlanKey;
  const isPro = plan.key === "pro";
  const priceMonthly = formatPrice(plan.price_monthly_cents, plan.currency);
  const priceAnnual = formatPrice(plan.price_annual_cents, plan.currency);
  const annualNote = plan.price_annual_cents > 0 && plan.price_monthly_cents > 0
    ? Math.round((1 - plan.price_annual_cents / (plan.price_monthly_cents * 12)) * 100)
    : 0;

  return (
    <div className={`billing__planCard ${isPro ? "billing__planCard--featured" : ""} ${isCurrent ? "billing__planCard--current" : ""}`}>
      {isPro && <div className="billing__planBadge"><Sparkles size={12} /> MOST POPULAR</div>}
      <h3 className="billing__planName">{plan.name}</h3>
      <p className="billing__planDesc">{plan.description}</p>

      <div className="billing__planPrice">
        <span className="billing__priceAmount">{priceMonthly}</span>
        <span className="billing__pricePeriod">/ month</span>
      </div>
      {annualNote > 0 && (
        <p className="billing__planAnnual">
          or {priceAnnual}/year ({annualNote}% off)
        </p>
      )}

      <div className="billing__planLimits">
        <div className="billing__planLimitRow">
          <span>Projects</span>
          <strong>{plan.limits.max_projects === -1 ? "Unlimited" : plan.limits.max_projects}</strong>
        </div>
        <div className="billing__planLimitRow">
          <span>Media uploads / mo</span>
          <strong>{plan.limits.max_media_uploads === -1 ? "Unlimited" : plan.limits.max_media_uploads}</strong>
        </div>
        <div className="billing__planLimitRow">
          <span>Processing / mo</span>
          <strong>{formatMinutes(plan.limits.max_processing_minutes)}</strong>
        </div>
        <div className="billing__planLimitRow">
          <span>AI generations / mo</span>
          <strong>{plan.limits.max_ai_generations === -1 ? "Unlimited" : plan.limits.max_ai_generations}</strong>
        </div>
        <div className="billing__planLimitRow">
          <span>Storage</span>
          <strong>{plan.limits.max_storage_gb === -1 ? "Unlimited" : `${plan.limits.max_storage_gb} GB`}</strong>
        </div>
      </div>

      <ul className="billing__planFeatures">
        {Object.entries(plan.tier_features || {})
          .filter(([, v]) => v)
          .map(([key]) => (
            <li key={key}><Check size={14} /> {key.replace(/_/g, " ")}</li>
          ))}
        {Object.entries(plan.features || {})
          .filter(([, v]) => v)
          .filter(([k]) => !["project_management", "media_upload", "export", "creator_intelligence_basic"].includes(k))
          .map(([key]) => (
            <li key={key}><Check size={14} /> {key.replace(/_/g, " ")}</li>
          ))}
      </ul>

      <div className="billing__planAction">
        {isCurrent ? (
          <button className="btn billing__btnCurrent" disabled>
            <Check size={15} /> Current Plan
          </button>
        ) : plan.key === "enterprise" ? (
          <a className="btn btn-primary billing__btnContact" href="mailto:support@scriptloom.com?subject=Enterprise%20Plan%20Inquiry">
            Contact Sales
          </a>
        ) : !paymentsConfigured ? (
          <button className="btn billing__btnDisabled" disabled>
            Payments not configured
          </button>
        ) : (
          <button className={`btn btn-primary ${isPro ? "billing__btnUpgrade" : ""}`} onClick={() => onUpgrade(plan)} disabled={busy}>
            {busy ? <><Loader2 className="lucide-spin" size={15} /> Starting...</> : <>Upgrade to {plan.name.replace(" Plan", "")}</>}
          </button>
        )}
      </div>
    </div>
  );
}

export default function BillingPage({ onShowToast }) {
  const navigate = useNavigate();
  const [tab, setTab] = useState("overview");
  const [plans, setPlans] = useState([]);
  const [subscription, setSubscription] = useState(null);
  const [usage, setUsage] = useState(null);
  const [invoices, setInvoices] = useState([]);
  const [provider, setProvider] = useState(null);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [cancelConfirm, setCancelConfirm] = useState(false);

  const loadAll = useCallback(async () => {
    try {
      const [plansData, subData, usageData, providerData, invoicesData] = await Promise.all([
        getPlans(),
        getSubscription(),
        getUsage(),
        getProviderStatus(),
        getInvoices(20),
      ]);
      setPlans(plansData || []);
      setSubscription(subData);
      setUsage(usageData);
      setProvider(providerData);
      setInvoices(invoicesData || []);
    } catch (err) {
      if (onShowToast) onShowToast("Failed to load billing information.");
    } finally {
      setLoading(false);
    }
  }, [onShowToast]);

  useEffect(() => { loadAll(); }, [loadAll]);

  const handleUpgrade = async (plan) => {
    setBusy(true);
    try {
      const result = await createCheckoutSession({
        plan_key: plan.key,
        billing_cycle: "monthly",
      });
      if (result?.url) {
        window.location.href = result.url;
      } else if (onShowToast) {
        onShowToast("Checkout session could not be created.");
      }
    } catch (err) {
      if (onShowToast) onShowToast(err.message || "Failed to start checkout.");
    } finally {
      setBusy(false);
    }
  };

  const handleCancel = async () => {
    setBusy(true);
    try {
      await cancelSubscription({ immediately: false });
      if (onShowToast) onShowToast("Subscription will be cancelled at the end of the billing period.");
      setCancelConfirm(false);
      await loadAll();
    } catch (err) {
      if (onShowToast) onShowToast(err.message || "Failed to cancel subscription.");
    } finally {
      setBusy(false);
    }
  };

  if (loading) {
    return (
      <div className="billing__loading">
        <Loader2 className="lucide-spin" size={24} /> Loading billing...
      </div>
    );
  }

  const currentPlanKey = subscription?.plan_key || "free";
  const isFree = currentPlanKey === "free";
  const paymentsConfigured = provider?.is_configured === true;

  return (
    <div className="billingPage">
      <div className="billing__header">
        <div>
          <h2 className="billing__title">Billing & Plan</h2>
          <p className="billing__subtitle">Manage your subscription, usage, and billing history.</p>
        </div>
        <button className="btn btn-ghost" onClick={() => navigate("/dashboard")}>
          <ArrowLeft size={15} /> Back to Dashboard
        </button>
      </div>

      {!paymentsConfigured && (
        <div className="billing__notice">
          <AlertTriangle size={16} />
          <div>
            <strong>Payments are not configured.</strong>
            <p>Live checkout is disabled on this deployment. Your Free plan and all current features continue to work normally.</p>
          </div>
        </div>
      )}

      <div className="billing__tabs">
        <button className={`billing__tab ${tab === "overview" ? "billing__tab--active" : ""}`} onClick={() => setTab("overview")}>
          <Crown size={15} /> Subscription
        </button>
        <button className={`billing__tab ${tab === "usage" ? "billing__tab--active" : ""}`} onClick={() => setTab("usage")}>
          <Activity size={15} /> Usage
        </button>
        <button className={`billing__tab ${tab === "plans" ? "billing__tab--active" : ""}`} onClick={() => setTab("plans")}>
          <CreditCard size={15} /> Plans & Pricing
        </button>
        <button className={`billing__tab ${tab === "history" ? "billing__tab--active" : ""}`} onClick={() => setTab("history")}>
          <History size={15} /> Billing History
        </button>
      </div>

      {tab === "overview" && (
        <div className="billing__overview">
          <div className="billing__currentCard">
            <div className="billing__currentIcon"><Crown size={22} color="#F59E0B" /></div>
            <div className="billing__currentInfo">
              <span className="billing__currentLabel">Current Plan</span>
              <h3>{subscription?.plan_display_name || subscription?.plan_name || "Free Plan"}</h3>
              <p>
                Status: <strong>{subscription?.status}</strong>
                {subscription?.billing_cycle && ` · ${subscription.billing_cycle} billing`}
              </p>
            </div>
            <div className="billing__currentActions">
              {!isFree && (
                <>
                  {cancelConfirm ? (
                    <div className="billing__cancelConfirm">
                      <p>Cancel at end of period? You keep access until the period ends.</p>
                      <div>
                        <button className="btn btn--danger btn-sm" onClick={handleCancel} disabled={busy}>
                          {busy ? <Loader2 className="lucide-spin" size={14} /> : "Confirm Cancel"}
                        </button>
                        <button className="btn btn-ghost btn-sm" onClick={() => setCancelConfirm(false)}>Keep Plan</button>
                      </div>
                    </div>
                  ) : (
                    <button className="btn btn-ghost btn-sm billing__btnCancel" onClick={() => setCancelConfirm(true)}>
                      Cancel subscription
                    </button>
                  )}
                </>
              )}
              {isFree && paymentsConfigured && (
                <button className="btn btn-primary" onClick={() => setTab("plans")}>
                  Upgrade Plan
                </button>
              )}
              {isFree && !paymentsConfigured && (
                <span className="billing__freeBadge"><ShieldCheck size={14} /> Free plan active</span>
              )}
            </div>
          </div>

          {usage && (
            <div className="billing__usageCard">
              <h3 className="billing__sectionTitle">This Period's Usage</h3>
              <p className="billing__periodNote">Billing period: {usage.period_month}</p>
              <UsageBar
                label="Media Uploads"
                used={usage.media_uploads?.used ?? 0}
                limit={usage.media_uploads?.limit}
                accent="var(--primary)"
              />
              <UsageBar
                label="Processing (minutes)"
                used={usage.processing_minutes?.used ?? 0}
                limit={usage.processing_minutes?.limit}
                accent="var(--accent-purple)"
              />
              <UsageBar
                label="AI Generations"
                used={usage.ai_generations?.used ?? 0}
                limit={usage.ai_generations?.limit}
                accent="var(--accent-cyan)"
              />
              <UsageBar
                label="Storage"
                used={usage.storage?.used_gb ?? 0}
                limit={usage.storage?.limit_gb}
                accent="var(--accent-green)"
              />
            </div>
          )}

          <div className="billing__featuresCard">
            <h3 className="billing__sectionTitle">Plan Features</h3>
            <div className="billing__featureGrid">
              {[
                ["Priority processing", usage?.features?.priority_processing],
                ["Advanced Creator Intelligence", usage?.features?.creator_intelligence_advanced],
                ["API access", usage?.features?.api_access],
                ["Team workspaces", usage?.features?.team_workspaces],
              ].map(([label, enabled]) => (
                <div key={label} className={`billing__featureItem ${enabled ? "" : "billing__featureItem--off"}`}>
                  {enabled ? <Check size={14} color="var(--accent-green)" /> : <X size={14} />}
                  <span>{label}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {tab === "usage" && (
        <div className="billing__usageTab">
          <div className="billing__usageGrid">
            <div className="billing__usageCard">
              <div className="billing__usageCardHeader">
                <FileText size={16} color="var(--primary)" />
                <span>Media Uploads</span>
              </div>
              <p className="billing__usageBig">{usage?.media_uploads?.used ?? 0}<small> / {usage?.media_uploads?.limit === -1 ? "∞" : usage?.media_uploads?.limit}</small></p>
              <p className="billing__usageSmall">uploads this month</p>
            </div>
            <div className="billing__usageCard">
              <div className="billing__usageCardHeader">
                <Zap size={16} color="var(--accent-purple)" />
                <span>Processing</span>
              </div>
              <p className="billing__usageBig">{usage?.processing_minutes?.used ?? 0}<small> / {usage?.processing_minutes?.limit === -1 ? "∞" : usage?.processing_minutes?.limit}</small></p>
              <p className="billing__usageSmall">minutes this month</p>
            </div>
            <div className="billing__usageCard">
              <div className="billing__usageCardHeader">
                <Sparkles size={16} color="var(--accent-cyan)" />
                <span>AI Generations</span>
              </div>
              <p className="billing__usageBig">{usage?.ai_generations?.used ?? 0}<small> / {usage?.ai_generations?.limit === -1 ? "∞" : usage?.ai_generations?.limit}</small></p>
              <p className="billing__usageSmall">AI outputs this month</p>
            </div>
            <div className="billing__usageCard">
              <div className="billing__usageCardHeader">
                <Download size={16} color="var(--accent-green)" />
                <span>Storage</span>
              </div>
              <p className="billing__usageBig">{usage?.storage?.used_gb ?? 0}<small> GB / {usage?.storage?.limit_gb === -1 ? "∞" : `${usage?.storage?.limit_gb} GB`}</small></p>
              <p className="billing__usageSmall">media stored</p>
            </div>
          </div>
        </div>
      )}

      {tab === "plans" && (
        <div className="billing__plansTab">
          <div className="billing__plansGrid">
            {plans.map((plan) => (
              <PlanCard
                key={plan.key}
                plan={plan}
                currentPlanKey={currentPlanKey}
                paymentsConfigured={paymentsConfigured}
                onUpgrade={handleUpgrade}
                busy={busy}
              />
            ))}
          </div>
          <p className="billing__plansNote">
            Prices are configurable by the Scriptloom team without code changes. Enterprise pricing is custom — contact support@scriptloom.com.
          </p>
        </div>
      )}

      {tab === "history" && (
        <div className="billing__historyTab">
          <h3 className="billing__sectionTitle">Billing History</h3>
          {invoices.length === 0 ? (
            <div className="billing__empty">
              <History size={28} />
              <p>No invoices yet. Invoices appear here after your first payment.</p>
            </div>
          ) : (
            <table className="billing__invoicesTable">
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Invoice</th>
                  <th>Amount</th>
                  <th>Status</th>
                  <th>Receipt</th>
                </tr>
              </thead>
              <tbody>
                {invoices.map((inv) => (
                  <tr key={inv.id}>
                    <td>{new Date(inv.created_at).toLocaleDateString()}</td>
                    <td className="billing__invoiceId">{inv.provider_invoice_id}</td>
                    <td>{formatPrice(inv.amount_cents, inv.currency)}</td>
                    <td>
                      <span className={`billing__status billing__status--${inv.status}`}>{inv.status}</span>
                    </td>
                    <td>
                      {inv.invoice_url ? (
                        <a href={inv.invoice_url} target="_blank" rel="noreferrer" className="billing__receiptLink">
                          <Download size={14} /> View
                        </a>
                      ) : (
                        "—"
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}
    </div>
  );
}
