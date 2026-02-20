"use client";

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
  type: "typology" | "verification";
  data: any;
}

const COLORS = ["#D4AF37", "#800020", "#22C55E", "#3B82F6", "#EF4444"];

export function StatsCharts({ type, data }: StatsChartsProps) {
  if (type === "typology") {
    const chartData = [
      { name: "Conducteurs", value: data?.drivers || 0 },
      { name: "Passagers", value: data?.passengers || 0 },
      { name: "Mixtes", value: data?.mixed || 0 },
    ];

    return (
      <ResponsiveContainer width="100%" height="100%">
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

  if (type === "verification") {
    // data is { status: string; count: number }[]
    const chartData = data.map((item: any) => ({
      name: item.status,
      count: item.count
    }));

    return (
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          layout="vertical"
          data={chartData}
          margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#334155" />
          <XAxis type="number" hide />
          <YAxis 
            dataKey="name" 
            type="category" 
            tick={{ fill: "#94a3b8", fontSize: 10, fontWeight: "bold" }}
            width={80}
          />
          <Tooltip 
            cursor={{ fill: "rgba(255,255,255,0.05)" }}
            contentStyle={{ backgroundColor: "#1e293b", border: "none", borderRadius: "8px", color: "#fff" }}
          />
          <Bar 
            dataKey="count" 
            fill="#D4AF37" 
            radius={[0, 4, 4, 0]}
            barSize={20}
          />
        </BarChart>
      </ResponsiveContainer>
    );
  }

  return null;
}
