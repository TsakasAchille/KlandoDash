/**
 * Parses @email mentions from a text string.
 */
export function parseMentions(text: string): string[] {
  const mentionRegex = /@([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})/g;
  const matches = Array.from(text.matchAll(mentionRegex), match => match[1]);
  return Array.from(new Set(matches)); // Unique emails
}
