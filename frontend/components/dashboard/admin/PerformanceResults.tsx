import { performanceRows } from "@/lib/adminMockApi";

export default function PerformanceResults() {
  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <h3 className="mb-4 text-xl font-bold text-slate-900">
        Performance Results
      </h3>
      <div className="overflow-hidden rounded-xl border border-slate-200">
        <table className="min-w-full bg-white text-left text-sm">
          <thead className="bg-slate-50 text-slate-600">
            <tr>
              <th className="px-4 py-3 font-semibold">Metric</th>
              <th className="px-4 py-3 font-semibold">Value</th>
              <th className="px-4 py-3 font-semibold">Trend</th>
            </tr>
          </thead>
          <tbody>
            {performanceRows.map((row) => (
              <tr key={row.id} className="border-t border-slate-200">
                <td className="px-4 py-3 text-slate-800">{row.metric}</td>
                <td className="px-4 py-3 font-semibold text-slate-900">
                  {row.value}
                </td>
                <td className="px-4 py-3 text-emerald-600">{row.trend}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
