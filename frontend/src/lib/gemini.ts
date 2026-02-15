import { GoogleGenerativeAI } from "@google/generative-ai";

export async function askKlandoAI(prompt: string, dataContext: any) {
  const apiKey = process.env.GOOGLE_GEMINI_API_KEY;
  
  if (!apiKey) {
    throw new Error("Clé API Gemini manquante dans .env.local");
  }

  const genAI = new GoogleGenerativeAI(apiKey);
  
  const fullPrompt = `
    Tu es l'assistant de Klando (covoiturage au Sénégal). 
    Analyse ces données : ${JSON.stringify(dataContext)}
    
    Question : ${prompt}
    Réponds en français, de manière courte et efficace.
  `;

  // On essaie d'abord le tout dernier modèle 2.0 Flash
  // S'il échoue, on descend vers le 1.5 Flash
  const modelsToTry = ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-pro"];
  let lastError = "";

  for (const modelName of modelsToTry) {
    try {
      console.log(`Essai avec le modèle: ${modelName}`);
      const model = genAI.getGenerativeModel({ model: modelName });
      const result = await model.generateContent(fullPrompt);
      return result.response.text();
    } catch (error: any) {
      lastError = error.message;
      console.warn(`Le modèle ${modelName} a échoué:`, lastError);
      continue; // On tente le suivant
    }
  }

  throw new Error(`Aucun modèle IA n'a pu répondre. (Dernière erreur: ${lastError})`);
}
