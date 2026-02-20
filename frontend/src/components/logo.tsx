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
    <div className={sizeClasses[size]}>
      <Image
        src="/logo-klando-sans-fond.png"
        alt="Klando"
        width={400}
        height={150}
        className="w-full h-auto object-contain"
        priority
        unoptimized
        sizes="(max-width: 768px) 100vw, 300px"
      />
    </div>
  );
}
