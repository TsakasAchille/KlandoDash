"use client";

import Link from "next/link";
import dynamic from "next/dynamic";
import { TripDetail } from "@/types/trip";
import { formatDate, formatDistance, formatPrice, cn } from "@/lib/utils";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { 
  Banknote, Car, Leaf, ExternalLink, Map as MapIcon, ShieldCheck, 
  Star, CheckCircle2, User, Users, Calendar, Clock, 
  MapPin, ArrowRight, Wallet, TrendingUp, ShieldAlert,
  Info, ChevronRight, Fuel, Gauge, Play, XCircle, Mail
} from "lucide-react";
import Image from "next/image";

// Import dynamique pour éviter les erreurs SSR avec Leaflet
const TripRouteMap = dynamic(
  () => import("./trip-route-map").then((mod) => mod.TripRouteMap),
  {
    ssr: false,
    loading: () => (
      <div className="w-full h-[600px] rounded-[2.5rem] bg-slate-100 flex items-center justify-center border-2 border-dashed border-slate-200">
        <div className="flex flex-col items-center gap-3">
            <div className="w-10 h-10 border-4 border-klando-gold border-t-transparent rounded-full animate-spin" />
            <span className="text-slate-400 text-[10px] font-black uppercase tracking-[0.2em] animate-pulse">Initialisation de la carte...</span>
        </div>
      </div>
    ),
  }
);

interface TripDetailsProps {
  trip: TripDetail;
}

