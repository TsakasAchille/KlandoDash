import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

/**
 * Format date in French locale
 */
export function formatDate(dateString: string): string {
  if (!dateString) return "-";
  const date = new Date(dateString);
  return date.toLocaleDateString("fr-FR", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

/**
 * Format distance in km
 */
export function formatDistance(km: number): string {
  if (!km && km !== 0) return "-";
  return `${km.toFixed(1)} km`;
}

/**
 * Format price in XOF
 */
export function formatPrice(amount: number): string {
  if (!amount && amount !== 0) return "-";
  return new Intl.NumberFormat("fr-FR").format(amount) + " XOF";
}
