"use client";

import { useEffect, useState } from "react";
import Image from "next/image";
import { Camera } from "lucide-react";
import { Button } from "@/components/ui/button";

import {
  getFarmDashboardData,
  type FarmDashboardResponse,
} from "@/lib/mockApi";

export default function FarmDashboard() {
  const [dashboardData, setDashboardData] =
    useState<FarmDashboardResponse | null>(null);

  useEffect(() => {
    async function loadDashboardData() {
      try {
        const data = await getFarmDashboardData();
        setDashboardData(data);
      } catch (error) {
        console.error("Failed to load dashboard data:", error);
        setDashboardData(null);
      }
    }

    loadDashboardData();
  }, []);

  return (
    <div className="max-w-6xl">
      {/* Live Camera Feed */}
      <div className="mb-8">
        <h3 className="text-xl font-bold text-slate-800 mb-4 flex items-center gap-2">
          <Camera className="w-6 h-6 text-green-600" />
          Live Camera Feed
        </h3>
        <div className="relative bg-slate-900 rounded-2xl overflow-hidden aspect-video shadow-xl">
          {dashboardData?.cameraFeed.imageUrl ? (
            <Image
              src={dashboardData.cameraFeed.imageUrl}
              alt="Duck farm"
              fill
              className="object-cover opacity-70"
            />
          ) : null}
          <div className="absolute inset-0 flex flex-col items-center justify-center bg-black/30">
            <div className="bg-white/10 backdrop-blur-sm rounded-full p-6 mb-4">
              <Camera className="w-16 h-16 text-white" />
            </div>
            <h4 className="text-white text-2xl font-bold mb-2">
              {dashboardData?.cameraFeed.statusLabel ?? "No camera status"}
            </h4>
            <p className="text-white/80 text-sm mb-6">
              {dashboardData?.cameraFeed.description ?? "No camera description"}
            </p>
            <Button className="bg-green-500 hover:bg-green-600 text-white px-8 py-6 text-lg rounded-xl shadow-lg">
              {dashboardData?.cameraFeed.actionLabel ?? "No action"}
            </Button>
          </div>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {(dashboardData?.stats ?? []).map((stat) => (
          <div
            key={stat.id}
            className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm"
          >
            <p className="text-sm text-slate-600 mb-2">{stat.label}</p>
            <p
              className={`text-3xl font-bold ${stat.valueClassName ?? "text-slate-800"}`}
            >
              {stat.value}
            </p>
            {stat.helper ? (
              <p
                className={`text-xs mt-2 ${stat.helperClassName ?? "text-slate-500"}`}
              >
                {stat.helper}
              </p>
            ) : null}
          </div>
        ))}
      </div>
    </div>
  );
}
