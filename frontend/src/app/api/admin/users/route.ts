import { auth } from "@/lib/auth";
import { createClient } from "@supabase/supabase-js";
import { NextResponse } from "next/server";

// Supabase admin client
const supabaseAdmin = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_ROLE_KEY!
);

// Vérifie que l'utilisateur est admin
async function isAdmin() {
  const session = await auth();
  return session?.user?.role === "admin";
}

// POST - Ajouter un utilisateur
export async function POST(request: Request) {
  if (!(await isAdmin())) {
    return NextResponse.json({ message: "Non autorisé" }, { status: 403 });
  }

  const session = await auth();
  const { email, role } = await request.json();

  if (!email || !role) {
    return NextResponse.json(
      { message: "Email et rôle requis" },
      { status: 400 }
    );
  }

  // Vérifier si l'utilisateur existe déjà
  const { data: existing } = await supabaseAdmin
    .from("dash_authorized_users")
    .select("email")
    .eq("email", email)
    .single();

  if (existing) {
    return NextResponse.json(
      { message: "Cet utilisateur existe déjà" },
      { status: 409 }
    );
  }

  const { data, error } = await supabaseAdmin
    .from("dash_authorized_users")
    .insert({
      email,
      role,
      active: true,
      added_by: session?.user?.email,
    })
    .select()
    .single();

  if (error) {
    console.error("Erreur POST:", error);
    return NextResponse.json(
      { message: "Erreur lors de l'ajout" },
      { status: 500 }
    );
  }

  return NextResponse.json({ user: data });
}

// PATCH - Modifier rôle ou statut
export async function PATCH(request: Request) {
  if (!(await isAdmin())) {
    return NextResponse.json({ message: "Non autorisé" }, { status: 403 });
  }

  const { email, action, role, active } = await request.json();

  if (!email || !action) {
    return NextResponse.json(
      { message: "Email et action requis" },
      { status: 400 }
    );
  }

  let updateData: { role?: string; active?: boolean } = {};

  if (action === "role" && role) {
    updateData.role = role;
  } else if (action === "active" && typeof active === "boolean") {
    updateData.active = active;
  } else {
    return NextResponse.json({ message: "Action invalide" }, { status: 400 });
  }

  const { error } = await supabaseAdmin
    .from("dash_authorized_users")
    .update(updateData)
    .eq("email", email);

  if (error) {
    console.error("Erreur PATCH:", error);
    return NextResponse.json(
      { message: "Erreur lors de la modification" },
      { status: 500 }
    );
  }

  return NextResponse.json({ success: true });
}

// DELETE - Supprimer un utilisateur
export async function DELETE(request: Request) {
  if (!(await isAdmin())) {
    return NextResponse.json({ message: "Non autorisé" }, { status: 403 });
  }

  const { email } = await request.json();

  if (!email) {
    return NextResponse.json({ message: "Email requis" }, { status: 400 });
  }

  const { error } = await supabaseAdmin
    .from("dash_authorized_users")
    .delete()
    .eq("email", email);

  if (error) {
    console.error("Erreur DELETE:", error);
    return NextResponse.json(
      { message: "Erreur lors de la suppression" },
      { status: 500 }
    );
  }

  return NextResponse.json({ success: true });
}
