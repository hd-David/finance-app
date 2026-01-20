import React from 'react';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

const DashboardChart = ({ portfolioData }) => {
  // Mock data for performance visualization
  const performanceData = [
    { time: '09:00', value: 4200 },
    { time: '10:00', value: 4500 },
    { time: '11:00', value: 4300 },
    { time: '12:00', value: 4800 },
    { time: '13:00', value: 5100 },
  ];

  return (
    <div className="row g-4 mt-2">
      {/* 📈 Chart 1: Performance Area Chart */}
      <div className="col-lg-8">
        <div className="metric-panel p-4" style={{ height: '350px' }}>
          <h6 className="text-info mb-4 fw-mono text-uppercase">Equity_Curve_Live</h6>
          <ResponsiveContainer width="100%" height="90%">
            <AreaChart data={performanceData}>
              <defs>
                <linearGradient id="colorVal" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#0dcaf0" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#0dcaf0" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <XAxis dataKey="time" stroke="#666" fontSize={12} tickLine={false} axisLine={false} />
              <YAxis hide domain={['auto', 'auto']} />
              <Tooltip 
                contentStyle={{ backgroundColor: '#000', border: '1px solid #333', color: '#fff' }}
                itemStyle={{ color: '#0dcaf0' }}
              />
              <Area type="monotone" dataKey="value" stroke="#0dcaf0" fillOpacity={1} fill="url(#colorVal)" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* 📊 Chart 2: Asset Allocation (Pie/Donut) */}
      <div className="col-lg-4">
        <div className="metric-panel p-4" style={{ height: '350px' }}>
          <h6 className="text-info mb-4 fw-mono text-uppercase">Allocation_Matrix</h6>
          <ResponsiveContainer width="100%" height="90%">
            <PieChart>
              <Pie
                data={portfolioData} // Data coming from your Alpha Vantage fetch
                innerRadius={60}
                outerRadius={80}
                paddingAngle={5}
                dataKey="value"
              >
                <Cell fill="#0dcaf0" />
                <Cell fill="#198754" />
                <Cell fill="#ffc107" />
                <Cell fill="#741ffc" />
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};
export default DashboardChart;