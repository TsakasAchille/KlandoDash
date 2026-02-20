"use client";

import { useState, useEffect } from "react";
import { 
  PieChart, 
  Pie, 
  Cell, 
  ResponsiveContainer, 
  Legend, 
  Tooltip,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid
} from "recharts";

interface StatsChartsProps {
  type: "typology" | "verification" | "orphan-cities";
  data: any;
}

const COLORS = ["#D4AF37", "#800020", "#22C55E", "#3B82F6", "#EF4444"];

export function StatsCharts({ type, data }: StatsChartsProps) {
  const [isMounted, setIsMounted] = useState(false);

  useEffect(() => {
    // Un léger délai permet au layout des onglets de se stabiliser
    const timer = setTimeout(() => setIsMounted(true), 150);
    return () => clearTimeout(timer);
  }, []);

  if (!isMounted) return <div className="h-full w-full bg-muted/5 animate-pulse rounded-lg" />;

  if (type === "typology") {
    const chartData = [
      { name: "Conducteurs", value: data?.drivers || 0 },
      { name: "Passagers", value: data?.passengers || 0 },
      { name: "Mixtes", value: data?.mixed || 0 },
    ];

    return (
      <ResponsiveContainer width="99%" height="100%" minWidth={0} minHeight={0} debounce={50}>
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            innerRadius={60}
            outerRadius={80}
            paddingAngle={5}
            dataKey="value"
          >
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip 
            contentStyle={{ backgroundColor: "#1e293b", border: "none", borderRadius: "8px", color: "#fff" }}
            itemStyle={{ color: "#fff" }}
          />
          <Legend verticalAlign="bottom" height={36}/>
        </PieChart>
      </ResponsiveContainer>
    );
  }

  if (type === "verification" || type === "orphan-cities") {
    const chartData = (data || []).map((item: any) => ({
      name: item.status || item.city,
      count: item.count || item.demand_count
    }));

    return (
      <ResponsiveContainer width="99%" height="100%" minWidth={0} minHeight={0} debounce={50}>
        <BarChart
          layout="vertical"
          data={chartData}
          margin={{ top: 5, right: 30, left: 40, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#334155" />
          <XAxis type="number" hide />
          <YAxis 
            dataKey="name" 
            type="category" 
            tick={{ fill: "#94a3b8", fontSize: 10, fontWeight: "bold" }}
            width={100}
          />
          <Tooltip 
            cursor={{ fill: "rgba(255,255,255,0.05)" }}
            contentStyle={{ backgroundColor: "#1e293b", border: "none", borderRadius: "8px", color: "#fff" }}
          />
          <Bar 
            dataKey="count" 
            fill={type === "orphan-cities" ? "#EF4444" : "#D4AF37"} 
            radius={[0, 4, 4, 0]}
            barSize={20}
          />
        </BarChart>
      </ResponsiveContainer>
    );
  }

  return null;
}
