import "./Analytics.css";
import { TrendingUp, Eye, Clock } from "lucide-react";

function Analytics() {
  const stats = [
    {
      icon: <TrendingUp size={18} />,
      label: "Growth",
      value: "+248%",
    },
    {
      icon: <Eye size={18} />,
      label: "Views",
      value: "1.2M",
    },
    {
      icon: <Clock size={18} />,
      label: "Saved",
      value: "18 hrs",
    },
  ];

  return (
    <div className="analytics">

      <h3>Performance</h3>

      <div className="analytics__grid">
        {stats.map((item) => (
          <div className="analytics__card" key={item.label}>

            <div className="analytics__icon">
              {item.icon}
            </div>

            <div className="analytics__value">
              {item.value}
            </div>

            <div className="analytics__label">
              {item.label}
            </div>

          </div>
        ))}
      </div>

    </div>
  );
}

export default Analytics;