export function TripDetails({ trip }: TripDetailsProps) {
  const co2Saved = ((trip.distance || 0) * 0.12 * (trip.passengers?.length || 0)).toFixed(1);
  const klandoMargin = (trip.total_paid_amount || 0) - (trip.driver_price || 0);
  const totalPassengers = trip.passengers?.length || 0;
  const occupancyRate = Math.round((totalPassengers / (trip.seats_published || 1)) * 100);

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-8 duration-1000 pb-20">
      
      {/* 1. HEADER HERO : Adouci */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 px-4">
        <div className="space-y-2">
            <div className="flex items-center gap-3">
                <div className="px-3 py-1 rounded-full bg-slate-800 text-klando-gold text-[9px] font-black uppercase tracking-widest border border-white/5 shadow-lg">
                    ID : {trip.trip_id.substring(0, 12)}
                </div>
                <BadgeStatus status={trip.status || "UNKNOWN"} />
            </div>
            <h1 className="text-2xl md:text-3xl font-black text-slate-900 tracking-tighter uppercase leading-none">
                {trip.departure_name?.split(',')[0]} <span className="text-klando-gold">→</span> {trip.destination_name?.split(',')[0]}
            </h1>
            <p className="text-[11px] font-bold text-slate-400 uppercase tracking-widest flex items-center gap-2">
                <Calendar className="w-3.5 h-3.5 text-klando-gold/60" />
                Départ le {formatDate(trip.departure_schedule || "")}
            </p>
        </div>

        <div className="flex items-center gap-4">
            <div className="text-right hidden sm:block">
                <p className="text-[9px] font-black text-slate-400 uppercase tracking-widest mb-1">Éco-Performance</p>
                <div className="flex items-center justify-end gap-2 text-green-600/80 font-black">
                    <Leaf className="w-3.5 h-3.5" />
                    <span className="text-sm">{co2Saved} kg CO₂</span>
                </div>
            </div>
            <div className="w-12 h-12 rounded-2xl bg-klando-gold flex items-center justify-center shadow-xl shadow-klando-gold/10">
                <TrendingUp className="w-6 h-6 text-klando-dark" />
            </div>
        </div>
      </div>

      {/* 2. SECTION CARTE (Overlay Anthracite adouci) */}
      <div className="grid grid-cols-1 gap-8">
        <div className="rounded-[3rem] overflow-hidden border-8 border-white shadow-xl bg-white relative group min-h-[600px]">
            {trip.polyline ? (
                <TripRouteMap
                    polylineString={trip.polyline}
                    departureName={trip.departure_name || ""}
                    destinationName={trip.destination_name || ""}
                />
            ) : (
                <div className="w-full h-[600px] bg-slate-50 flex flex-col items-center justify-center border-2 border-dashed border-slate-200 rounded-[2.5rem]">
                    <MapPin className="w-16 h-16 text-slate-200 mb-4 animate-bounce" />
                    <p className="text-sm font-black text-slate-400 uppercase tracking-[0.3em]">Tracé GPS non disponible</p>
                </div>
            )}
            
            {/* Overlay Anthracite Soft (Slate 800) */}
            <div className="absolute bottom-8 left-8 right-8 z-[1000]">
                <div className="bg-slate-800/90 backdrop-blur-xl p-7 rounded-[2.5rem] border border-white/10 shadow-2xl flex flex-col lg:flex-row items-center justify-between gap-8">
                    <div className="flex items-center gap-10 flex-1 w-full lg:w-auto">
                        <div className="flex-1 min-w-0">
                            <p className="text-[8px] font-black text-klando-gold/80 uppercase tracking-[0.2em] mb-2">Origine</p>
                            <p className="text-white font-black text-base uppercase leading-tight truncate">{trip.departure_name}</p>
                            <p className="text-slate-400 text-[10px] italic mt-1 truncate">{trip.departure_description}</p>
                        </div>
                        <div className="w-10 h-10 rounded-full bg-white/5 flex items-center justify-center border border-white/10 flex-shrink-0">
                            <ArrowRight className="w-5 h-5 text-klando-gold" />
                        </div>
                        <div className="flex-1 text-right lg:text-left min-w-0">
                            <p className="text-[8px] font-black text-klando-gold/80 uppercase tracking-[0.2em] mb-2">Destination</p>
                            <p className="text-white font-black text-base uppercase leading-tight truncate">{trip.destination_name}</p>
                            <p className="text-slate-400 text-[10px] italic mt-1 truncate">{trip.destination_description}</p>
                        </div>
                    </div>
                    
                    <div className="h-px lg:h-12 w-full lg:w-[1px] bg-white/10" />
                    
                    <div className="flex items-center gap-8 shrink-0">
                        <div className="text-center">
                            <p className="text-[10px] font-black text-white/40 uppercase tracking-widest mb-1">Distance</p>
                            <p className="text-lg font-black text-white tabular-nums">{formatDistance(trip.distance || 0)}</p>
                        </div>
                        <div className="text-center">
                            <p className="text-[10px] font-black text-white/40 uppercase tracking-widest mb-1">Occupation</p>
                            <p className="text-lg font-black text-klando-gold tabular-nums">{occupancyRate}%</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
      </div>

      {/* 3. GRILLE DE DÉTAILS : Anthracite adouci */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
        
        {/* CONDUCTEUR */}
        <Card className="rounded-[3rem] border-none shadow-xl bg-white overflow-hidden flex flex-col">
            <div className="bg-slate-50 p-6 border-b border-slate-100 flex items-center justify-between">
                <h3 className="text-slate-900 font-black uppercase text-[10px] tracking-widest flex items-center gap-2">
                    <ShieldCheck className="w-3.5 h-3.5 text-blue-500" /> Conducteur
                </h3>
                <Link href={`/users?selected=${trip.driver_id}`}>
                    <Button size="icon" variant="ghost" className="w-8 h-8 rounded-xl hover:bg-slate-100 text-slate-400">
                        <User className="w-4 h-4" />
                    </Button>
                </Link>
            </div>
            <CardContent className="p-8 flex-1 flex flex-col justify-center">
                <div className="flex items-center gap-5">
                    <div className="relative">
                        <div className="w-16 h-16 rounded-2xl border-4 border-slate-50 overflow-hidden shadow-md">
                            {trip.driver_photo ? (
                                <Image src={trip.driver_photo} alt="" fill className="object-cover" sizes="64px" />
                            ) : (
                                <div className="w-full h-full bg-slate-100 flex items-center justify-center text-slate-300 font-black text-xl uppercase">
                                    {(trip.driver_name || "C").charAt(0)}
                                </div>
                            )}
                        </div>
                        <div className="absolute -bottom-1 -right-1 bg-klando-gold text-klando-dark px-1.5 py-0.5 rounded text-[8px] font-black border-2 border-white">
                            {trip.driver_rating?.toFixed(1) || "5.0"} ★
                        </div>
                    </div>
                    <div className="min-w-0">
                        <h4 className="text-base font-black text-slate-900 uppercase tracking-tight truncate">{trip.driver_name}</h4>
                        <p className="text-slate-400 font-mono text-[11px] mt-0.5">{trip.driver_phone || "Non renseigné"}</p>
                    </div>
                </div>
            </CardContent>
        </Card>

        {/* FINANCE CARD : Anthracite Soft (Slate 800) */}
        <Card className="rounded-[3rem] border-none shadow-2xl bg-slate-800 text-white p-8 xl:col-span-2 relative overflow-hidden flex flex-col justify-between">
            <div className="absolute top-0 right-0 w-64 h-64 bg-klando-gold/5 blur-[80px] -mr-32 -mt-32 pointer-events-none" />
            
            <div className="flex items-center justify-between relative z-10">
                <div className="flex items-center gap-4">
                    <div className="w-10 h-10 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center">
                        <Wallet className="w-5 h-5 text-klando-gold" />
                    </div>
                    <div>
                        <h3 className="text-base font-black uppercase tracking-tight leading-none text-white">Analyse Financière</h3>
                        <p className="text-white/30 text-[8px] font-black uppercase tracking-widest mt-1">Ref: {trip.trip_id.split('-')[0]}</p>
                    </div>
                </div>
                <div>
                    {trip.has_successful_transaction ? (
                        <span className="text-green-400 text-[9px] font-black uppercase tracking-widest bg-green-400/10 px-3 py-1 rounded-full border border-green-400/20">● PAYÉ</span>
                    ) : (
                        <span className="text-orange-400 text-[9px] font-black uppercase tracking-widest bg-orange-400/10 px-3 py-1 rounded-full border border-orange-400/20">● EN ATTENTE</span>
                    )}
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 relative z-10 my-6">
                <div className="space-y-1">
                    <p className="text-[9px] font-black text-white/30 uppercase tracking-widest">Collecté</p>
                    <p className="text-2xl font-black text-white tracking-tighter tabular-nums">{formatPrice(trip.total_paid_amount || 0)}</p>
                </div>
                <div className="space-y-1">
                    <p className="text-[9px] font-black text-white/30 uppercase tracking-widest">Part Chauffeur</p>
                    <p className="text-2xl font-black text-klando-gold tracking-tighter tabular-nums">{formatPrice(trip.driver_price || 0)}</p>
                </div>
                <div className="bg-white/5 rounded-[2rem] p-5 border border-white/5 shadow-inner">
                    <p className="text-[9px] font-black text-green-400/60 uppercase tracking-widest mb-1">Profit Klando</p>
                    <p className="text-2xl font-black text-green-400 tracking-tighter tabular-nums">+{formatPrice(klandoMargin)}</p>
                </div>
            </div>

            <div className="flex items-center justify-between border-t border-white/5 pt-6 relative z-10">
                <div className="flex items-center gap-2 text-white/30">
                    <Info className="w-3 h-3" />
                    <span className="text-[8px] font-bold uppercase">Inclut les frais de service et assurance</span>
                </div>
                <div className="text-[8px] font-black text-white/10 uppercase tracking-[0.3em]">
                    KLANDO FINANCE CORE
                </div>
            </div>
        </Card>
      </div>

      {/* 4. PASSAGERS : Grille moderne adoucie */}
      <div className="space-y-5 pt-4">
        <h2 className="text-[11px] font-black uppercase tracking-widest text-slate-400 px-4 flex items-center gap-2">
            <Users className="w-3.5 h-3.5" /> Passagers confirmés ({totalPassengers}/{trip.seats_published})
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5 px-2">
            {trip.passengers?.map((p) => (
                <Card key={p.uid} className="rounded-[2rem] border-none shadow-md bg-white hover:shadow-lg transition-all duration-500 border border-slate-100">
                    <div className="p-4 flex items-center gap-4">
                        <div className="relative">
                            <div className="w-10 h-10 rounded-xl overflow-hidden shadow-inner bg-slate-50">
                                {p.photo_url ? (
                                    <Image src={p.photo_url} alt="" fill className="object-cover" sizes="40px" />
                                ) : (
                                    <div className="w-full h-full flex items-center justify-center text-slate-300 text-sm font-black uppercase">
                                        {p.display_name?.charAt(0)}
                                    </div>
                                )}
                            </div>
                            {p.has_paid && (
                                <div className="absolute -top-1 -right-1 bg-green-500 text-white rounded-full p-0.5 border-2 border-white shadow-sm">
                                    <CheckCircle2 className="w-2 h-2" />
                                </div>
                            )}
                        </div>
                        <div className="flex-1 min-w-0">
                            <p className="font-black text-[11px] uppercase text-slate-900 truncate">{p.display_name}</p>
                            <p className={cn(
                                "text-[8px] font-black uppercase mt-0.5",
                                p.has_paid ? "text-green-500" : "text-slate-300"
                            )}>
                                {p.has_paid ? `Payé ${formatPrice(p.amount_paid || 0)}` : 'Non payé'}
                            </p>
                        </div>
                        <Link href={`/users?selected=${p.uid}`}>
                            <Button size="icon" variant="ghost" className="w-7 h-7 hover:bg-slate-50 text-slate-300 hover:text-klando-gold">
                                <ExternalLink className="w-3 h-3" />
                            </Button>
                        </Link>
                    </div>
                </Card>
            ))}
            
            {(!trip.passengers || trip.passengers.length === 0) && (
                <div className="col-span-full py-10 flex flex-col items-center justify-center bg-slate-50/50 rounded-[2rem] border-2 border-dashed border-slate-200 opacity-40">
                    <p className="text-[10px] font-black uppercase tracking-[0.2em] text-slate-400 italic">En attente de réservations</p>
                </div>
            )}
        </div>
      </div>
    </div>
  );
}

function BadgeStatus({ status }: { status: string }) {
    const configs: Record<string, { label: string, color: string, icon: any }> = {
        'ACTIVE': { label: 'EN COURS', color: 'bg-blue-500 text-white shadow-blue-500/10', icon: Play },
        'COMPLETED': { label: 'TERMINÉ', color: 'bg-green-600 text-white shadow-green-500/10', icon: CheckCircle2 },
        'CANCELLED': { label: 'ANNULÉ', color: 'bg-red-600 text-white shadow-red-500/10', icon: XCircle },
        'PENDING': { label: 'EN ATTENTE', color: 'bg-orange-500 text-white shadow-orange-500/10', icon: Clock },
    };
    const config = configs[status] || { label: status, color: 'bg-slate-500 text-white', icon: ShieldAlert };
    const Icon = config.icon;
    return (
        <div className={cn("flex items-center gap-1.5 px-3 py-1 rounded-full font-black uppercase text-[8px] tracking-widest shadow-md", config.color)}>
            <Icon className="w-3 h-3" /> {config.label}
        </div>
    );
}
