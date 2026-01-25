"use client";

import Image from "next/image";

export function Logo({ size = "medium" }: { size?: "small" | "medium" | "large" | "xlarge" }) {
  const sizeClasses = {
    small: "w-8 h-8",
    medium: "w-12 h-12", 
    large: "w-16 h-16",
    xlarge: "w-[400px] h-[150px]"
  };

  return (
    <div className={sizeClasses[size]} style={{ padding: 0, margin: 0, lineHeight: 0 }}>
      <Image
        src="/logo-klando-sans-fond.png"
        alt="Klando"
        width={400}
        height={150}
        className="w-full h-full object-contain"
        priority
      />
    </div>
  );
}
