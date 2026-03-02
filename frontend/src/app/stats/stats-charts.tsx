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
  CartesianGrid,
  AreaChart,
  Area
} from "recharts";

interface StatsChartsProps {
  type: "typology" | "registration-typology" | "verification" | "orphan-cities" | "revenue-trends";
  data: any;
}

const COLORS = ["#D4AF37", "#800020", "#22C55E", "#3B82F6", "#EF4444"];

export function StatsCharts({ type, data }: StatsChartsProps) {
  const [isMounted, setIsMounted] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => setIsMounted(true), 150);
    return () => clearTimeout(timer);
  }, []);

  if (!isMounted) return <div className="h-full w-full bg-muted/5 animate-pulse rounded-lg" />;

  if (type === "typology" || type === "registration-typology") {
    const chartData = type === "typology" ? [
      { name: "Conducteurs", value: data?.drivers || 0 },
      { name: "Passagers", value: data?.passengers || 0 },
      { name: "Mixtes", value: data?.mixed || 0 },
    ] : [
      { name: "Rôle Conducteur", value: data?.drivers || 0 },
      { name: "Rôle Passager", value: data?.passengers || 0 },
    ];

    const total = chartData.reduce((acc, curr) => acc + curr.value, 0) || 1;

    return (
      <div className="w-full h-full min-h-[250px]">
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
              label={({ percent }) => `${((percent || 0) * 100).toFixed(0)}%`}
              labelLine={false}
            >
              {chartData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={type === "registration-typology" ? (index === 0 ? "#D4AF37" : "#3B82F6") : COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip 
              contentStyle={{ backgroundColor: "#1e293b", border: "none", borderRadius: "8px", color: "#fff" }}
              itemStyle={{ color: "#fff" }}
              formatter={(value: any) => [`${value} (${((Number(value) / total) * 100).toFixed(1)}%)`, 'Nombre']}
            />
            <Legend verticalAlign="bottom" height={36}/>
          </PieChart>
        </ResponsiveContainer>
      </div>
    );
  }

  if (type === "revenue-trends") {
    return (
      <div className="w-full h-full min-h-[300px]">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart
            data={data}
            margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
          >
            <defs>
              <linearGradient id="colorRevenue" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#22C55E" stopOpacity={0.3}/>
                <stop offset="95%" stopColor="#22C55E" stopOpacity={0}/>
              </linearGradient>
            </defs>
            <XAxis 
              dataKey="label" 
              tick={{ fill: "#94a3b8", fontSize: 10 }}
              axisLine={false}
              tickLine={false}
            />
            <YAxis 
              tick={{ fill: "#94a3b8", fontSize: 10 }}
              axisLine={false}
              tickLine={false}
              tickFormatter={(val) => `${val/1000}k`}
            />
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#334155" />
            <Tooltip 
              contentStyle={{ backgroundColor: "#1e293b", border: "none", borderRadius: "12px", color: "#fff" }}
              formatter={(value: any) => [`${Number(value).toLocaleString()} CFA`, 'Revenu']}
            />
            <Area 
              type="monotone" 
              dataKey="revenue" 
              stroke="#22C55E" 
              fillOpacity={1} 
              fill="url(#colorRevenue)" 
              strokeWidth={3}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    );
  }

  if (type === "verification" || type === "orphan-cities") {
    const chartData = (data || []).map((item: any) => ({
      name: item.status || item.city,
      count: item.count || item.demand_count
    }));

    const total = chartData.reduce((acc: number, curr: any) => acc + curr.count, 0) || 1;

    return (
      <div className="w-full h-full min-h-[250px]">
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
              formatter={(value: any) => [`${value} (${((Number(value) / total) * 100).toFixed(1)}%)`, 'Nombre']}
            />
            <Bar 
              dataKey="count" 
              fill={type === "orphan-cities" ? "#EF4444" : "#D4AF37"} 
              radius={[0, 4, 4, 0]}
              barSize={20}
            />
          </BarChart>
        </ResponsiveContainer>
      </div>
    );
  }

  return null;
}
