"use client";

import Image from "next/image";

export function Logo({ size = "medium" }: { size?: "small" | "medium" | "large" | "xlarge" }) {
  const sizeClasses = {
    small: "w-24",
    medium: "w-32", 
    large: "w-40",
    xlarge: "w-44"
  };

  return (
    <div className={sizeClasses[size] + " relative"}>
      <Image
        src="/logo-klando-sans-fond.png"
        alt="Klando"
        width={400}
        height={150}
        className="w-full h-auto object-contain"
        priority={true}
        unoptimized
        sizes="(max-width: 768px) 100vw, 300px"
      />
      {/* Fallback au cas où l'image Next.js a un souci de chargement initial sur certains devices */}
      <noscript>
        <img src="/logo-klando-sans-fond.png" alt="Klando" className="w-full h-auto" />
      </noscript>
    </div>
  );
}
