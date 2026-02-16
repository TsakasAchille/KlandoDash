"use client";

import { Button } from "@/components/ui/button";
import { FileText, CreditCard, ExternalLink, XCircle } from "lucide-react";
import Image from "next/image";

interface DocumentCardProps {
  title: string;
  url: string | null | undefined;
  type: "license" | "id";
}

export function DocumentCard({ title, url, type }: DocumentCardProps) {
  const Icon = type === "license" ? FileText : CreditCard;

  return (
    <div className="space-y-3">
      <h4 className="text-sm font-bold flex items-center gap-2">
        <Icon className="w-4 h-4 text-klando-gold" />
        {title}
      </h4>
      {url ? (
        <div className="relative group aspect-[4/3] rounded-xl overflow-hidden bg-muted border">
          <Image
            src={url}
            alt={title}
            fill
            className="object-contain"
          />
          <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-2">
            <Button size="sm" variant="secondary" asChild>
              <a href={url} target="_blank" rel="noopener noreferrer">
                <ExternalLink className="w-4 h-4 mr-2" />
                Agrandir
              </a>
            </Button>
          </div>
        </div>
      ) : (
        <div className="aspect-[4/3] rounded-xl bg-muted/50 border border-dashed flex flex-col items-center justify-center text-muted-foreground">
          <XCircle className="w-8 h-8 mb-2 opacity-20" />
          <p className="text-xs italic">Document non fourni</p>
        </div>
      )}
    </div>
  );
}
