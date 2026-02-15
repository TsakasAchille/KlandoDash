import { GoogleGenerativeAI } from "@google/generative-ai";

const genAI = new GoogleGenerativeAI(process.env.GOOGLE_GEMINI_API_KEY || "");

export async function askKlandoAI(prompt: string, dataContext: any) {
  if (!process.env.GOOGLE_GEMINI_API_KEY) {
    throw new Error("Clé API Gemini manquante. Ajoutez GOOGLE_GEMINI_API_KEY à votre .env.local");
  }

  const model = genAI.getGenerativeModel({ model: "gemini-1.5-flash" });
  
  const systemInstruction = `
    Tu es l'assistant intelligent du Dashboard Klando, un service de covoiturage au Sénégal.
    Ta mission est d'aider les administrateurs à analyser les données et à prendre des décisions.
    
    CONSIGNES :
    - Sois précis, pro et utilise un ton amical mais efficace.
    - Utilise le contexte de données fourni pour répondre aux questions.
    - Si tu ne connais pas la réponse, dis-le simplement.
    - Les prix sont en XOF (Franc CFA).
    - Les villes principales sont Dakar, Thies, Saint-Louis, Mbour, Ziguinchor, etc.
  `;

  const contextString = JSON.stringify(dataContext);
  
  const fullPrompt = `
    SYSTÈME: ${systemInstruction}
    CONTEXTE DES DONNÉES ACTUELLES: ${contextString}
    
    QUESTION DE L'ADMINISTRATEUR: ${prompt}
  `;

  try {
    const result = await model.generateContent(fullPrompt);
    const response = await result.response;
    return response.text();
  } catch (error) {
    console.error("Gemini API Error:", error);
    throw new Error("Erreur lors de la communication avec l'IA.");
  }
}
