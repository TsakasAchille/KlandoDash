import { UserPlus, ArrowRight } from "lucide-react";
import Link from "next/link";
import Image from "next/image";
import { UserListItem } from "@/types/user";
import { formatDate } from "@/lib/utils";

interface RecentUsersSectionProps {
  users: UserListItem[];
}

export function RecentUsersSection({ users }: RecentUsersSectionProps) {
  return (
    <div className="space-y-6 pt-4">
      <h2 className="text-lg font-black flex items-center gap-2 uppercase tracking-widest">
        <UserPlus className="w-5 h-5 text-purple-500" />
        Nouveaux Membres
      </h2>
      <div className="bg-card rounded-3xl border border-border/40 overflow-hidden shadow-sm">
        <div className="divide-y divide-border/20">
          {users.map((user) => (
            <Link key={user.uid} href={`/users?selected=${user.uid}`} className="block hover:bg-secondary/20 transition-all duration-300 group">
              <div className="flex items-center justify-between p-5 px-8">
                <div className="flex items-center gap-6">
                  <div className="relative">
                    <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-secondary to-card overflow-hidden flex-shrink-0 flex items-center justify-center border border-border/50 group-hover:border-klando-gold/50 transition-colors shadow-inner">
                      {user.photo_url ? (
                        <Image src={user.photo_url} alt="" width={48} height={48} className="w-full h-full object-cover" />
                      ) : (
                        <span className="text-lg font-black text-klando-gold">{(user.display_name || '?').charAt(0)}</span>
                      )}
                    </div>
                    <div className="absolute -bottom-1 -right-1 w-4 h-4 bg-green-500 border-2 border-card rounded-full" />
                  </div>
                  <div>
                    <p className="font-black text-sm uppercase tracking-tight group-hover:text-klando-gold transition-colors">{user.display_name || 'Sans nom'}</p>
                    <p className="text-[11px] text-muted-foreground mt-1 font-medium">{user.email}</p>
                  </div>
                </div>
                
                <div className="hidden md:flex items-center gap-12">
                  <div className="text-right space-y-1">
                    <p className="text-[10px] font-black uppercase tracking-widest text-muted-foreground/60">Rôle</p>
                    <span className="text-[10px] font-black uppercase bg-secondary px-3 py-1 rounded-lg border border-border/50">
                      {user.role}
                    </span>
                  </div>
                  <div className="text-right space-y-1">
                    <p className="text-[10px] font-black uppercase tracking-widest text-muted-foreground/60">Inscription</p>
                    <p className="text-[11px] font-bold">{user.created_at ? formatDate(user.created_at) : '-'}</p>
                  </div>
                  <div className="w-10 h-10 rounded-full bg-secondary/50 flex items-center justify-center group-hover:bg-klando-gold group-hover:text-white transition-all">
                    <ArrowRight className="w-4 h-4" />
                  </div>
                </div>
              </div>
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
}
