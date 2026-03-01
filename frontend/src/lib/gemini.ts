import { GoogleGenerativeAI } from "@google/generative-ai";

/**
 * Interface pour le rapport d'analyse de document
 */
export interface DocumentAnalysisReport {
  documentType: 'ID_CARD' | 'DRIVER_LICENSE' | 'UNKNOWN';
  isSenegalese: boolean;
  isLegible: boolean;
  documentNumber: string | null;
  expirationDate: string | null;
  fullName: string | null;
  nameMatchesProfile?: boolean;
  confidenceScore: number; // 0-100
  summary: string;
  warnings: string[];
}

/**
 * Assistant général Klando (Texte)
 */
// eslint-disable-next-line @typescript-eslint/no-explicit-any
export async function askKlandoAI(prompt: string, dataContext: any) {
  const apiKey = process.env.GOOGLE_GEMINI_API_KEY;
  if (!apiKey) throw new Error("Clé API Gemini manquante");

  const genAI = new GoogleGenerativeAI(apiKey);
  const fullPrompt = `Tu es l'assistant de Klando (covoiturage au Sénégal). Analyse ces données : ${JSON.stringify(dataContext)}\n\nQuestion : ${prompt}\nRéponds en français, de manière courte et efficace.`;
  
  const modelsToTry = ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"];
  let lastError = "";

  for (const modelName of modelsToTry) {
    try {
      const model = genAI.getGenerativeModel({ model: modelName });
      const result = await model.generateContent(fullPrompt);
      const text = result.response.text();
      if (text) return text;
    } catch (error: any) {
      lastError = error.message;
      if (lastError.includes("API_KEY_INVALID") || lastError.includes("429")) throw error;
      continue; 
    }
  }
  throw new Error(`Tous les modèles ont échoué: ${lastError}`);
}

/**
 * Analyse un document (ID ou Permis) à partir de son URL via Vision
 */
export async function analyzeDocument(imageUrl: string, type: 'ID_CARD' | 'DRIVER_LICENSE', expectedName?: string | null): Promise<DocumentAnalysisReport> {
  const apiKey = process.env.GOOGLE_GEMINI_API_KEY;
  if (!apiKey) throw new Error("Clé API Gemini manquante");

  const genAI = new GoogleGenerativeAI(apiKey);
  
  // Noms de modèles à tester par ordre de performance
  const modelsToTry = [
    "gemini-2.0-flash-exp", 
    "gemini-2.0-flash",
    "gemini-1.5-flash",
    "gemini-1.5-pro"
  ];
  
  let lastError = null;

  for (const modelName of modelsToTry) {
    try {
      console.log(`[AI-DEBUG] Essai avec modèle : ${modelName}`);
      const model = genAI.getGenerativeModel({ model: modelName });

      // 1. Récupération de l'image
      const response = await fetch(imageUrl);
      if (!response.ok) throw new Error(`Erreur HTTP image: ${response.status}`);
      
      let contentType = response.headers.get("content-type") || "image/jpeg";
      
      // FIX: Si le type est générique, on force image/jpeg pour que Gemini accepte
      if (contentType === "application/octet-stream" || !contentType.startsWith("image/")) {
          contentType = "image/jpeg";
      }

      const buffer = await response.arrayBuffer();
      const base64Data = Buffer.from(buffer).toString("base64");

      const prompt = `
        ANALYSE DE DOCUMENT D'IDENTITÉ SÉNÉGALAIS
        Type demandé: ${type === 'ID_CARD' ? "Carte Nationale d'Identité" : "Permis de conduire"}
        Nom du profil à comparer: "${expectedName || 'Inconnu'}"

        EXTRAIS LES INFORMATIONS SUIVANTES EN JSON STRICT :
        {
          "documentType": "${type}",
          "isSenegalese": boolean (mentions République du Sénégal ?),
          "isLegible": boolean (image assez nette ?),
          "documentNumber": "string (le numéro officiel sans espaces)",
          "expirationDate": "YYYY-MM-DD (format ISO)",
          "fullName": "LE NOM COMPLET EN MAJUSCULES",
          "nameMatchesProfile": boolean (correspond à ${expectedName || 'Inconnu'} ?),
          "confidenceScore": number (0-100),
          "summary": "Résumé français en 1 phrase",
          "warnings": ["ex: Document expiré", "ex: Image floue"]
        }
      `;

      const result = await model.generateContent([
        {
          inlineData: {
            data: base64Data,
            mimeType: contentType
          }
        },
        prompt
      ]);

      const text = result.response.text();
      const jsonMatch = text.match(/\{[\s\S]*\}/);
      if (!jsonMatch) throw new Error("Format JSON non trouvé");

      const data = JSON.parse(jsonMatch[0]);
      
      // Sécurité date
      if (data.expirationDate && !/^\d{4}-\d{2}-\d{2}$/.test(data.expirationDate)) {
          data.expirationDate = null;
      }

      console.log(`[AI-SUCCESS] Document lu avec ${modelName} : ${data.fullName}`);
      return data as DocumentAnalysisReport;

    } catch (error: any) {
      lastError = error;
      console.error(`[AI-FAILED] ${modelName}:`, error.message);
      if (error.message?.includes("429")) throw error;
      continue;
    }
  }

  throw new Error(`L'IA a échoué sur tous les modèles. Dernière erreur: ${lastError?.message}`);
}
