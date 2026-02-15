"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { TripListItem } from "@/types/trip";
import { formatDate, formatPrice } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableRow,
} from "@/components/ui/table";
import { ChevronLeft, ChevronRight, ExternalLink, Loader2 } from "lucide-react";

interface UserTripsTableProps {
  userId: string;
}

export function UserTripsTable({ userId }: UserTripsTableProps) {
  const [trips, setTrips] = useState<TripListItem[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const limit = 5;

  useEffect(() => {
    setLoading(true);
    fetch(`/api/users/${userId}/trips?page=${page}&limit=${limit}`)
      .then((res) => res.json())
      .then((data) => {
        setTrips(data.trips || []);
        setTotal(data.total || 0);
        setLoading(false);
      })
      .catch(() => {
        setTrips([]);
        setTotal(0);
        setLoading(false);
      });
  }, [userId, page]);

  useEffect(() => {
    setPage(1);
  }, [userId]);

  const totalPages = Math.ceil(total / limit);

  if (loading) {
    return (
      <div className="p-8 flex justify-center">
        <Loader2 className="h-6 w-6 animate-spin text-klando-gold" />
      </div>
    );
  }

  return (
    <div className="bg-card">
      {trips.length === 0 ? (
        <div className="p-6 text-center">
          <p className="text-muted-foreground text-xs font-medium">Aucun trajet enregistré</p>
        </div>
      ) : (
        <div className="divide-y divide-border/10">
          <Table>
            <TableBody>
              {trips.map((trip) => (
                <TableRow key={trip.trip_id} className="hover:bg-muted/5 border-none">
                  <TableCell className="py-2 px-4">
                    <div className="text-[11px] font-black uppercase tracking-tight">
                      {trip.departure_name}
                      <span className="text-klando-gold mx-1">→</span>
                      {trip.destination_name}
                    </div>
                    <div className="text-[10px] text-muted-foreground font-medium">
                      {trip.departure_schedule ? formatDate(trip.departure_schedule) : "-"} · <span className="text-foreground font-bold">{formatPrice(trip.passenger_price || 0)}</span>
                    </div>
                  </TableCell>
                  <TableCell className="text-right py-2 px-4">
                    <Link href={`/trips?selected=${trip.trip_id}`}>
                      <Button 
                        variant="ghost" 
                        className="h-7 w-7 p-0 hover:bg-klando-gold/10 hover:text-klando-gold transition-colors"
                      >
                        <ExternalLink className="w-3.5 h-3.5" />
                      </Button>
                    </Link>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>

          {totalPages > 1 && (
            <div className="flex items-center justify-between px-4 py-2 bg-muted/5">
              <span className="text-[9px] font-black uppercase tracking-widest text-muted-foreground">
                {page} / {totalPages}
              </span>
              <div className="flex gap-1">
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-6 w-6"
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                  disabled={page === 1}
                >
                  <ChevronLeft className="w-3 h-3" />
                </Button>
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-6 w-6"
                  onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                  disabled={page >= totalPages}
                >
                  <ChevronRight className="w-3 h-3" />
                </Button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
