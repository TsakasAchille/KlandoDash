import React from 'react';
import Link from 'next/link';

/**
 * Utility to convert text patterns (TRIP-ID, TICKET-ID) into clickable Next.js links.
 */
export function linkify(text: string): React.ReactNode[] {
  // Regex for TRIP-XXXX and TICKET-XXXX (flexible on numbers/chars)
  const regex = /(TRIP-[A-Z0-9-]+|TICKET-[A-Z0-9-]+)/gi;
  
  const parts = text.split(regex);
  
  return parts.map((part, i) => {
    if (part.match(/TRIP-/i)) {
      return (
        <Link 
          key={i} 
          href={`/trips?id=${part.toUpperCase()}`} 
          className="text-white underline decoration-white/30 hover:decoration-white font-black bg-white/10 px-1.5 py-0.5 rounded"
        >
          {part.toUpperCase()}
        </Link>
      );
    }
    
    if (part.match(/TICKET-/i)) {
      return (
        <Link 
          key={i} 
          href={`/support?id=${part.toUpperCase()}`} 
          className="text-white underline decoration-white/30 hover:decoration-white font-black bg-white/10 px-1.5 py-0.5 rounded"
        >
          {part.toUpperCase()}
        </Link>
      );
    }
    
    return <React.Fragment key={i}>{part}</React.Fragment>;
  });
}
