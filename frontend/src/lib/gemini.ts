import { GoogleGenerativeAI } from "@google/generative-ai";

export async function askKlandoAI(prompt: string, dataContext: any) {
  const apiKey = process.env.GOOGLE_GEMINI_API_KEY;
  
  if (!apiKey) {
    throw new Error("Clé API Gemini manquante dans .env.local");
  }

  // Debug: Vérifier si la clé est bien chargée (sans l'afficher entièrement)
  console.log(`[AI] Utilisation de la clé : ${apiKey.substring(0, 6)}...`);

  const genAI = new GoogleGenerativeAI(apiKey);
  
  const fullPrompt = `
    Tu es l'assistant de Klando (covoiturage au Sénégal). 
    Analyse ces données : ${JSON.stringify(dataContext)}
    
    Question : ${prompt}
    Réponds en français, de manière courte et efficace.
  `;

  // Ordre de test des modèles : 2.0 Flash -> 1.5 Flash -> 1.5 Pro
  const modelsToTry = ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"];
  let lastError = "";

  for (const modelName of modelsToTry) {
    try {
      console.log(`[AI] Tentative avec le modèle : ${modelName}`);
      const model = genAI.getGenerativeModel({ model: modelName });
      
      // Configuration optionnelle pour forcer la stabilité
      const result = await model.generateContent(fullPrompt);
      const text = result.response.text();
      
      if (text) {
        console.log(`[AI] Succès avec ${modelName}`);
        return text;
      }
    } catch (error: any) {
      lastError = error.message;
      console.error(`[AI] Échec du modèle ${modelName}:`, lastError);
      
      // Si c'est une erreur de quota ou de clé, on arrête tout
      if (lastError.includes("API_KEY_INVALID") || lastError.includes("429")) {
        throw new Error(`Problème d'accès API (${modelName}): ${lastError}`);
      }
      continue; 
    }
  }

  throw new Error(`Aucun modèle n'est accessible. (Détail: ${lastError}). Vérifiez vos quotas et l'activation du modèle sur Google AI Studio.`);
}
