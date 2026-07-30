import "./PlatformIcons.css";

import {
  Youtube,
  Instagram,
  Music2,
  Facebook,
  Twitch,
} from "lucide-react";

function PlatformIcons() {
  const platforms = [
    {
      icon: <Youtube size={22} />,
      name: "YouTube",
    },
    {
      icon: <Instagram size={22} />,
      name: "Instagram",
    },
    {
      icon: <Music2 size={22} />,
      name: "TikTok",
    },
    {
      icon: <Facebook size={22} />,
      name: "Facebook",
    },
    {
      icon: <Twitch size={22} />,
      name: "Twitch",
    },
  ];

  return (
    <div className="platforms">

      <h3>Export Platforms</h3>

      <div className="platforms__grid">
        {platforms.map((platform) => (
          <div
            className="platforms__item"
            key={platform.name}
          >
            <div className="platforms__icon">
              {platform.icon}
            </div>

            <span>{platform.name}</span>
          </div>
        ))}
      </div>

    </div>
  );
}

export default PlatformIcons;