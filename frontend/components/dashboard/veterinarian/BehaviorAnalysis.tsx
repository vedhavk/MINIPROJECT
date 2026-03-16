"use client";

import { useEffect, useState } from "react";
import {
  type BehaviorMetric,
  getBehaviorMetrics,
} from "@/lib/veterinarianMockApi";

const summaryCards = [
  {
    title: "Social Behavior",
    value: "Normal",
    helper: "Good flock interaction",
    color: "text-blue-600",
  },
  {
    title: "Feeding Pattern",
    value: "Healthy",
    helper: "Regular eating habits",
    color: "text-green-600",
  },
  {
    title: "Activity Level",
    value: "Moderate",
    helper: "Within normal range",
    color: "text-orange-600",
  },
];

export default function BehaviorAnalysis() {
  const [behaviorMetrics, setBehaviorMetrics] = useState<BehaviorMetric[]>([]);

  useEffect(() => {
    async function loadMetrics() {
      const metrics = await getBehaviorMetrics();
      setBehaviorMetrics(metrics);
    }

    loadMetrics();
  }, []);

  const maxDuration = Math.max(
    ...behaviorMetrics.map((metric) => metric.duration),
    1,
  );

  return (
    <div className="space-y-6">
      <section className="rounded-2xl bg-white p-6 shadow-sm">
        <h3 className="mb-6 text-xl font-bold text-slate-900">
          Daily Behavior Patterns
        </h3>
        <div className="relative h-72">
          <div className="absolute inset-0 grid grid-cols-5 gap-6 px-6 pt-4">
            {behaviorMetrics.map((metric) => {
              const height = (metric.duration / maxDuration) * 100;

              return (
                <div
                  key={metric.label}
                  className="flex flex-col items-center justify-end gap-3"
                >
                  <div className="relative flex h-full w-full items-end justify-center rounded-xl bg-slate-50 px-3 pt-4">
                    <div
                      className="group relative w-full rounded-xl bg-blue-500 transition-colors hover:bg-blue-600"
                      style={{ height: `${height}%` }}
                    >
                      <div className="absolute -top-12 left-1/2 hidden -translate-x-1/2 rounded-lg border bg-white px-3 py-2 text-xs font-medium text-slate-700 shadow-sm group-hover:block">
                        {metric.duration} minutes
                      </div>
                    </div>
                  </div>
                  <div className="text-center">
                    <p className="text-base font-medium text-slate-600">
                      {metric.label}
                    </p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
        <div className="mt-3 flex justify-center gap-2 text-sm text-blue-600">
          <span className="h-4 w-4 rounded bg-blue-500" />
          duration
        </div>
      </section>

      <div className="grid gap-4 lg:grid-cols-3">
        {summaryCards.map((card) => (
          <div key={card.title} className="rounded-2xl bg-white p-6 shadow-sm">
            <h4 className="text-2xl font-bold text-slate-900">{card.title}</h4>
            <p className={`mt-4 text-5xl font-bold ${card.color}`}>
              {card.value}
            </p>
            <p className="mt-2 text-lg text-slate-500">{card.helper}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
