"use server";

import fs from "fs/promises";
import path from "path";

export async function getChangelogAction() {
  try {
    const changelogPath = path.join(process.cwd(), "..", "CHANGELOG.md");
    // On essaie aussi le chemin local si on est dans le dossier frontend au build
    try {
      return await fs.readFile(changelogPath, "utf-8");
    } catch {
      const fallbackPath = path.join(process.cwd(), "CHANGELOG.md");
      return await fs.readFile(fallbackPath, "utf-8");
    }
  } catch (error) {
    console.error("Error reading changelog:", error);
    return "# Changelog non disponible";
  }
}
