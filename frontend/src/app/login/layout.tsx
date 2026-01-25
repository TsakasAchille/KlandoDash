export default function LoginLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  // Layout sans sidebar pour la page de connexion
  return <>{children}</>;
}
