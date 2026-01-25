"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { TripListItem } from "@/types/trip";
import { formatDate, formatPrice } from "@/lib/utils";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableRow,
} from "@/components/ui/table";
import { ChevronLeft, ChevronRight, ExternalLink, Car } from "lucide-react";

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

  // Reset page when user changes
  useEffect(() => {
    setPage(1);
  }, [userId]);

  const totalPages = Math.ceil(total / limit);

  if (loading) {
    return (
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-lg flex items-center gap-2">
            <Car className="w-5 h-5 text-klando-gold" />
            Trajets
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="animate-pulse space-y-3">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="h-12 bg-secondary rounded" />
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-lg flex items-center gap-2">
          <Car className="w-5 h-5 text-klando-gold" />
          Trajets ({total})
        </CardTitle>
      </CardHeader>
      <CardContent>
        {trips.length === 0 ? (
          <p className="text-muted-foreground text-sm">Aucun trajet</p>
        ) : (
          <>
            <Table>
              <TableBody>
                {trips.map((trip) => (
                  <TableRow key={trip.trip_id}>
                    <TableCell className="py-2">
                      <div className="text-sm">
                        <span className="font-medium">{trip.departure_name}</span>
                        <span className="text-muted-foreground"> → </span>
                        <span className="font-medium">{trip.destination_name}</span>
                      </div>
                      <div className="text-xs text-muted-foreground">
                        {trip.departure_schedule ? formatDate(trip.departure_schedule) : "-"} · {formatPrice(trip.passenger_price || 0)}
                      </div>
                    </TableCell>
                    <TableCell className="text-right py-2">
                      <Link href={`/trips?selected=${trip.trip_id}`}>
                        <Button 
                          variant="ghost" 
                          className="min-h-[44px] min-w-[44px] sm:min-h-[32px] sm:min-w-[32px] px-3 sm:px-2"
                          size="sm"
                        >
                          <ExternalLink className="w-4 h-4 sm:w-4 sm:h-4" />
                          <span className="hidden sm:inline ml-2">Voir</span>
                        </Button>
                      </Link>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>

            {totalPages > 1 && (
              <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mt-4">
                <Button
                  variant="outline"
                  className="min-h-[44px] min-w-[44px] sm:min-h-[32px] sm:min-w-[32px]"
                  size="sm"
                  onClick={() => setPage((p) => p - 1)}
                  disabled={page === 1}
                >
                  <ChevronLeft className="w-4 h-4" />
                  <span className="hidden sm:inline ml-2">Précédent</span>
                </Button>
                <span className="text-sm text-muted-foreground text-center">
                  {page} / {totalPages}
                </span>
                <Button
                  variant="outline"
                  className="min-h-[44px] min-w-[44px] sm:min-h-[32px] sm:min-w-[32px]"
                  size="sm"
                  onClick={() => setPage((p) => p + 1)}
                  disabled={page >= totalPages}
                >
                  <span className="hidden sm:inline mr-2">Suivant</span>
                  <ChevronRight className="w-4 h-4" />
                </Button>
              </div>
            )}
          </>
        )}
      </CardContent>
    </Card>
  );
}
